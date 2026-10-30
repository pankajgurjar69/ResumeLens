# GitHub guide for beginners

1. Sign in to GitHub and create a new repository named `ResumeLens`.
2. Do not initialise it with a README if you already have this project's README.
3. Open VS Code terminal inside the `ResumeLens` project folder.
4. Run these commands one by one:

```bash
git init
git add .
git status
git commit -m "Initial ResumeLens MVP"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ResumeLens.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If Git asks you to sign in, complete GitHub's browser authentication. Before pushing, check `git status` and confirm no real resumes, `.env` files or database files are included.
