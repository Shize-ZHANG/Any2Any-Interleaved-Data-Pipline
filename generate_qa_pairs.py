#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FoodieQA 数据集处理脚本
调用 OpenAI API 生成多模态交错问答对
"""

import json
import os
import time
import requests
from typing import List, Dict, Any
from openai import OpenAI

class FoodieQAProcessor:
    def __init__(self, api_key: str, github_base_url: str = ""):
        """
        初始化处理器
        
        Args:
            api_key: OpenAI API密钥
            github_base_url: GitHub图片链接的基础URL
        """
        self.client = OpenAI(api_key=api_key)
        self.github_base_url = github_base_url
        
    def upload_images_to_github(self, image_paths: List[str]) -> List[str]:
        """
        将图片上传到GitHub并获取公开链接
        注意：这个函数需要根据您的GitHub仓库配置进行调整
        
        Args:
            image_paths: 本地图片路径列表
            
        Returns:
            GitHub公开链接列表
        """
        # 这里是示例代码，您需要根据实际情况调整
        # 可以使用GitHub API或者手动上传后提供链接
        github_urls = []
        
        for image_path in image_paths:
            # 提取文件名
            filename = os.path.basename(image_path)
            
            # 构建GitHub链接（示例格式）
            # 实际使用时，您需要先上传图片到GitHub仓库
            github_url = f"{self.github_base_url}/{filename}"
            github_urls.append(github_url)
            
            print(f"处理图片: {image_path} -> {github_url}")
            
        return github_urls
    
    def construct_prompt(self, image_urls: List[str], data_index: int) -> str:
        """
        构建发送给OpenAI的prompt
        
        Args:
            image_urls: GitHub图片链接列表
            data_index: 数据索引
            
        Returns:
            构建好的prompt字符串
        """
        # 构建原始数据部分
        original_data = {
            f"image{i+1}": url for i, url in enumerate(image_urls[:4])  # 最多4张图片
        }
        
        prompt = f"""You are a multimodal expert. Based on the following original data, please construct a data (Question-Answer pair) entry that strictly conforms to the JSON format below.
Please design a multimodal interleaved Question-Answer pair. You can place different pieces of information from the original data into the input or output of the Question-Answer pair.

[Original data]
{json.dumps(original_data, indent=2, ensure_ascii=False)}

[Question-Answer pair JSON template]
This Question-Answer pair must adhere to the following structure in the following JSON template and don't generate additional information.
{{
    "domain": "general_domain",
    "subdomain": "food",
    "id": "{data_index + 1}",
    "input": {{
        "modal": {{
            "image1": "url",
            "image2": "url",
            "image3": "url",
            "image4": "url"
        }},
        "content": "Interleave <image1>, <image2>, <image3>, <image4> tags at the appropriate position in the text and clearly indicate that the answer must include the number of audios in the output to support or illustrate the explanation."
    }},
    "output": {{
        "modal": {{
            "audio1": "text",
            ...
        }},
        "content": "This is the golden annotation answer that the model is expected to generate. Interleave <audio> tags and so on at suitable positions within the text."
    }}
}}

[Construction requirements]
1 You need to design appropriate question-answer pair and clearly indicate in the question which specific modalities other than text are required to be included in the answer. 
2 The content of the input is the entire input fed into the model. The question-answer pair should be open-world QA. 
3 The content of the input is the entire input fed into the model and the content of the output is the golden output of the model. You should design the input content and output content based on the original data.
4 Give the JSON directly, no additional output information.
5 The <> tags should be the components of the text sentence, not just a single word. For example, the <> tags can serve as the subject, object, or other components of the sentence.
6 Please note that the <> tags of the input should not appear in the output.
7 You should design the text of the <audio> and fill the text into the "text" position of the <audio>.

Please respond with only the JSON, no additional text or explanation."""

        return prompt
    
    def call_openai_api(self, prompt: str, max_retries: int = 3) -> str:
        """
        调用OpenAI API
        
        Args:
            prompt: 发送的prompt
            max_retries: 最大重试次数
            
        Returns:
            API返回的响应
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",  # 或者使用 "gpt-3.5-turbo"
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a helpful assistant that generates structured JSON data for multimodal question-answer pairs about food."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7,
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"API调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise e
    
    def process_dataset(self, dataset_path: str, output_path: str, max_items: int = None):
        """
        处理整个数据集
        
        Args:
            dataset_path: 输入数据集路径
            output_path: 输出文件路径
            max_items: 最大处理条目数（用于测试）
        """
        print(f"开始处理数据集: {dataset_path}")
        
        # 读取原始数据集
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        if max_items:
            dataset = dataset[:max_items]
            print(f"限制处理条目数: {max_items}")
        
        results = []
        
        for i, item in enumerate(dataset):
            print(f"处理第 {i+1}/{len(dataset)} 条数据...")
            
            try:
                # 获取图片路径
                if 'images' in item:
                    image_paths = item['images']
                elif 'food_meta' in item and 'food_file' in item['food_meta']:
                    image_paths = [item['food_meta']['food_file']]
                else:
                    print(f"跳过第 {i+1} 条数据：没有找到图片信息")
                    continue
                
                # 上传图片到GitHub并获取链接
                github_urls = self.upload_images_to_github(image_paths)
                
                # 构建prompt
                prompt = self.construct_prompt(github_urls, i)
                
                # 调用OpenAI API
                response = self.call_openai_api(prompt)
                
                # 尝试解析JSON响应
                try:
                    qa_pair = json.loads(response)
                    results.append(qa_pair)
                    print(f"✅ 成功生成第 {i+1} 条问答对")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败 (第 {i+1} 条): {str(e)}")
                    print(f"原始响应: {response}")
                    continue
                
                # 添加延迟以避免API限制
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ 处理第 {i+1} 条数据时出错: {str(e)}")
                continue
        
        # 保存结果
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 处理完成！生成了 {len(results)} 条问答对")
        print(f"结果保存到: {output_path}")

def main():
    """主函数"""
    # 配置参数
    API_KEY = os.getenv('OPENAI_API_KEY')  # 从环境变量获取API密钥
    GITHUB_BASE_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/images"  # 替换为您的GitHub仓库链接
    
    if not API_KEY:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    # 初始化处理器
    processor = FoodieQAProcessor(API_KEY, GITHUB_BASE_URL)
    
    # 处理不同的数据集
    datasets = [
        ("mivqa_tidy.json", "mivqa_qa_pairs.json"),
        ("sivqa_tidy.json", "sivqa_qa_pairs.json"),
        ("textqa_tidy.json", "textqa_qa_pairs.json")
    ]
    
    for input_file, output_file in datasets:
        if os.path.exists(input_file):
            print(f"\n{'='*50}")
            print(f"处理数据集: {input_file}")
            print(f"{'='*50}")
            
            # 测试模式：只处理前5条数据
            processor.process_dataset(input_file, output_file, max_items=5)
        else:
            print(f"⚠️  数据集文件不存在: {input_file}")

if __name__ == "__main__":
    main()