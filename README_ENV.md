# 环境变量配置说明

## 配置API密钥

为了避免在代码中硬编码API密钥，我们使用环境变量来管理敏感信息。

### 1. 创建配置文件

在项目根目录创建 `config.env` 文件：

```bash
# OpenAI API配置
OPENAI_API_KEY=your_actual_api_key_here
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 使用方法

代码会自动从 `config.env` 文件加载环境变量：

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('config.env')

# 获取API密钥
API_KEY = os.getenv('OPENAI_API_KEY')
```

### 4. 安全注意事项

- `config.env` 文件已添加到 `.gitignore`，不会被提交到版本控制
- 不要在代码中硬编码API密钥
- 在生产环境中，建议使用系统环境变量而不是配置文件

### 5. 系统环境变量（可选）

您也可以直接在系统中设置环境变量：

```bash
# macOS/Linux
export OPENAI_API_KEY="your_api_key_here"

# Windows
set OPENAI_API_KEY=your_api_key_here
```

这样就不需要 `config.env` 文件了。 