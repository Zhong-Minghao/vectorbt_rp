# GitHub 上传指南

## 🚀 快速上传到 GitHub

### 方法 1: 使用 GitHub CLI（推荐）

```bash
# 1. 安装 GitHub CLI（如果还没有）
# 下载：https://cli.github.com/

# 2. 登录 GitHub
gh auth login

# 3. 创建仓库并推送
gh repo create portfolio-backtest --public --source=. --push
```

### 方法 2: 手动创建

```bash
# 1. 在 GitHub 上创建新仓库
# 访问：https://github.com/new
# 仓库名：portfolio-backtest
# 选择 Public 或 Private
# 不要初始化 README（我们已经有了）

# 2. 初始化本地 git 仓库
cd "d:\0信银\26---new"
git init

# 3. 添加所有文件
git add .

# 4. 创建首次提交
git commit -m "Initial commit: Portfolio Backtest Framework

- 模块化的投资组合回测框架
- 支持风险平价和均值方差策略
- 多种协方差估计方法和优化算法
- 完整的文档和示例"

# 5. 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/portfolio-backtest.git

# 6. 推送到 GitHub
git branch -M main
git push -u origin main
```

### 方法 3: 使用 VS Code

1. **打开 VS Code**
   ```bash
   cd "d:\0信银\26---new"
   code .
   ```

2. **初始化 Git 仓库**
   - 点击左侧源代码管理图标（或按 Ctrl+Shift+G）
   - 点击"初始化存储库"按钮

3. **提交更改**
   - 在消息框中输入：`Initial commit: Portfolio Backtest Framework`
   - 点击 ✓ 提交

4. **推送到 GitHub**
   - 点击源代码管理面板中的"发布分支"按钮
   - 或者在终端运行：
     ```bash
     git remote add origin https://github.com/YOUR_USERNAME/portfolio-backtest.git
     git push -u origin main
     ```

## 📝 上传前检查清单

### ✅ 必要文件
- [x] README.md - 项目主页 ✨ 已创建
- [x] LICENSE - 许可证（建议添加 MIT）
- [x] requirements.txt - 依赖列表
- [x] .gitignore - Git 忽略文件

### 📋 创建 .gitignore

在项目根目录创建 `.gitignore` 文件：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
data/
outputs/
temp/

# Memory (Claude Code)
.claude/
```

### 📦 创建 requirements.txt

```bash
# 自动生成依赖列表
pip freeze > requirements.txt
```

或者手动创建：

```txt
# Core dependencies
pandas>=1.5.0
numpy>=1.23.0
scipy>=1.9.0
vectorbt>=0.25.0

# Visualization
matplotlib>=3.5.0
plotly>=5.0.0

# Development
jupyter>=1.0.0
pytest>=7.0.0
```

### 📄 创建 LICENSE

在项目根目录创建 `LICENSE` 文件（MIT 许可证）：

```
MIT License

Copyright (c) 2026 Portfolio Backtest Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🎨 上传后的优化

### 1. 启用 GitHub Pages
- 进入仓库 Settings → Pages
- Source 选择：Deploy from a branch
- Branch 选择：main / root
- 保存后就可以通过 `https://YOUR_USERNAME.github.io/portfolio-backtest/` 访问文档

### 2. 添加项目描述
在 GitHub 仓库页面点击右上角的 ⚙️ 设置：
- Description: 可扩展的投资组合回测框架
- Topics: `portfolio-optimization`, `backtesting`, `quantitative-finance`, `python`, `vectorbt`

### 3. 设置可见性
- Public: 任何人都可以查看
- Private: 只有你可以访问

## 🔗 常用 Git 命令

```bash
# 查看状态
git status

# 添加所有更改
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送到 GitHub
git push

# 拉取最新更改
git pull

# 查看提交历史
git log --oneline

# 创建新分支
git checkout -b feature-name

# 合并分支
git merge feature-name
```

## 📧 需要帮助？

如果遇到问题：
1. 查看 [GitHub 官方文档](https://docs.github.com/en)
2. 在项目的 Issues 中提问

## ✅ 完成后

上传成功后，你会看到：
- ✅ 漂亮的 README.md 主页
- ✅ 所有文档都可以在线阅读
- ✅ 代码版本管理
- 🎉 可以分享给其他人！

---

**准备好了吗？开始上传吧！** 🚀