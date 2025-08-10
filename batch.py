#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成QA对的脚本
自动更换URL中的文件名，批量处理多个ID
"""

import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv('config.env')

# 从环境变量获取API密钥
API_KEY = os.getenv('OPENAI_API_KEY')

def generate_image_urls(data_id: str) -> list:
    """
    根据数据ID生成对应的图片URL列表
    
    Args:
        data_id: 数据ID，如 "0001", "0002" 等
        
    Returns:
        包含4张图片URL的列表
    """
    base_url = "https://raw.githubusercontent.com/liyanlin06/any2any_data/main/general_area/food/image"
    
    # 生成4张图片的URL，文件名格式：img_{data_id}_{序号}.{扩展名}
    image_urls = [
        f"{base_url}/img_{data_id}_01.jpg",
        f"{base_url}/img_{data_id}_02.jpeg", 
        f"{base_url}/img_{data_id}_03.jpeg",
        f"{base_url}/img_{data_id}_04.jpeg"
    ]
    
    return image_urls

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
9 IMPORTANT: The number of <audio> in the output is 1. If the number of <audio> is more than 1, each audio can focus on different images, but all audios together must cover ALL images.
10 IMPORTANT: The output must contain exactly the same number of audios as specified in the input question with the format of <audio1>, <audio2>, etc. Remember: audios collectively explain all images, with each audio potentially focusing on different subsets. 
12 IMPORTANT: The output content MUST not contain the <image> tags of images in the output. The output content MUST reference all audio tags using <audio1>, <audio2>, etc. format to create a cohesive narrative that ties together all the audio explanations.
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

def process_single_id(data_id: str, delay: int = 2) -> bool:
    """
    处理单个ID的QA对生成
    
    Args:
        data_id: 数据ID，如 "0001"
        delay: API调用间隔延迟(秒)
        
    Returns:
        是否成功
    """
    print(f"\n🔄 处理ID: {data_id}")
    
    # 生成图片URL
    image_urls = generate_image_urls(data_id)
    
    print(f"   📷 图片URLs:")
    for i, url in enumerate(image_urls, 1):
        print(f"      image{i}: {url}")
    
    # 创建prompt
    prompt = create_prompt(image_urls, data_id)
    
    # 调用API
    print(f"   📤 调用OpenAI API...")
    response = call_openai_api(prompt, image_urls)
    
    if response:
        try:
            # 清理响应
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            qa_pair = json.loads(cleaned_response)
            
            # 保存到JSONL文件
            output_file = "generated_qa_pairs.jsonl"
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(qa_pair, ensure_ascii=False, indent=2) + "\n")
            
            print(f"   ✅ 成功生成QA对，已保存")
            return True
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON解析失败: {e}")
            # 保存原始响应到错误日志
            with open("error_log.txt", "a", encoding="utf-8") as f:
                f.write(f"ID: {data_id}\nError: {e}\nResponse: {response}\n{'='*50}\n")
            return False
            
    else:
        print(f"   ❌ API调用失败")
        # 记录错误
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"ID: {data_id}\nError: API调用失败\n{'='*50}\n")
        return False

def batch_process(start_id: int = 1, end_id: int = 10, delay: int = 2):
    """
    批量处理多个ID
    
    Args:
        start_id: 起始ID
        end_id: 结束ID
        delay: API调用间隔延迟(秒)
    """
    print("🚀 FoodieQA 批量生成QA对脚本")
    print("=" * 50)
    print(f"🎯 处理范围: ID {start_id:04d} 到 {end_id:04d}")
    print(f"⏱️  API延迟: {delay}秒")
    print("=" * 50)
    
    # 检查API密钥
    if not API_KEY:
        print("❌ 请在config.env文件中设置OPENAI_API_KEY环境变量")
        return
    
    # 创建输出目录
    output_dir = "generated_qa_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    success_count = 0
    error_count = 0
    
    # 批量处理
    for i in range(start_id, end_id + 1):
        data_id = f"{i:04d}"  # 格式化为4位数字，如 "0001"
        
        success = process_single_id(data_id, delay)
        if success:
            success_count += 1
        else:
            error_count += 1
        
        # 添加延迟以避免API限制（除了最后一个）
        if i < end_id:
            print(f"   ⏳ 等待{delay}秒后继续...")
            time.sleep(delay)
    
    # 输出统计信息
    print(f"\n{'='*50}")
    print(f"📊 处理完成!")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {error_count} 个")
    print(f"📁 输出文件: generated_qa_pairs.jsonl")
    if error_count > 0:
        print(f"📝 错误日志: error_log.txt")
    print(f"{'='*50}")

def main():
    """主函数"""
    print("FoodieQA 批量生成QA对脚本")
    print("=" * 50)
    print("请选择模式:")
    print("1. 单次处理 (测试用)")
    print("2. 批量处理")
    
    choice = input("请输入选择 (1或2): ").strip()
    
    if choice == "1":
        # 单次处理模式
        print("\n🎯 单次处理模式")
        data_id = input("请输入要处理的ID (例如: 0001): ").strip()
        if not data_id:
            data_id = "0001"
        
        process_single_id(data_id)
        
    elif choice == "2":
        # 批量处理模式
        print("\n📊 批量处理模式")
        start_id = input("请输入起始ID (默认: 1): ").strip()
        end_id = input("请输入结束ID (默认: 10): ").strip()
        delay = input("请输入API延迟秒数 (默认: 2): ").strip()
        
        # 设置默认值
        start_id = int(start_id) if start_id.isdigit() else 1
        end_id = int(end_id) if end_id.isdigit() else 10
        delay = int(delay) if delay.isdigit() else 2
        
        batch_process(start_id, end_id, delay)
        
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()