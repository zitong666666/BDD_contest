#!/usr/bin/env python3
import requests
import json
import os

def test_backend():
    """测试后端API功能"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== 测试后端API ===")
    
    # 1. 测试系统状态
    try:
        response = requests.get(f"{base_url}/api/system/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 系统状态API正常: CPU {stats.get('cpuPercent', 'N/A')}%, 内存 {stats.get('memory', {}).get('percent', 'N/A')}%")
        else:
            print(f"❌ 系统状态API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 系统状态API错误: {e}")
        return False
    
    # 2. 测试图片检测
    try:
        image_path = "yolov5-6.2/data/images/bus.jpg"
        if not os.path.exists(image_path):
            print(f"❌ 测试图片不存在: {image_path}")
            return False
            
        with open(image_path, 'rb') as f:
            files = {'images': f}
            data = {'params': json.dumps({"conf": 0.25, "iou": 0.45, "imgsz": 640})}
            response = requests.post(f"{base_url}/api/detect/image", files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('jobId')
            print(f"✅ 图片检测API正常: Job ID {job_id}")
            
            # 等待检测完成
            import time
            for i in range(10):
                time.sleep(2)
                status_response = requests.get(f"{base_url}/api/detect/status", params={'jobId': job_id})
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    print(f"   检测状态: {status}")
                    if status in ['completed', 'failed']:
                        break
            
            return True
        else:
            print(f"❌ 图片检测API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 图片检测API错误: {e}")
        return False

def test_frontend():
    """测试前端访问"""
    print("\n=== 测试前端访问 ===")
    try:
        response = requests.get("http://127.0.0.1:5173", timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务正常")
            return True
        else:
            print(f"❌ 前端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端服务错误: {e}")
        return False

if __name__ == "__main__":
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print(f"\n=== 测试结果 ===")
    print(f"后端: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"前端: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 所有服务正常运行！")
        print("请在浏览器中访问: http://localhost:5173")
    else:
        print("\n⚠️ 存在问题，请检查服务状态")
