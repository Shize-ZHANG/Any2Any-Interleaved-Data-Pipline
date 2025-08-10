# FoodieQA 问答对生成器

这个项目提供了一套完整的工具来处理FoodieQA数据集，调用OpenAI API生成符合特定格式的多模态交错问答对。

## 功能特性

- 📸 **图片上传**: 自动将本地图片上传到GitHub并获取公开链接
- 🤖 **AI生成**: 调用OpenAI API生成高质量的问答对
- 🔄 **批量处理**: 支持批量处理整个数据集
- 📝 **格式规范**: 严格遵循指定的JSON格式要求
- 🛠️ **错误处理**: 完善的错误处理和重试机制

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境配置

### 1. 设置OpenAI API密钥

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 2. 设置GitHub Token（可选，用于自动上传图片）

```bash
export GITHUB_TOKEN="your_github_token_here"
```

获取GitHub Token: https://github.com/settings/tokens

## 使用方法

### 方法一：手动上传图片后使用

1. **手动上传图片到GitHub仓库**
   - 将`images/`目录中的图片上传到您的GitHub仓库
   - 获取图片的公开链接格式：`https://raw.githubusercontent.com/用户名/仓库名/main/images/图片名`

2. **修改配置**
   ```python
   # 在 generate_qa_pairs.py 中修改
   GITHUB_BASE_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/images"
   ```

3. **运行主脚本**
   ```bash
   python generate_qa_pairs.py
   ```

### 方法二：使用自动上传工具

1. **配置GitHub上传器**
   ```python
   # 在 github_uploader.py 中修改
   REPO_OWNER = "YOUR_USERNAME"
   REPO_NAME = "FoodieQA"
   ```

2. **批量上传图片**
   ```bash
   python github_uploader.py
   ```

3. **运行主脚本**
   ```bash
   python generate_qa_pairs.py
   ```

### 方法三：运行示例

```bash
python run_example.py
```

## 文件说明

- `generate_qa_pairs.py` - 主要的问答对生成脚本
- `github_uploader.py` - GitHub图片上传工具
- `run_example.py` - 运行示例和测试脚本
- `requirements.txt` - Python依赖列表
- `mivqa_tidy.json` - 多图像视觉问答数据集
- `sivqa_tidy.json` - 单图像视觉问答数据集  
- `textqa_tidy.json` - 文本问答数据集

## 生成的JSON格式

脚本会生成符合以下格式的问答对：

```json
{
    "domain": "general_domain",
    "subdomain": "food",
    "id": "1",
    "input": {
        "modal": {
            "image1": "https://github.com/...",
            "image2": "https://github.com/...",
            "image3": "https://github.com/...",
            "image4": "https://github.com/..."
        },
        "content": "基于<image1>中的川菜、<image2>中的粤菜、<image3>中的湘菜和<image4>中的鲁菜，请分析这四种菜系的特点并提供3段音频解释来支持你的分析。"
    },
    "output": {
        "modal": {
            "audio1": "川菜以麻辣著称，善用花椒和辣椒调味",
            "audio2": "粤菜注重原汁原味，烹调技法精细多样",
            "audio3": "湘菜口味重，以辣椒调味为主要特色"
        },
        "content": "通过观察这四道菜，我们可以分析出不同菜系的特点。<audio1>川菜以麻辣著称，善用花椒和辣椒调味</audio1>，体现了川菜的麻辣特色。<audio2>粤菜注重原汁原味，烹调技法精细多样</audio2>，展现了粤菜的精致。<audio3>湘菜口味重，以辣椒调味为主要特色</audio3>，突出了湘菜的辣味特点。"
    }
}
```

## 注意事项

1. **API限制**: OpenAI API有调用频率限制，脚本内置了延迟机制
2. **图片链接**: 确保GitHub图片链接是公开可访问的
3. **数据量**: 建议先用少量数据测试，确认效果后再批量处理
4. **成本控制**: 使用GPT-4会产生较高费用，可以先用GPT-3.5-turbo测试

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   ❌ 请设置 OPENAI_API_KEY 环境变量
   ```
   解决：确保正确设置了OpenAI API密钥

2. **图片链接无法访问**
   ```
   ❌ 图片链接无法访问
   ```
   解决：检查GitHub仓库是否为公开，图片链接是否正确

3. **JSON解析失败**
   ```
   ❌ JSON解析失败
   ```
   解决：检查API返回的内容，可能需要调整prompt

## 许可证

MIT License