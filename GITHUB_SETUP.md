# GitHub Setup Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ai-video-generation` (or your preferred name)
3. Description: `AI video generation system with LLM-powered storyboarding`
4. Choose: **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Link Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add GitHub as remote origin (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/ai-video-generation.git

# Or if using SSH:
git remote add origin git@github.com:YOUR_USERNAME/ai-video-generation.git

# Verify remote was added
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Verify Upload

Go to your GitHub repository URL and verify all files are there:
- ✅ video_engine/ directory
- ✅ agent_harness/ directory
- ✅ Documentation files (README.md, QUICKSTART.md, etc.)
- ✅ examples/ directory
- ✅ .gitignore file
- ✅ requirements.txt

## Quick Commands Reference

```bash
# Check current git status
git status

# Add all changes
git add .

# Commit with message
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull latest changes
git pull

# View commit history
git log --oneline

# Create and switch to new branch
git checkout -b feature-name

# Switch back to main
git checkout main
```

## Recommended: Add GitHub Repository Info to README

After creating the repository, update README.md with:

```markdown
## Repository

GitHub: https://github.com/YOUR_USERNAME/ai-video-generation

## Clone

\`\`\`bash
git clone https://github.com/YOUR_USERNAME/ai-video-generation.git
cd ai-video-generation
pip install -r requirements.txt
\`\`\`
```

## Git Workflow for Future Changes

1. **Make changes** to code
2. **Test changes**:
   ```bash
   python test_video_engine.py
   python check_readiness.py
   ```
3. **Stage changes**:
   ```bash
   git add .
   # Or add specific files:
   git add video_engine/core/orchestrator.py
   ```
4. **Commit changes**:
   ```bash
   git commit -m "Add feature X"
   # Or for detailed commit:
   git commit -m "Add feature X

   - Implemented Y
   - Fixed Z
   - Updated documentation"
   ```
5. **Push to GitHub**:
   ```bash
   git push
   ```

## Example Commit Messages

Good commit messages:
- ✅ `Add CogVideoX model adapter`
- ✅ `Fix video concatenation bug for transition effects`
- ✅ `Update documentation with new examples`
- ✅ `Implement FastAPI REST endpoints (Phase 2)`

Less helpful:
- ❌ `Update`
- ❌ `Fix bug`
- ❌ `Changes`

## Branching Strategy (Optional)

For larger features, use branches:

```bash
# Create feature branch
git checkout -b feature/fastapi-backend

# Work on feature, make commits
git add .
git commit -m "Add FastAPI app structure"

# Push branch to GitHub
git push -u origin feature/fastapi-backend

# When done, merge to main
git checkout main
git merge feature/fastapi-backend
git push
```

## Useful Git Commands

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes
git reset --hard HEAD

# View changes before committing
git diff

# View staged changes
git diff --cached

# Show file history
git log --follow filename.py

# Create a tag for releases
git tag -a v1.0.0 -m "Phase 1 Complete"
git push --tags
```

## GitHub Features to Enable

1. **Issues**: Track bugs and feature requests
2. **Projects**: Organize work (for Phase 2, 3, 4)
3. **Actions**: CI/CD (future: automated testing)
4. **Releases**: Version releases

## Next Steps After GitHub Setup

1. ✅ Repository created and pushed
2. Add GitHub URL to README.md
3. Create initial GitHub Release (v1.0.0 - Phase 1)
4. Consider adding:
   - CONTRIBUTING.md
   - LICENSE file
   - GitHub Actions for testing
   - Issue templates

## Help

If you encounter issues:

```bash
# Check if remote is set
git remote -v

# Check current branch
git branch

# View git configuration
git config --list

# Set user info (if needed)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```
