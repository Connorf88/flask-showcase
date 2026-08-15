# Autonomous Deployment Demo 🚀

A Flask service that proves its own deployment pipeline works.

Push a commit, and a five-job GitHub Actions pipeline lints it, tests it, builds a Docker image, pushes that image to GitHub Container Registry, deploys it to Render, and then polls the live service until it confirms the new commit is answering. No manual step anywhere in that chain.

The page the service returns displays the commit SHA, image tag, and build timestamp baked into the running container. **When the pipeline runs, the values on the live page change.** That visible change is the demo.

---

## 🛠️ What's Inside

| Component | What it does | Built with |
|---|---|---|
| **Application** | Serves a deployment manifest showing the running build's provenance | Flask, Jinja2 |
| **Container** | Multi-stage build, non-root user, baked-in health check | Docker |
| **Pipeline** | Five dependent jobs, gated so failures never reach production | GitHub Actions |
| **Registry** | Versioned images tagged by commit SHA | GitHub Container Registry |
| **Hosting** | Pulls and runs the published image | Render (free tier) |
| **Tests** | Seven tests that must pass before an image is ever built | pytest |

---

## 🌐 Goals

- Demonstrate a complete commit-to-production pipeline, not a fragment of one
- Make the automation *visible* rather than something you have to take on faith
- Keep quality gates real: a failing test stops the deploy
- Follow container practices that hold up to review — non-root, multi-stage, pinned dependencies
- Provide a template that works for any containerized application

---

## 🧰 Tools & Technologies

- **CI/CD:** GitHub Actions
- **Containers:** Docker (multi-stage), Docker Compose
- **Registry:** GitHub Container Registry (GHCR)
- **Hosting:** Render
- **Language:** Python 3.12
- **Framework:** Flask, served by gunicorn
- **Quality:** pytest, ruff

---

## 📁 Project Structure

```
autonomous-deployment-demo/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          Five-job pipeline
├── src/
│   ├── app.py                 Flask service
│   ├── requirements.txt       Pinned dependencies
│   └── templates/
│       └── index.html         Deployment manifest page
├── tests/
│   └── test_app.py            Test suite (7 tests)
├── Dockerfile                 Multi-stage build
├── docker-compose.yml         Local development
├── ruff.toml                  Lint configuration
├── .dockerignore              Keeps the image clean
├── .gitignore
├── .env.example
├── LICENSE
└── README.md
```

---

## 🔄 How the Pipeline Works

```
git push origin main
        │
        ├──▶ 01  Lint      ruff checks style
        ├──▶ 02  Test      pytest runs 7 tests
        │         │
        │         ▼        both must pass
        ├──▶ 03  Build     image built, tagged by commit SHA,
        │         │        pushed to ghcr.io
        │         ▼
        ├──▶ 04  Deploy    Render pulls and runs the new image
        │         │
        │         ▼
        └──▶ 05  Verify    polls /health until it reports the
                           commit that was just pushed
```

Jobs 1 and 2 run in parallel. Job 3 waits for both. If either fails, no image is built and nothing deploys.

Job 5 matters more than it looks: without it, a deploy that silently never came up would still show a green checkmark. Verifying that the *specific new commit* is live is the difference between "the pipeline finished" and "the change is actually in production."

Pull requests run jobs 1–3 (the image is built to prove it compiles, but not pushed) and skip deployment. Only `main` deploys.

---

## 💻 Running Locally

**Prerequisites:** [Git](https://git-scm.com), [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
git clone https://github.com/connorf88/autonomous-deployment-demo.git
cd autonomous-deployment-demo
docker compose up --build
```

Open <http://localhost:5000>.

<details>
<summary>Without Docker (plain Python)</summary>

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r src/requirements.txt
python src/app.py
```
</details>

**Run the tests:**

```bash
pip install pytest ruff
pytest tests/ -v
ruff check src/ tests/
```

---

## 🔌 Endpoints

| Route | Returns |
|---|---|
| `/` | Deployment manifest page |
| `/health` | Liveness JSON including the running commit SHA |
| `/api/info` | Full build metadata as JSON |

---

## ⚙️ Configuration

The pipeline needs two values, set under **Settings → Secrets and variables → Actions**:

| Name | Type | Value |
|---|---|---|
| `RENDER_DEPLOY_HOOK` | Secret | Deploy hook URL from your Render service settings |
| `APP_URL` | Variable | Your live Render URL, no trailing slash |

`GITHUB_TOKEN` is provided automatically — you don't create it.

---

## 🌍 Live Deployment

🔗 **Live app:** _add your Render URL here once deployed_

**To watch the automation happen:**

1. Note the commit SHA shown on the live page
2. Change something in `src/` and push it
3. Open the **Actions** tab and watch the five jobs run
4. Refresh the live page — the SHA has changed

That loop, done in front of an interviewer, is the whole portfolio pitch.

---

## 🔧 Adapting This for Your Own Projects

The pipeline doesn't care what language the app is in. To reuse it:

1. Replace `src/` with your application
2. Adjust the `Dockerfile` base image and install step for your stack
3. Update the lint and test commands in jobs 01 and 02
4. Point `RENDER_DEPLOY_HOOK` at a different service, or swap job 04 for AWS, Fly.io, or Railway

The structure — gate, build, publish, deploy, verify — stays the same.

---

## 📌 About

Built by **Connor F** ([@connorf88](https://github.com/connorf88)) while moving into DevOps engineering.

I wanted a project that showed the whole delivery path rather than one piece of it, and that a reviewer could verify in about thirty seconds by clicking a link and watching the commit hash change.

---

## 📬 Feedback

Spotted something that could be better? Open an issue — I'm learning, and I'd rather know.

---

## 📄 License

MIT — fork it, adapt it, use it as a starting point for your own portfolio.
