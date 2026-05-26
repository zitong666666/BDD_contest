from __future__ import annotations

import os
import uuid
import shutil
import asyncio
import subprocess
import threading
from typing import Dict, Any, Optional
import sys

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
import csv
import platform
import time
import psutil
import io
import zipfile
import yaml

app = FastAPI(title="YOLOv5 BDD Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
RUNS_DIR = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs')
os.makedirs(RUNS_DIR, exist_ok=True)
STATE_DIR = os.path.join(BASE_DIR, 'state')
os.makedirs(STATE_DIR, exist_ok=True)
JOBS_FILE = os.path.join(STATE_DIR, 'jobs.json')
CONFIG_FILE = os.path.join(STATE_DIR, 'config.json')


# In-memory job registry (simple demo; replace with DB or redis in production)
jobs: Dict[str, Dict[str, Any]] = {}
def _job_public_view(job: Dict[str, Any]) -> Dict[str, Any]:
    view = {k: v for k, v in job.items() if k not in ('process',)}
    return view


def _save_jobs() -> None:
    try:
        serializable = {jid: _job_public_view(j) for jid, j in jobs.items()}
        with open(JOBS_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, ensure_ascii=False)
    except Exception:
        pass


def _load_jobs() -> None:
    try:
        if os.path.isfile(JOBS_FILE):
            with open(JOBS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    jobs.update(data)
                    # running 作业在重启后标记为 unknown
                    for j in jobs.values():
                        if j.get('status') in ('running', 'queued'):
                            j['status'] = 'unknown'
    except Exception:
        pass


_load_jobs()

# Ensure Windows asyncio subprocess works (Selector event loop policy)
if sys.platform.startswith('win'):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass


class TrainPayload(BaseModel):
    model: str
    weights: str
    data: str
    epochs: int
    batch: int
    imgsz: int


async def _run_process(cmd: list[str], cwd: Optional[str] = None, job_id: Optional[str] = None):
    """Run subprocess using subprocess.Popen for Windows compatibility"""
    def run_in_thread():
        try:
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            if job_id:
                jobs[job_id]['status'] = 'running'
                jobs[job_id]['process'] = process
            
            # Read output line by line
            for line in iter(process.stdout.readline, ''):
                if job_id:
                    jobs[job_id].setdefault('logs', []).append(line.rstrip())
            
            process.wait()
            
            if job_id:
                if process.returncode == 0:
                    jobs[job_id]['status'] = 'completed'
                else:
                    jobs[job_id]['status'] = 'failed'
                    jobs[job_id]['error'] = f'Process exited with code {process.returncode}'
                jobs[job_id].pop('process', None)
                    
        except Exception as e:
            if job_id:
                jobs[job_id]['status'] = 'failed'
                jobs[job_id]['error'] = str(e)
                jobs[job_id].pop('process', None)
    
    # Run in thread to avoid blocking
    thread = threading.Thread(target=run_in_thread)
    thread.daemon = True
    thread.start()


@app.post('/api/train/start')
async def start_train(payload: TrainPayload):
    job_id = uuid.uuid4().hex
    jobs[job_id] = {
        'id': job_id,
        'type': 'train',
        'status': 'queued',
        'logs': [],
        'createdAt': int(time.time()),
        'params': payload.model,
    }

    # Map model name to yaml
    model_yaml = os.path.join(WORK_DIR, 'yolov5-6.2', 'models', f"{payload.model}.yaml")
    weights = payload.weights
    data_yaml = payload.data

    cmd = [
        sys.executable, os.path.join(WORK_DIR, 'yolov5-6.2', 'train.py'),
        '--img', str(payload.imgsz),
        '--batch', str(payload.batch),
        '--epochs', str(payload.epochs),
        '--data', data_yaml,
        '--cfg', model_yaml,
        '--weights', weights,
        '--project', os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'train'),
        '--name', f'exp_{job_id[:8]}'
    ]

    asyncio.create_task(_run_process(cmd, cwd=WORK_DIR, job_id=job_id))
    _save_jobs()
    return { 'jobId': job_id }


@app.get('/api/train/status')
async def train_status(jobId: str):
    job = jobs.get(jobId)
    if not job:
        return JSONResponse(status_code=404, content={'detail': 'job not found'})
    # 若训练已丢失进程但 artifacts 存在，尽量给出成功状态
    if job.get('type') == 'train' and job.get('status') in ('unknown', 'queued', 'running'):
        train_dir = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'train')
        guess = f"exp_{jobId[:8]}"
        exp_path = os.path.join(train_dir, guess)
        if os.path.isfile(os.path.join(exp_path, 'results.csv')):
            job['status'] = 'succeeded'
    return _job_public_view(job)


@app.post('/api/detect/image')
async def detect_image(params: str = Form(...), images: list[UploadFile] = File(...)):
    import json
    p = json.loads(params)
    job_id = uuid.uuid4().hex
    jobs[job_id] = { 'id': job_id, 'type': 'detect-image', 'status': 'queued', 'logs': [] }

    temp_dir = os.path.join(WORK_DIR, 'temp', job_id)
    os.makedirs(temp_dir, exist_ok=True)
    input_dir = os.path.join(temp_dir, 'images')
    os.makedirs(input_dir, exist_ok=True)
    for f in images:
        dest = os.path.join(input_dir, f.filename)
        with open(dest, 'wb') as fp:
            shutil.copyfileobj(f.file, fp)

    weights = p.get('weights', os.path.join(WORK_DIR, 'yolov5-6.2', 'weights', 'best.pt'))
    conf = str(p.get('conf', 0.25))
    iou = str(p.get('iou', 0.45))
    imgsz = str(p.get('imgsz', 640))

    out_dir = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'detect', f'exp_{job_id[:8]}')
    cmd = [
        sys.executable, os.path.join(WORK_DIR, 'yolov5-6.2', 'detect.py'),
        '--source', input_dir,
        '--weights', weights,
        '--conf-thres', conf,
        '--iou-thres', iou,
        '--imgsz', imgsz,
        '--save-txt', '--save-conf',
        '--project', os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'detect'),
        '--name', f'exp_{job_id[:8]}'
    ]
    asyncio.create_task(_run_process(cmd, cwd=WORK_DIR, job_id=job_id))
    jobs[job_id]['createdAt'] = int(time.time())
    jobs[job_id]['outputDir'] = out_dir
    _save_jobs()
    return { 'jobId': job_id, 'outputDir': out_dir }


@app.post('/api/detect/video')
async def detect_video(params: str = Form(...), video: UploadFile = File(...)):
    import json
    p = json.loads(params)
    job_id = uuid.uuid4().hex
    jobs[job_id] = { 'id': job_id, 'type': 'detect-video', 'status': 'queued', 'logs': [] }

    temp_dir = os.path.join(WORK_DIR, 'temp', job_id)
    os.makedirs(temp_dir, exist_ok=True)
    video_path = os.path.join(temp_dir, video.filename)
    with open(video_path, 'wb') as fp:
        shutil.copyfileobj(video.file, fp)

    weights = p.get('weights', os.path.join(WORK_DIR, 'yolov5-6.2', 'weights', 'best.pt'))
    conf = str(p.get('conf', 0.25))
    iou = str(p.get('iou', 0.45))
    imgsz = str(p.get('imgsz', 640))
    out_dir = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'detect', f'exp_{job_id[:8]}')

    cmd = [
        sys.executable, os.path.join(WORK_DIR, 'yolov5-6.2', 'detect.py'),
        '--source', video_path,
        '--weights', weights,
        '--conf-thres', conf,
        '--iou-thres', iou,
        '--imgsz', imgsz,
        '--save-txt', '--save-conf',
        '--project', os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'detect'),
        '--name', f'exp_{job_id[:8]}'
    ]
    asyncio.create_task(_run_process(cmd, cwd=WORK_DIR, job_id=job_id))
    jobs[job_id]['createdAt'] = int(time.time())
    jobs[job_id]['outputDir'] = out_dir
    _save_jobs()
    return { 'jobId': job_id, 'outputDir': out_dir }


@app.get('/api/detect/status')
async def detect_status(jobId: str):
    job = jobs.get(jobId)
    if not job:
        return JSONResponse(status_code=404, content={'detail': 'job not found'})
    if job.get('type', '').startswith('detect') and job.get('status') in ('unknown', 'queued', 'running'):
        out_dir = _detect_output_dir_for_job(jobId)
        if out_dir and os.path.isdir(out_dir) and os.listdir(out_dir):
            job['status'] = 'succeeded'
    return _job_public_view(job)


def _detect_output_dir_for_job(job_id: str) -> Optional[str]:
    base = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'detect')
    cand = f'exp_{job_id[:8]}'
    path = os.path.join(base, cand)
    return path if os.path.isdir(path) else None


@app.get('/api/detect/files')
async def detect_files(jobId: str):
    out_dir = _detect_output_dir_for_job(jobId)
    if not out_dir:
        return { 'files': [] }
    names = [f for f in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir, f))]
    return { 'files': names }


@app.get('/api/detect/file')
async def detect_file(jobId: str, name: str):
    out_dir = _detect_output_dir_for_job(jobId)
    if not out_dir:
        return JSONResponse(status_code=404, content={'detail': 'not found'})
    file_path = os.path.join(out_dir, name)
    if not os.path.isfile(file_path):
        return JSONResponse(status_code=404, content={'detail': 'not found'})
    return FileResponse(file_path)


def _read_yolo_txt(txt_path: str):
    # YOLO txt: class cx cy w h [conf]
    boxes = []
    if not os.path.isfile(txt_path):
        return boxes
    with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                cls = int(float(parts[0]))
                cx, cy, w, h = map(float, parts[1:5])
                conf = float(parts[5]) if len(parts) >= 6 else None
                boxes.append({ 'cls': cls, 'cx': cx, 'cy': cy, 'w': w, 'h': h, 'conf': conf })
    return boxes


@app.get('/api/detect/json')
async def detect_json(jobId: str, image: str):
    """Return detection boxes for a specific image output (normalized YOLO format)."""
    out_dir = _detect_output_dir_for_job(jobId)
    if not out_dir:
        return JSONResponse(status_code=404, content={'detail': 'not found'})
    stem, _ = os.path.splitext(image)
    txt = os.path.join(out_dir, 'labels', f'{stem}.txt')
    boxes = _read_yolo_txt(txt)
    return { 'boxes': boxes }


# Webcam detection (server-side capture with detect.py, preview latest frame)
@app.post('/api/detect/webcam/start')
async def detect_webcam_start(params: str = Form("{}")):
    import json
    p = json.loads(params or "{}")
    job_id = uuid.uuid4().hex
    jobs[job_id] = { 'id': job_id, 'type': 'detect-webcam', 'status': 'queued', 'logs': [] }

    weights = p.get('weights', os.path.join(WORK_DIR, 'yolov5-6.2', 'weights', 'best.pt'))
    conf = str(p.get('conf', 0.25))
    iou = str(p.get('iou', 0.45))
    imgsz = str(p.get('imgsz', 640))
    out_dir = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'detect', f'exp_{job_id[:8]}')

    cmd = [
        sys.executable, os.path.join(WORK_DIR, 'yolov5-6.2', 'detect.py'),
        '--source', '0',
        '--weights', weights,
        '--conf-thres', conf,
        '--iou-thres', iou,
        '--imgsz', imgsz,
        '--project', os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'detect'),
        '--name', f'exp_{job_id[:8]}',
        '--save-txt',
        '--save-conf'
    ]
    asyncio.create_task(_run_process(cmd, cwd=WORK_DIR, job_id=job_id))
    jobs[job_id]['outputDir'] = out_dir
    jobs[job_id]['createdAt'] = int(time.time())
    _save_jobs()
    return { 'jobId': job_id }


@app.post('/api/detect/webcam/stop')
async def detect_webcam_stop(jobId: str = Form(...)):
    job = jobs.get(jobId)
    if not job:
        return JSONResponse(status_code=404, content={'detail': 'job not found'})
    process = job.get('process')
    if process:
        try:
            process.terminate()
        except Exception:
            pass
    job['status'] = 'stopped'
    _save_jobs()
    return { 'stopped': True }


@app.get('/api/detect/webcam/preview')
async def detect_webcam_preview(jobId: str):
    out_dir = _detect_output_dir_for_job(jobId)
    if not out_dir:
        return JSONResponse(status_code=404, content={'detail': 'not found'})
    # find latest annotated image
    candidates = [os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not candidates:
        return JSONResponse(status_code=404, content={'detail': 'no frames yet'})
    latest = max(candidates, key=os.path.getmtime)
    return FileResponse(latest)


@app.get('/api/results/list')
async def results_list(kind: str = 'all'):
    items: list[dict[str, Any]] = []
    def collect(base: str, type_label: str):
        if not os.path.isdir(base):
            return
        for name in os.listdir(base):
            path = os.path.join(base, name)
            if not os.path.isdir(path):
                continue
            mtime = os.path.getmtime(path)
            items.append({ 'type': type_label, 'name': name, 'path': path, 'mtime': mtime })
    detect_dir = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'detect')
    train_dir = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'train')
    if kind in ('all', 'detect'):
        collect(detect_dir, 'detect')
    if kind in ('all', 'train'):
        collect(train_dir, 'train')
    items.sort(key=lambda x: x['mtime'], reverse=True)
    for it in items:
        it.pop('path', None)
    return { 'items': items }


@app.get('/api/jobs')
async def jobs_list(limit: int = 20):
    # return recent jobs from memory/state
    arr = list(jobs.values())
    arr.sort(key=lambda j: j.get('createdAt', 0), reverse=True)
    arr = arr[:limit]
    return { 'items': [ _job_public_view(j) for j in arr ] }


@app.get('/api/results/files')
async def results_files(kind: str, name: str):
    base = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', kind, name)
    if not os.path.isdir(base):
        return JSONResponse(status_code=404, content={'detail': 'not found'})
    files = [f for f in os.listdir(base) if os.path.isfile(os.path.join(base, f))]
    return { 'files': files }


@app.get('/api/results/file')
async def results_file(kind: str, name: str, file: str):
    base = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', kind, name)
    target = os.path.join(base, file)
    if not os.path.isfile(target):
        return JSONResponse(status_code=404, content={'detail': 'not found'})
    return FileResponse(target)


@app.get('/api/train/metrics')
async def train_metrics(jobId: str):
    # results.csv is saved under runs/train/exp*/results.csv
    train_dir = os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'train')
    # guess exp name by jobId first
    guess = f'exp_{jobId[:8]}'
    exp_path = os.path.join(train_dir, guess)
    if not os.path.isdir(exp_path):
        # fallback: pick latest
        exps = [os.path.join(train_dir, d) for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))]
        exp_path = max(exps, key=os.path.getmtime) if exps else None
    if not exp_path:
        return { 'rows': [] }
    csv_path = os.path.join(exp_path, 'results.csv')
    if not os.path.isfile(csv_path):
        return { 'rows': [] }
    rows = []
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return { 'rows': rows }


@app.get('/api/detect/zip')
async def detect_zip(jobId: str):
    out_dir = _detect_output_dir_for_job(jobId)
    if not out_dir:
        return JSONResponse(status_code=404, content={'detail': 'not found'})
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name in os.listdir(out_dir):
            path = os.path.join(out_dir, name)
            if os.path.isfile(path):
                zf.write(path, arcname=name)
    buf.seek(0)
    headers = {
        'Content-Disposition': f'attachment; filename="{os.path.basename(out_dir)}.zip"'
    }
    return StreamingResponse(buf, media_type='application/zip', headers=headers)


class StopPayload(BaseModel):
    jobId: str


@app.post('/api/train/stop')
async def train_stop(payload: StopPayload):
    job = jobs.get(payload.jobId)
    if not job:
        return JSONResponse(status_code=404, content={'detail': 'job not found'})
    process = job.get('process')
    if process:
        try:
            process.terminate()
        except Exception:
            pass
    job['status'] = 'stopped'
    return { 'stopped': True }


@app.get('/')
async def root():
    return { 'ok': True }


@app.get('/api/system/stats')
async def system_stats():
    # basic system info for dashboard
    vm = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.1)
    gpus = []
    # Optional: try torch.cuda if installed
    try:
        import torch  # type: ignore
        if torch.cuda.is_available():
            count = torch.cuda.device_count()
            for i in range(count):
                name = torch.cuda.get_device_name(i)
                gpus.append({ 'index': i, 'name': name })
    except Exception:
        pass
    return {
        'time': int(time.time()),
        'platform': platform.platform(),
        'python': sys.version.split(' ')[0],
        'cpuPercent': cpu,
        'memory': { 'total': vm.total, 'available': vm.available, 'percent': vm.percent },
        'gpus': gpus,
        'runs': {
            'train': os.listdir(os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'train')) if os.path.isdir(os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'train')) else [],
            'detect': os.listdir(os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'detect')) if os.path.isdir(os.path.join(WORK_DIR, 'yolov5-6.2', 'runs', 'detect')) else [],
        }
    }


@app.get('/api/system/config')
async def get_config():
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


@app.put('/api/system/config')
async def put_config(payload: Dict[str, Any]):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False)
        return { 'ok': True }
    except Exception as e:
        return JSONResponse(status_code=500, content={'detail': str(e)})


def _load_names_from_yaml(yaml_path: str) -> list[str]:
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            y = yaml.safe_load(f) or {}
            names = y.get('names')
            if isinstance(names, dict):
                # dict index->name
                return [name for _, name in sorted(names.items(), key=lambda kv: int(kv[0]))]
            if isinstance(names, list):
                return [str(n) for n in names]
    except Exception:
        pass
    return []


@app.get('/api/classes')
async def get_classes():
    # try configured data yaml first
    cfg = {}
    try:
        if os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f) or {}
    except Exception:
        pass
    data_yaml = cfg.get('data') or cfg.get('data_yaml')
    names: list[str] = []
    if data_yaml and os.path.isfile(data_yaml):
        names = _load_names_from_yaml(data_yaml)
    if not names:
        # fallback coco.yaml under yolov5
        coco = os.path.join(WORK_DIR, 'yolov5-6.2', 'data', 'coco.yaml')
        if os.path.isfile(coco):
            names = _load_names_from_yaml(coco)
    return { 'names': names }


