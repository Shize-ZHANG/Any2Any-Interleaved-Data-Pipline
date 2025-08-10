#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的OpenAI API调用脚本
直接使用您提供的prompt生成问答对
"""

import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv('config.env')

# 从环境变量获取API密钥
API_KEY = os.getenv('OPENAI_API_KEY')

def call_openai_api(prompt: str, image_urls: list) -> str:
    """
    调用OpenAI API，支持多模态输入
    
    Args:
        prompt: 发送的文本prompt
        image_urls: 图片URL列表
        
    Returns:
        API返回的响应
    """
    client = OpenAI(api_key=API_KEY)
    
    try:
        # 构建消息内容，包含文本和图片
        content = [{"type": "text", "text": prompt}]
        
        # 添加图片URL到消息内容中
        for url in image_urls[:4]:  # 最多4张图片
            content.append({
                "type": "image_url", 
                "image_url": {"url": url}
            })
        
        response = client.chat.completions.create(
            model="gpt-4o",  # GPT-4o 模型
            messages=[
                {
                    "role": "system", 
                    "content": "You are a multimodal expert. Generate structured JSON data for multimodal question-answer pairs. Always respond with properly formatted, multi-line JSON that is easy to read."
                },
                {
                    "role": "user", 
                    "content": content
                }
            ],
            max_tokens=5000,
            response_format={"type": "json_object"}  # 强制输出JSON格式
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ API调用失败: {str(e)}")
        return None

def create_prompt(image_urls: list, data_index: int = 1) -> str:
    """
    创建您提供的prompt
    
    Args:
        image_urls: 图片URL列表
        data_index: 数据索引
        
    Returns:
        完整的prompt
    """
    # 构建原始数据
    original_data = {}
    for i, url in enumerate(image_urls[:4]):  # 最多4张图片
        original_data[f"image{i+1}"] = url
    
    prompt = f"""You are a multimodal expert. Based on the following original data, please construct a data (Question-Answer pair) entry that strictly conforms to the JSON format below.
Please design a multimodal interleaved Question-Answer pair. You can place different pieces of information from the original data into the input or output of the Question-Answer pair.

[Original data]
{json.dumps(original_data, indent=2, ensure_ascii=False)}

[Question-Answer pair JSON template]
This Question-Answer pair must adhere to the following structure in the following JSON template and don't generate additional information.
{{
    "domain": "general_domain",
    "subdomain": "food",
    "id": "{data_index}",
    "input": {{
        "modal": {{
            "image1": "url",
            "image2": "url",
            "image3": "url",
            "image4": "url"
        }},
        "content": "Must interleave <image1>, <image2>, <image3>, <image4> tags at the appropriate position in the text and clearly indicate that the answer must include the number of audios in the output to support or illustrate the explanation, which means that the question should clearly indicate that the answer must include the number of audios in the output to support or illustrate the explanation. "
    }},
    "output": {{
        "modal": {{
            "audio1": "text",
            ...
        }},
        "content": "This is the golden annotation answer that the model is expected to generate. Your answer text MUST naturally integrate all <audio> tags at appropriate positions with the format of <audio1>, <audio2>, etc. within the text. IMPORTANT: All audios together should provide comprehensive explanation for ALL images, with each audio potentially focusing on different subsets of images. The content should reference each audio using <audio1>, <audio2>, etc. format to create a cohesive narrative."
    }}
}}

[Construction requirements]
1 You need to design appropriate question-answer pair and clearly indicate in the question which specific modalities other than text are required to be included in the answer.
2 The output content MUST reference all audio tags using <audio1>, <audio2>, etc. format to create a cohesive narrative.
3 The output modal (audio text) MUST reference all image tags using <image1>, <image2>, <image3>, <image4> format to indicate which images each audio explains. 
2 The content of the input is the entire input fed into the model. The question-answer pair should be open-world QA. 
3 The content of the input is the entire input fed into the model and the content of the output is the golden output of the model. You should design the input content and output content based on the original data.
4 The content of the input MUST contain all tags corresponding to the input modality using <image1>, <image2>, <image3>, <image4> format, and the content of the output MUST contain all tags corresponding to the output modality using <audio1>, <audio2>, etc. format.
5 Give the JSON directly, no additional output information.
6 The <> tags should be the components of the text sentence, not just a single word. For example, the <> tags can serve as the subject, object, or other components of the sentence.
7 Please note that the <> tags of the input should not appear in the output.
8 You should design the text of the <audio> and fill the text into the "text" position of the <audio>. Each audio text MUST reference the specific images it explains using <image1>, <image2>, <image3>, <image4> tags.
9 The number of <audio> in the output is 1. Each audio can focus on different images, but all audios together must cover ALL images.
10 IMPORTANT: The output must contain exactly the same number of audios as specified in the input question with the format of <audio1>, <audio2>, etc. Remember: audios collectively explain all images, with each audio potentially focusing on different subsets. 
12 IMPORTANT: The output content cannot contain the <image> tags of images in the output. The output content MUST reference all audio tags using <audio1>, <audio2>, etc. format to create a cohesive narrative that ties together all the audio explanations.
13 IMPORTANT: All audios together MUST cover ALL images (<image1>, <image2>, <image3>, <image4>). Each individual audio can focus on a subset of images, but collectively they must explain all 4 images.

[IMPORTANT CLARIFICATION]
The number of audios (e.g., 2 or 3) indicates how many detailed audio explanations you should provide. Each audio can focus on different images, but ALL audios together must comprehensively cover ALL 4 images. For example:
- If you need 2 audios: Audio1 explains images 1&2, Audio2 explains images 3&4 (covers all 4 images)
- If you need 3 audios: Audio1 explains image 1, Audio2 explains images 2&3, Audio3 explains image 4 (covers all 4 images but the distribution of the images can be random)

[Example of correct understanding]
Question asks about 4 images and requests 2 audios → Answer should describe ALL 4 images across BOTH audios combined, not necessarily each audio covering all images.

[Output Content Requirement]
The output content (golden annotation answer) MUST reference all audio tags using <audio1>, <audio2>, etc. format to create a cohesive narrative that connects all the audio explanations together.

[Output Modal Requirement]
The output modal (audio text) MUST reference all image tags using <image1>, <image2>, <image3>, <image4> format to indicate which specific images each audio explains. This ensures clear mapping between audios and images.

Please respond with only the JSON, no additional text or explanation.


    """

    return prompt

def main():
    """主函数"""
    print("FoodieQA 简单API调用脚本")
    print("=" * 50)
    
    # 检查API密钥
    if not API_KEY:
        print("❌ 请在config.env文件中设置OPENAI_API_KEY环境变量")
        return
    
    # 示例图片URL（请替换为实际的图片链接）
    example_urls = [
    "https://raw.githubusercontent.com/liyanlin06/any2any_data/main/general_area/food/image/img_0001_01.jpg",
    "https://raw.githubusercontent.com/liyanlin06/any2any_data/main/general_area/food/image/img_0001_02.jpeg",
    "https://raw.githubusercontent.com/liyanlin06/any2any_data/main/general_area/food/image/img_0001_03.jpeg",
    "https://raw.githubusercontent.com/liyanlin06/any2any_data/main/general_area/food/image/img_0001_04.jpeg"
    ]
    
    print("示例图片URL:")
    for i, url in enumerate(example_urls, 1):
        print(f"  image{i}: {url}")
    
    # 询问用户是否要使用示例URL或输入自定义URL
    print("\n请选择:")
    print("1. 使用示例URL")
    print("2. 输入自定义图片URL")
    
    choice = input("请输入选择 (1或2): ").strip()
    
    if choice == "2":
        print("\n请输入图片URL (最多4个，按回车结束每个URL):")
        custom_urls = []
        for i in range(4):
            url = input(f"image{i+1} URL (可选): ").strip()
            if url:
                custom_urls.append(url)
            else:
                break
        
        if custom_urls:
            example_urls = custom_urls
        else:
            print("未输入URL，使用示例URL")
    
    # 创建prompt
    print("\n正在创建prompt...")
    prompt = create_prompt(example_urls)
    
    print("\n生成的Prompt:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    
    # 调用API
    print("\n正在调用OpenAI API...")
    response = call_openai_api(prompt, example_urls)
    
    if response:
        print("\n✅ API调用成功!")
        print("\nAPI响应:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # 尝试解析JSON
        try:
            # 清理响应，移除可能的markdown代码块标记
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # 移除 ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # 移除 ```
            cleaned_response = cleaned_response.strip()
            
            qa_pair = json.loads(cleaned_response)
            print("\n✅ JSON解析成功!")
            
            print("\n格式化的问答对:")
            print(json.dumps(qa_pair, ensure_ascii=False, indent=2))
            
            # 保存结果到JSONL文件
            output_file = "generated_qa_pairs.jsonl"
            with open(output_file, "a", encoding="utf-8") as f:
                # 保存格式化的多行JSON，而不是单行
                f.write(json.dumps(qa_pair, ensure_ascii=False, indent=2) + "\n")
            
            print(f"\n✅ 结果已追加保存到: {output_file}")
            print(f"   (JSONL格式：每个JSON对象为多行格式，便于阅读)")
            
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON解析失败: {e}")
            print("原始响应可能包含额外的文本，请检查上面的API响应")
            
            # 保存原始响应
            with open("raw_response.txt", "w", encoding="utf-8") as f:
                f.write(response)
            print("原始响应已保存到: raw_response.txt")
    
    else:
        print("❌ API调用失败")

if __name__ == "__main__":
    main()