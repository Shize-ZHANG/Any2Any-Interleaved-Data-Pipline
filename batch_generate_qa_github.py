#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成QA对的脚本 - GitHub图片版本
使用GitHub仓库中的图片URL，处理每个ID的四张图片，生成QA对
"""

import json
import os
import time
import argparse
from pathlib import Path
from simple import call_openai_api, create_prompt

def build_github_image_urls(json_id, image_paths):
    """根据JSON ID和图片路径构建GitHub图片URL"""
    github_base_url = "https://raw.githubusercontent.com/liyanlin06/any2any_data/main/general_area/food/image"
    
    # 构建新的图片URL列表
    github_urls = []
    for i, original_path in enumerate(image_paths):
        # 从原始路径提取文件名，然后构建新的文件名
        # 原始格式：images/14521898_179_image.jpg
        # 新格式：img_{json_id}_{i+1:02d}.jpg
        file_extension = Path(original_path).suffix
        new_filename = f"img_{json_id}_{i+1:02d}{file_extension}"
        github_url = f"{github_base_url}/{new_filename}"
        github_urls.append(github_url)
    
    return github_urls

def batch_generate_qa(start_id=None, count=None, delay=2):
    """批量生成QA对"""
    
    # 检查API密钥
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ 请在config.env文件中设置OPENAI_API_KEY环境变量")
        return
    
    # 读取JSON数据
    try:
        with open('original_data/original_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ 找不到 original_data/original_data.json 文件")
        return
    except json.JSONDecodeError:
        print("❌ original_data.json 文件格式错误")
        return
    
    # 根据参数筛选数据
    if start_id:
        # 找到起始ID的位置
        start_index = None
        for i, item in enumerate(data):
            if item['id'] == start_id:
                start_index = i
                break
        
        if start_index is None:
            print(f"❌ 找不到ID为 {start_id} 的数据条目")
            return
        
        data = data[start_index:]
        print(f"🎯 从ID {start_id} 开始处理")
    
    if count:
        data = data[:count]
        print(f"📊 限制处理数量为 {count} 个")
    
    print(f"📊 开始处理 {len(data)} 个数据条目...")
    
    # 创建输出目录
    output_dir = Path('generated_qa_data')
    output_dir.mkdir(exist_ok=True)
    
    # 输出文件
    output_file = output_dir / 'batch_qa_results.jsonl'
    error_file = output_dir / 'error_log.txt'
    
    success_count = 0
    error_count = 0
    
    # 处理每个数据条目
    for i, item in enumerate(data):
        json_id = item['id']
        images = item['images']
        
        print(f"\n🔄 处理第 {i+1}/{len(data)} 个条目 (ID: {json_id})")
        print(f"   图片数量: {len(images)}")
        
        # 构建GitHub图片URL
        github_image_urls = build_github_image_urls(json_id, images)
        
        print(f"   📷 图片URLs:")
        for j, url in enumerate(github_image_urls):
            print(f"      image{j+1}: {url}")
        
        try:
            # 创建prompt
            prompt = create_prompt(github_image_urls, json_id)
            
            # 调用API
            print(f"   📤 调用OpenAI API...")
            response = call_openai_api(prompt, github_image_urls)
            
            if response:
                # 尝试解析JSON
                try:
                    # 清理响应
                    cleaned_response = response.strip()
                    if cleaned_response.startswith('```json'):
                        cleaned_response = cleaned_response[7:]
                    if cleaned_response.endswith('```'):
                        cleaned_response = cleaned_response[:-3]
                    cleaned_response = cleaned_response.strip()
                    
                    qa_pair = json.loads(cleaned_response)
                    
                    # 添加原始ID信息
                    qa_pair['original_id'] = json_id
                    qa_pair['original_image_paths'] = images
                    qa_pair['github_image_urls'] = github_image_urls
                    
                    # 保存到JSONL文件
                    with open(output_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(qa_pair, ensure_ascii=False, indent=2) + "\n")
                    
                    print(f"   ✅ 成功生成QA对，已保存")
                    success_count += 1
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON解析失败: {e}")
                    # 保存原始响应到错误日志
                    with open(error_file, "a", encoding="utf-8") as f:
                        f.write(f"ID: {json_id}\nError: {e}\nResponse: {response}\n{'='*50}\n")
                    error_count += 1
                    
            else:
                print(f"   ❌ API调用失败")
                error_count += 1
                # 记录错误
                with open(error_file, "a", encoding="utf-8") as f:
                    f.write(f"ID: {json_id}\nError: API调用失败\n{'='*50}\n")
        
        except Exception as e:
            print(f"   ❌ 处理过程中出错: {e}")
            error_count += 1
            # 记录错误
            with open(error_file, "a", encoding="utf-8") as f:
                f.write(f"ID: {json_id}\nError: {e}\n{'='*50}\n")
        
        # 添加延迟以避免API限制
        if i < len(data) - 1:  # 不是最后一个
            print(f"   ⏳ 等待{delay}秒后继续...")
            time.sleep(delay)
    
    # 输出统计信息
    print(f"\n{'='*50}")
    print(f"📊 处理完成!")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {error_count} 个")
    print(f"📁 输出文件: {output_file}")
    if error_count > 0:
        print(f"📝 错误日志: {error_file}")
    print(f"{'='*50}")

def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description='批量生成QA对脚本')
    parser.add_argument('--start-id', type=str, help='起始ID (例如: 0001)')
    parser.add_argument('--count', type=int, help='处理的数量')
    parser.add_argument('--delay', type=int, default=2, help='API调用间隔延迟(秒)，默认2秒')
    
    args = parser.parse_args()
    
    print("🚀 FoodieQA 批量生成QA对脚本")
    print("=" * 50)
    
    if args.start_id:
        print(f"🎯 起始ID: {args.start_id}")
    if args.count:
        print(f"📊 处理数量: {args.count}")
    print(f"⏱️  API延迟: {args.delay}秒")
    print("=" * 50)
    
    # 调用主函数
    batch_generate_qa(
        start_id=args.start_id,
        count=args.count,
        delay=args.delay
    )

if __name__ == "__main__":
    main() 