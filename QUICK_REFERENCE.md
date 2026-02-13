# AI Video Generation - 快速参考卡片

## 🚀 快速开始

### 推送到 GitHub（首次）
```bash
# 1. 在 GitHub 创建仓库: https://github.com/new
# 2. 执行以下命令（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/ai-video-generation.git
git push -u origin main
```

### 生成视频
```bash
# 基础用法
python -m video_engine.cli generate "您的视频描述"

# 完整选项
python -m video_engine.cli generate "海滩日落" \
  --model replicate:svd-xt \
  --max-shots 3 \
  --output my_video.mp4
```

## 📝 Git 工作流

### 方式1：使用便捷脚本
```bash
./git_commit.sh
```

### 方式2：手动提交
```bash
git add .
git commit -m "您的提交信息"
git push
```

## 🔧 常用命令

### Git 命令
```bash
git status              # 查看更改状态
git diff                # 查看具体更改
git log --oneline       # 查看提交历史
git pull                # 拉取最新代码
```

### 视频生成命令
```bash
python -m video_engine.cli generate "提示词"           # 生成视频
python -m video_engine.cli storyboard "提示词"         # 只生成故事板
python -m video_engine.cli list-models                # 列出可用模型
python -m video_engine.cli list-jobs                  # 列出所有任务
```

### 系统检查
```bash
python check_readiness.py     # 检查系统准备情况
python test_video_engine.py   # 运行测试套件
```

## 📁 重要文件

| 文件 | 说明 |
|------|------|
| `.env` | API 密钥配置（需手动添加） |
| `README.md` | 项目概览 |
| `QUICKSTART.md` | 详细设置指南 |
| `GITHUB_SETUP.md` | Git 工作流指南 |
| `PROJECT_SUMMARY.md` | 完整项目总结 |
| `git_commit.sh` | 便捷提交脚本 |

## 🔑 配置 API 密钥

编辑 `.env` 文件：
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
REPLICATE_API_TOKEN=r8_your-token-here
```

获取密钥：
- Anthropic: https://console.anthropic.com/
- Replicate: https://replicate.com/account/api-tokens

## 💰 成本估算

每个3镜头视频（约10秒）：
- Claude API（故事板）：~$0.02
- Replicate SVD-XT（视频）：~$0.36
- **总计**：~$0.40/视频

## ⏱️ 生成时间

- 故事板：5-10秒
- 每个镜头：60-90秒
- 3镜头视频：约3-4分钟
- 5镜头视频：约5-7分钟

## 🎯 提交信息示例

**推荐**：
- ✅ `添加 FastAPI 后端端点`
- ✅ `修复视频拼接转场效果 bug`
- ✅ `更新文档：添加 I2V 使用示例`
- ✅ `实现 CogVideoX 模型适配器`

**不推荐**：
- ❌ `更新`
- ❌ `修复`
- ❌ `改动`

## 📊 项目状态

```
✅ Phase 1: 核心引擎          - 完成
📋 Phase 2: FastAPI 后端      - 待开始
📋 Phase 3: React 前端        - 待开始
📋 Phase 4: 生产功能          - 待开始
```

## 🆘 故障排除

### API 密钥错误
```bash
cat .env | grep API_KEY    # 检查密钥配置
```

### FFmpeg 未找到
```bash
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Ubuntu
```

### Git 推送失败
```bash
git remote -v              # 检查远程仓库配置
git config --list          # 查看 Git 配置
```

## 📚 更多文档

- 完整文档：`README_VIDEO.md`
- 快速开始：`QUICKSTART.md`
- 命令参考：`COMMANDS.md`
- Git 指南：`GITHUB_SETUP.md`
- 项目总结：`PROJECT_SUMMARY.md`

## 🎓 示例代码

查看 `examples/` 目录：
- `generate_video.py` - 编程方式生成视频
- `generate_storyboard.py` - 生成故事板示例

---

**快速帮助**：需要详细说明？运行 `cat GITHUB_SETUP.md`
