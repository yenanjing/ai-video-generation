#!/bin/bash
# Helper script for git commits

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "==============================================="
echo "Git Commit Helper"
echo "==============================================="
echo ""

# Check if there are changes
if [[ -z $(git status -s) ]]; then
    echo "No changes to commit"
    exit 0
fi

# Show changes
echo "Changed files:"
git status -s
echo ""

# Get commit message
echo "Enter commit message:"
read -p "> " commit_msg

if [[ -z "$commit_msg" ]]; then
    echo "Commit message cannot be empty"
    exit 1
fi

# Add all changes
echo ""
echo "${YELLOW}Adding changes...${NC}"
git add .

# Commit
echo "${YELLOW}Committing...${NC}"
git commit -m "$commit_msg"

# Ask if should push
echo ""
read -p "Push to GitHub? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "${YELLOW}Pushing to GitHub...${NC}"
    git push
    echo ""
    echo "${GREEN}✓ Changes committed and pushed!${NC}"
else
    echo ""
    echo "${GREEN}✓ Changes committed locally${NC}"
    echo "Run 'git push' when ready to push to GitHub"
fi

echo ""
