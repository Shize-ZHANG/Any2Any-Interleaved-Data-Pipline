import json
import os
import shutil
from pathlib import Path

def copy_and_rename_images():
    # 读取JSON数据
    with open('original_data/original_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建目标目录
    target_dir = Path('original_data/original_data_images')
    target_dir.mkdir(exist_ok=True)
    
    success_count = 0
    error_count = 0
    
    print(f"开始处理 {len(data)} 个JSON条目...")
    
    for item in data:
        json_id = item['id']
        images = item['images']
        
        for i, image_path in enumerate(images):
            # 构建源文件路径
            source_path = Path(image_path)
            
            # 构建目标文件名：img_0234_02 格式
            target_filename = f"img_{json_id}_{i+1:02d}{source_path.suffix}"
            target_path = target_dir / target_filename
            
            try:
                # 检查源文件是否存在
                if source_path.exists():
                    # 复制文件
                    shutil.copy2(source_path, target_path)
                    success_count += 1
                    print(f"✓ 复制成功: {image_path} -> {target_filename}")
                else:
                    print(f"✗ 源文件不存在: {image_path}")
                    error_count += 1
                    
            except Exception as e:
                print(f"✗ 复制失败: {image_path} -> {target_filename}, 错误: {e}")
                error_count += 1
    
    print(f"\n=== 处理完成 ===")
    print(f"成功复制: {success_count} 张图片")
    print(f"失败: {error_count} 张图片")
    print(f"目标目录: {target_dir.absolute()}")

if __name__ == "__main__":
    copy_and_rename_images() 