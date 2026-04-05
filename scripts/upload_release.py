# -*- coding: utf-8 -*-
import os
import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
REPO_OWNER = "pathseeker05"
REPO_NAME = "chinese-culture-data-converter"
TAG = "v1.0.0"

def create_release():
    if not GITHUB_TOKEN:
        print("请设置 GITHUB_TOKEN 环境变量")
        print("  Windows: $env:GITHUB_TOKEN='your_token'")
        print("  Linux/Mac: export GITHUB_TOKEN='your_token'")
        return
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    body = """中华文化数据库 v1.0.0

## 数据统计

| 类别 | 数量 |
|:-----|------|
| 诗词 | 65,185 |
| 对联 | 744,930 |
| 词语 | 264,434 |
| 成语 | 30,895 |
| 谜语 | 27,517 |
| 汉字 | 16,142 |
| 歇后语 | 14,032 |
| 传统色 | 161 |
| **总计** | **1,163,266** |

## 使用方法

1. 下载 objectbox.zip
2. 解压到项目目录
3. 使用 ObjectBox SDK 访问数据"""
    
    response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases",
        headers=headers,
        json={
            "tag_name": TAG,
            "name": TAG,
            "body": body,
            "draft": False,
            "prerelease": False
        }
    )
    
    if response.status_code == 201:
        release = response.json()
        upload_url = release["upload_url"].replace("{?name,label}", "")
        print(f"Release 创建成功: {release['html_url']}")
        
        zip_path = os.path.join(os.path.dirname(__file__), "..", "output", "objectbox.zip")
        if os.path.exists(zip_path):
            with open(zip_path, "rb") as f:
                upload_response = requests.post(
                    upload_url,
                    headers={
                        "Authorization": f"token {GITHUB_TOKEN}",
                        "Content-Type": "application/zip"
                    },
                    params={"name": "objectbox.zip"},
                    data=f
                )
            if upload_response.status_code == 201:
                print(f"文件上传成功")
            else:
                print(f"文件上传失败: {upload_response.text}")
    else:
        print(f"Release 创建失败: {response.text}")

if __name__ == "__main__":
    create_release()
