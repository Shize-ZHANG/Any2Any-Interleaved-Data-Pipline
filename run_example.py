#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行示例脚本
演示如何使用FoodieQA处理器生成问答对
"""

import os
import json
from generate_qa_pairs import FoodieQAProcessor

def run_single_example():
    """运行单个示例"""
    # 配置API密钥
    API_KEY = os.getenv('OPENAI_API_KEY')
    if not API_KEY:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    # 示例GitHub图片链接（请替换为实际链接）
    github_urls = [
        "https://raw.githubusercontent.com/YOUR_USERNAME/FoodieQA/main/images/14521898_179_image.jpg",
        "https://raw.githubusercontent.com/YOUR_USERNAME/FoodieQA/main/images/14521898_208_IMG_5468.jpeg",
        "https://raw.githubusercontent.com/YOUR_USERNAME/FoodieQA/main/images/14456664_179_IMG_4221.jpeg",
        "https://raw.githubusercontent.com/YOUR_USERNAME/FoodieQA/main/images/14456664_188_57291912-AA46-487E-8EA0-01538BDAD35E.jpeg"
    ]
    
    # 初始化处理器
    processor = FoodieQAProcessor(API_KEY)
    
    # 构建prompt
    prompt = processor.construct_prompt(github_urls, 0)
    
    print("生成的Prompt:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    
    try:
        # 调用API
        print("\n正在调用OpenAI API...")
        response = processor.call_openai_api(prompt)
        
        print("\nAPI响应:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # 尝试解析JSON
        try:
            qa_pair = json.loads(response)
            print("\n✅ JSON解析成功！")
            print("生成的问答对:")
            print(json.dumps(qa_pair, ensure_ascii=False, indent=2))
            
            # 保存示例结果
            with open("example_qa_pair.json", "w", encoding="utf-8") as f:
                json.dump(qa_pair, f, ensure_ascii=False, indent=2)
            print("\n示例结果已保存到: example_qa_pair.json")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            
    except Exception as e:
        print(f"❌ API调用失败: {e}")

def show_prompt_template():
    """显示prompt模板"""
    print("Prompt模板预览:")
    print("=" * 80)
    
    # 示例数据
    example_urls = [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg", 
        "https://example.com/image3.jpg",
        "https://example.com/image4.jpg"
    ]
    
    processor = FoodieQAProcessor("dummy_key")
    prompt = processor.construct_prompt(example_urls, 0)
    print(prompt)
    print("=" * 80)

def main():
    """主函数"""
    print("FoodieQA 问答对生成器示例")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 显示Prompt模板")
        print("2. 运行单个示例（需要OpenAI API密钥）")
        print("3. 退出")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            show_prompt_template()
        elif choice == "2":
            run_single_example()
        elif choice == "3":
            print("再见！")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()