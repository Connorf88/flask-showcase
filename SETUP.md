# Setup Guide — Connor

Every command here is ready to copy and paste. Do the parts in order; each one assumes the previous finished.

Delete this file before you push if you'd rather it not appear in the repo — or leave it, it does no harm.

---

## Part 1 — Put the project on your computer

1. Unzip the download. You'll get a folder called `autonomous-deployment-demo`.
2. Move it somewhere you'll find again, for example `C:\Users\<you>\Projects\`.
3. Open **PowerShell**.
4. Go into the folder. Replace the path with wherever you actually put it:

```powershell
cd C:\Users\<you>\Projects\autonomous-deployment-demo
```

5. Confirm you're in the right place — you should see `Dockerfile`, `README.md`, `src`:

```powershell
ls
```

---

## Part 2 — First commit

Run these one at a time.

```powershell
git init
```

```powershell
git config user.name "connorf88"
```

```powershell
git config user.email "your-github-email@example.com"
```

> Use the email on your GitHub account, or commits won't be linked to your profile.

```powershell
git add .
```

```powershell
git status
```

You should see a list of files in green. That's everything staged and ready.

```powershell
git commit -m "Initial commit: autonomous deployment pipeline"
```

---

## Part 3 — Create the GitHub repository

1. Go to <https://github.com/new>
2. **Repository name:** `autonomous-deployment-demo`
3. **Description:** `Flask service with a five-job CI/CD pipeline: build, publish to GHCR, deploy to Render, verify.`
4. Set it to **Public** — a private portfolio project can't be seen by employers.
5. **Do not** tick "Add a README", "Add .gitignore", or "Choose a license". You already have all three. Ticking them causes a conflict on your first push.
6. Click **Create repository**.

---

## Part 4 — Push

Back in PowerShell:

```powershell
git remote add origin https://github.com/connorf88/autonomous-deployment-demo.git
```

```powershell
git branch -M main
```

```powershell
git push -u origin main
```

A browser window will open asking you to sign in to GitHub. Approve it.

Refresh your repository page — your code is there.

**The pipeline will start running immediately.** Click the **Actions** tab to watch. Jobs 01, 02, and 03 will pass. Job 04 will fail, because you haven't connected Render yet. That's expected, and Part 5 fixes it.

---

## Part 5 — Deploy on Render

1. Go to <https://render.com> and sign up with your GitHub account. No card needed for the free tier.
2. Click **New** → **Web Service**.
3. Choose **Build and deploy from a Git repository**, then connect `connorf88/autonomous-deployment-demo`.
4. Fill in:
   - **Name:** `autonomous-deployment-demo`
   - **Region:** whichever is closest to you
   - **Branch:** `main`
   - **Runtime / Language:** `Docker`
   - **Instance type:** `Free`
5. Click **Create Web Service** and wait for the first build — a few minutes.
6. Copy your live URL from the top of the page. It looks like `https://autonomous-deployment-demo.onrender.com`.
7. Open it. You should see the deployment manifest page.

> **Free tier behaviour:** the service sleeps after 15 minutes of no traffic, and the next visit takes 30–50 seconds to wake it. This is normal. Mention it in your README if you like — knowing your infrastructure's limits is a point in your favour, not against you.

---

## Part 6 — Connect the pipeline to Render

**Get the deploy hook:**

1. In Render, open your service → **Settings**
2. Scroll to **Deploy Hook** and copy the URL

**Add it to GitHub:**

1. Go to `https://github.com/connorf88/autonomous-deployment-demo/settings/secrets/actions`
2. **New repository secret**
   - Name: `RENDER_DEPLOY_HOOK`
   - Secret: paste the deploy hook URL
   - **Add secret**
3. Switch to the **Variables** tab → **New repository variable**
   - Name: `APP_URL`
   - Value: your Render URL, **with no trailing slash**
   - **Add variable**

**Run the full pipeline:**

1. Go to the **Actions** tab
2. Click **CI/CD Pipeline** in the left sidebar
3. Click **Run workflow** → **Run workflow**

All five jobs should go green. Job 05 confirms your commit is live.

---

## Part 7 — Finish the README

Open `README.md` and find this line:

```
🔗 **Live app:** _add your Render URL here once deployed_
```

Replace it with your actual URL. Then:

```powershell
git add README.md
```

```powershell
git commit -m "Add live deployment URL"
```

```powershell
git push
```

Watch the Actions tab. This push runs the whole pipeline end to end and redeploys the site.

---

## Part 8 — The thing that gets you hired

Once everything is green:

1. Open your live site. Note the commit SHA on the page.
2. Change something visible — edit the text in `src/templates/index.html`.
3. Commit and push:

```powershell
git add .
```

```powershell
git commit -m "Update manifest copy"
```

```powershell
git push
```

4. Open the Actions tab and watch the five jobs run.
5. Wait for job 05 to go green, then refresh your live site.

**The SHA has changed.** You didn't touch a server.

Record that loop — code change, pipeline running, live page updating — as a short screen recording or GIF and put it at the top of your README. It's the single most persuasive thing in the whole project, because it takes an interviewer ten seconds to understand and can't be faked.

---

## If something breaks

**`git: command not found`**
Git isn't installed. Get it from <https://git-scm.com/download/win>, then close and reopen PowerShell.

**`remote origin already exists`**
You ran the remote command twice. Fix it with:
```powershell
git remote set-url origin https://github.com/connorf88/autonomous-deployment-demo.git
```

**`failed to push some refs` / `rejected`**
You ticked one of the "initialize with" boxes when creating the repo. Run:
```powershell
git pull origin main --allow-unrelated-histories
```
then push again.

**Job 04 fails: "RENDER_DEPLOY_HOOK is not set"**
Part 6 isn't done, or the secret name is misspelled. It must match exactly.

**Job 05 times out**
Usually the free instance waking up slowly, or `APP_URL` has a trailing slash. Check the variable, then re-run the job from the Actions tab.

**Render build fails**
Open the Render logs. Confirm **Runtime** is set to `Docker` — if Render guessed `Python`, it ignores your Dockerfile and the build won't match what the pipeline produces.

---

## What to do next

Once this is running, the natural additions — roughly in order of effort:

- A status badge at the top of the README (Actions tab → workflow → ⋯ → Create status badge)
- Security scanning in the pipeline (Trivy scans the image for known CVEs)
- A second environment, so `main` deploys to staging and a tag deploys to production
- Swap Render for a small Kubernetes deployment once you want orchestration on your résumé

Each one is a real talking point. None of them matter until this first one is live and working.
