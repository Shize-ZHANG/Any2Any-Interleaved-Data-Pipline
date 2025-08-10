import json

def extract_images():
    # 读取原始数据
    with open('mivqa_tidy.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取所有images字段
    images_data = []
    for item in data:
        if 'images' in item:
            images_data.append({
                "images": item['images']
            })
    
    # 保存到新文件
    with open('original_data/original_data.json', 'w', encoding='utf-8') as f:
        json.dump(images_data, f, ensure_ascii=False, indent=2)
    
    print(f"成功提取了 {len(images_data)} 个images字段")
    print("数据已保存到 original_data/original_data.json")

if __name__ == "__main__":
    extract_images() 