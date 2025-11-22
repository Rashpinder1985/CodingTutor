# Git Repository Guide

## Repository Status

✅ Git repository initialized  
✅ Initial commit made (commit hash: 7759d71)  
✅ All project files committed  
✅ .gitignore configured (excludes venv, .env, generated files)

## Repository Contents

**Total:** 19 files, 4042 lines of code

**Files committed:**
- Documentation (5 files)
- Python source code (9 files)
- Configuration files (3 files)
- Utility scripts (2 files)

## Basic Git Commands

### View Status
```bash
git status          # Check current status
git log             # View commit history
git log --oneline   # Compact commit history
```

### Make Changes
```bash
# After making changes to files:
git add .                    # Stage all changes
git add specific_file.py     # Stage specific file
git commit -m "Description"  # Commit with message
```

### View Changes
```bash
git diff                # View unstaged changes
git diff --staged       # View staged changes
git show               # View last commit
```

### Branches
```bash
git branch                    # List branches
git branch feature-name       # Create new branch
git checkout feature-name     # Switch to branch
git checkout -b feature-name  # Create and switch to branch
git merge feature-name        # Merge branch into current
```

### Remote Repository

If you want to push this to GitHub/GitLab:

```bash
# On GitHub, create a new repository (without initializing with README)
# Then:

git remote add origin https://github.com/yourusername/Agent_Compute.git
git branch -M main
git push -u origin main
```

## Recommended Workflow

### Daily Development
```bash
# 1. Check status
git status

# 2. Make your changes in the code

# 3. Review changes
git diff

# 4. Stage changes
git add .

# 5. Commit
git commit -m "Descriptive message about changes"

# 6. (Optional) Push to remote
git push
```

### Feature Development
```bash
# 1. Create feature branch
git checkout -b add-new-language

# 2. Make changes and commit
git add .
git commit -m "Add support for Ruby language"

# 3. Switch back to main
git checkout main

# 4. Merge feature
git merge add-new-language

# 5. Delete feature branch (optional)
git branch -d add-new-language
```

## What's Ignored

The `.gitignore` file excludes:
- `venv/` - Virtual environment
- `.env` - Environment variables (API keys)
- `*.pyc`, `__pycache__/` - Python bytecode
- `generated_questions.json` - Generated output files
- `*.xlsx` (except sample) - Excel files
- `*.log` - Log files
- IDE files (`.vscode/`, `.idea/`)

## Common Scenarios

### Undo Last Commit (keep changes)
```bash
git reset --soft HEAD~1
```

### Undo Changes to File
```bash
git checkout -- filename.py
```

### View File from Previous Commit
```bash
git show HEAD~1:src/input_processor.py
```

### Create a Tag/Release
```bash
git tag -a v1.0.0 -m "Version 1.0.0 - Initial release"
git push origin v1.0.0
```

## Commit Message Guidelines

Good commit messages:
- ✅ "Add support for Ruby programming language"
- ✅ "Fix bug in Excel parsing for empty cells"
- ✅ "Update documentation with new examples"
- ✅ "Refactor question generator for better performance"

Bad commit messages:
- ❌ "Update"
- ❌ "Fix bug"
- ❌ "Changes"
- ❌ "WIP"

## Initial Commit Details

```
Commit: 7759d71
Branch: main
Files: 19
Lines: 4042
Message: Initial commit: Adaptive Question Generation Tool
```

## Next Steps

### To Push to GitHub:

1. **Create GitHub Repository**
   - Go to github.com
   - Click "New repository"
   - Name it "Agent_Compute" or "adaptive-question-generator"
   - Don't initialize with README (you already have one)

2. **Connect and Push**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
   git push -u origin main
   ```

3. **Verify**
   - Visit your GitHub repository
   - All files should be visible

### To Create .gitignore for Generated Files

Already done! The `.gitignore` is configured to exclude:
- Generated JSON files
- Excel files (except sample)
- Virtual environment
- Environment variables
- IDE configs

## Best Practices

1. **Commit Often**: Make small, focused commits
2. **Write Good Messages**: Describe what and why
3. **Use Branches**: Develop features in separate branches
4. **Pull Before Push**: If working with others
5. **Review Before Commit**: Use `git diff` to review changes
6. **Don't Commit Secrets**: Never commit API keys (.env is gitignored)
7. **Tag Releases**: Use tags for version releases

## Useful Aliases

Add to `~/.gitconfig`:

```ini
[alias]
    st = status
    co = checkout
    br = branch
    cm = commit -m
    last = log -1 HEAD
    unstage = reset HEAD --
    visual = log --oneline --graph --decorate --all
```

Then use:
```bash
git st          # instead of git status
git co main     # instead of git checkout main
git visual      # pretty branch visualization
```

## Repository Statistics

```bash
# Count commits
git rev-list --count main

# Count files
git ls-files | wc -l

# Count lines of code
git ls-files | xargs wc -l

# See who contributed what
git shortlog -sn

# Repository size
du -sh .git
```

## Troubleshooting

### Accidentally Committed Large File
```bash
git rm --cached large_file.xlsx
git commit -m "Remove large file"
```

### Wrong Commit Message
```bash
git commit --amend -m "Correct message"
```

### Committed to Wrong Branch
```bash
git reset --soft HEAD~1
git stash
git checkout correct-branch
git stash pop
git commit -m "Correct message"
```

### Need to Ignore Already Tracked File
```bash
git rm --cached filename
# Add filename to .gitignore
git commit -m "Stop tracking filename"
```

## GitHub Integration

### Add README Badge
Add to top of README.md:
```markdown
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
```

### GitHub Actions (Optional)
Create `.github/workflows/test.yml` for automated testing

### Issues and Pull Requests
Use GitHub Issues to track:
- Bugs
- Feature requests
- Enhancements
- Questions

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Repository Ready!** Your code is now version controlled and ready to be shared on GitHub or other Git platforms.

