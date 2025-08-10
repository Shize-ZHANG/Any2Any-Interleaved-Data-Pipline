#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub图片上传工具
帮助将本地图片上传到GitHub仓库并获取公开链接
"""

import os
import base64
import json
import requests
from typing import List, Optional

class GitHubUploader:
    def __init__(self, token: str, repo_owner: str, repo_name: str, branch: str = "main"):
        """
        初始化GitHub上传器
        
        Args:
            token: GitHub Personal Access Token
            repo_owner: 仓库所有者用户名
            repo_name: 仓库名称
            branch: 分支名称，默认为main
        """
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.branch = branch
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def upload_file(self, local_path: str, remote_path: str, commit_message: str = None) -> Optional[str]:
        """
        上传单个文件到GitHub
        
        Args:
            local_path: 本地文件路径
            remote_path: GitHub仓库中的路径
            commit_message: 提交消息
            
        Returns:
            文件的公开下载链接，失败时返回None
        """
        if not os.path.exists(local_path):
            print(f"❌ 文件不存在: {local_path}")
            return None
        
        # 读取文件内容并编码为base64
        with open(local_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
        
        # 准备API请求数据
        if not commit_message:
            commit_message = f"Upload {os.path.basename(local_path)}"
        
        data = {
            "message": commit_message,
            "content": content,
            "branch": self.branch
        }
        
        # 检查文件是否已存在
        url = f"{self.base_url}/{remote_path}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            # 文件已存在，需要提供SHA值进行更新
            file_info = response.json()
            data["sha"] = file_info["sha"]
            print(f"文件已存在，将更新: {remote_path}")
        
        # 上传文件
        response = requests.put(url, headers=self.headers, json=data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            download_url = result["content"]["download_url"]
            print(f"✅ 上传成功: {local_path} -> {download_url}")
            return download_url
        else:
            print(f"❌ 上传失败: {local_path}")
            print(f"状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    
    def upload_images_batch(self, image_paths: List[str], remote_dir: str = "images") -> List[str]:
        """
        批量上传图片
        
        Args:
            image_paths: 本地图片路径列表
            remote_dir: GitHub仓库中的目录
            
        Returns:
            成功上传的图片公开链接列表
        """
        uploaded_urls = []
        
        for local_path in image_paths:
            if not os.path.exists(local_path):
                print(f"⚠️  跳过不存在的文件: {local_path}")
                continue
            
            # 构建远程路径
            filename = os.path.basename(local_path)
            remote_path = f"{remote_dir}/{filename}"
            
            # 上传文件
            url = self.upload_file(local_path, remote_path)
            if url:
                uploaded_urls.append(url)
        
        return uploaded_urls

def batch_upload_foodie_images(token: str, repo_owner: str, repo_name: str, 
                              images_dir: str = "images") -> dict:
    """
    批量上传FoodieQA数据集中的所有图片
    
    Args:
        token: GitHub Personal Access Token
        repo_owner: 仓库所有者
        repo_name: 仓库名称
        images_dir: 本地图片目录
        
    Returns:
        图片路径到GitHub链接的映射字典
    """
    uploader = GitHubUploader(token, repo_owner, repo_name)
    
    # 获取所有图片文件
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    image_files = []
    
    if os.path.exists(images_dir):
        for filename in os.listdir(images_dir):
            if os.path.splitext(filename.lower())[1] in image_extensions:
                image_files.append(os.path.join(images_dir, filename))
    else:
        print(f"❌ 图片目录不存在: {images_dir}")
        return {}
    
    print(f"找到 {len(image_files)} 个图片文件")
    
    # 批量上传
    url_mapping = {}
    for i, image_path in enumerate(image_files, 1):
        print(f"上传进度: {i}/{len(image_files)}")
        
        filename = os.path.basename(image_path)
        remote_path = f"images/{filename}"
        
        url = uploader.upload_file(image_path, remote_path)
        if url:
            # 使用相对路径作为key，便于在数据集中匹配
            relative_path = f"images/{filename}"
            url_mapping[relative_path] = url
    
    # 保存映射关系
    mapping_file = "image_url_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(url_mapping, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 上传完成！URL映射已保存到: {mapping_file}")
    print(f"成功上传 {len(url_mapping)} 个图片")
    
    return url_mapping

def main():
    """主函数 - 演示如何使用"""
    # 配置参数（请根据实际情况修改）
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # 从环境变量获取
    REPO_OWNER = "YOUR_USERNAME"  # 替换为您的GitHub用户名
    REPO_NAME = "FoodieQA"  # 替换为您的仓库名
    IMAGES_DIR = "images"  # 本地图片目录
    
    if not GITHUB_TOKEN:
        print("❌ 请设置 GITHUB_TOKEN 环境变量")
        print("获取token: https://github.com/settings/tokens")
        return
    
    if REPO_OWNER == "YOUR_USERNAME":
        print("❌ 请在脚本中设置正确的REPO_OWNER和REPO_NAME")
        return
    
    # 批量上传图片
    url_mapping = batch_upload_foodie_images(GITHUB_TOKEN, REPO_OWNER, REPO_NAME, IMAGES_DIR)
    
    if url_mapping:
        print("\n示例映射关系:")
        for i, (local_path, github_url) in enumerate(url_mapping.items()):
            if i < 3:  # 只显示前3个
                print(f"  {local_path} -> {github_url}")
            else:
                print(f"  ... 还有 {len(url_mapping) - 3} 个")
                break

if __name__ == "__main__":
    main()