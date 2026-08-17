# Jenesyx Terminal — Setup Guide

This template creates the green terminal profile shown in this folder: a self-typing ASCII portrait, neofetch-style information card, and live contribution heatmap.

## Fastest setup

1. Create a public repository named exactly like your GitHub username.
2. Copy **the contents** of `Jenesyx` into it, excluding `.git` and `.venv` if they exist locally.
3. Edit the personal text in `scripts/make_info_card.py` and the contact links in `README.md`.
4. Replace `source-photo.jpg` and regenerate the portrait.
5. Push the repository and run **Update profile art** in GitHub Actions.

## Requirements

- A GitHub account
- Python 3.10 or newer
- Git, GitHub Desktop, or GitHub’s web uploader
- The included Python requirements files

No paid API or external stats-card service is required.

## 1. Create your profile repository

Create a **public** GitHub repository whose name exactly matches your username. GitHub displays its root `README.md` on your profile.

## 2. Copy the template

Copy the template files into the root of your profile repository:

```text
your-username/
├── .github/workflows/update-profile-art.yml
├── data/contributions.json
├── scripts/
├── avi-ascii.svg
├── contrib-heatmap.svg
├── info-card.svg
├── source-photo.jpg
├── source-prepped.png
├── whoami.svg
├── README.md
└── SETUP.md
```

Do **not** copy a nested `.git` folder or `.venv` environment. Make sure the hidden `.github` folder is copied.

## 3. Personalize the information card

Open `scripts/make_info_card.py` and edit only the section marked `EDIT ME`:

```python
USER = "your-terminal-name"
HOST = "your-github-username"
ROWS = [
    ("Now", "What you are currently building"),
    ("Stack", "Your main technologies"),
    ("Learning", "What you are learning"),
    ("Reach", "Your username and website"),
]
```

Keep values reasonably short; long text wraps and makes the card taller.

Regenerate the card and combined identity image:

```bash
python scripts/make_info_card.py
python scripts/compose_whoami.py
```

## 4. Create your ASCII portrait

Replace `source-photo.jpg` with your portrait. A plain or removed background produces the best ASCII result.

### Basic method

Use this when your photo already has a simple background:

```bash
python -m pip install -r scripts/requirements-portrait-basic.txt
python scripts/prep_photo.py source-photo.jpg --no-rembg
python scripts/make_ascii_svg.py
python scripts/compose_whoami.py
```

### Automatic background-removal method

This installs larger machine-learning dependencies but can remove a complex background automatically:

```bash
python -m pip install -r scripts/requirements-portrait.txt
python scripts/prep_photo.py source-photo.jpg
python scripts/make_ascii_svg.py
python scripts/compose_whoami.py
```

If the portrait looks too bright, dark, or detailed, adjust `--clip`, `--gamma`, or the `--cols` value documented by the scripts, then regenerate it.

## 5. Update the README

In `README.md`:

- Replace `arta@github` in the terminal headings.
- Replace the website and social URLs.
- Replace badge labels and usernames.
- Remove contact buttons you do not need.

Do not rename `whoami.svg` or `contrib-heatmap.svg` unless their paths are also updated in `README.md`.

## 6. Generate live contribution data locally

Install the lightweight daily dependencies:

```bash
python -m pip install -r scripts/requirements.txt
python scripts/fetch_contributions.py your-github-username
python scripts/render_heatmap_svg.py
```

This updates `data/contributions.json` and `contrib-heatmap.svg`. Internet access is required.

## 7. Preview the result

- Open `README.md` in VS Code and press `Ctrl+Shift+V`.
- Push the repository for the exact GitHub SVG rendering and animation behavior.

## 8. Enable automatic updates

Push the repository and open **Actions → Update profile art → Run workflow**. The workflow refreshes the contribution heatmap every day.

If the workflow cannot commit:

1. Open **Settings → Actions → General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Save and run the workflow again.

The portrait and information card change only when you regenerate and commit them; the daily workflow intentionally updates only contribution data.

## AI-assisted setup prompt

Place your source portrait in the repository, then copy this prompt into a coding assistant:

```text
Set up the Jenesyx Terminal GitHub profile template in this repository for me.

My details:
- GitHub username: [USERNAME]
- Terminal user name: [SHORT NAME]
- Full name: [NAME]
- Current work: [CURRENT WORK]
- Previous work: [PREVIOUS WORK]
- Technology stack: [STACK]
- Highlights: [HIGHLIGHTS]
- Currently learning: [LEARNING]
- Website and social links: [LINKS]
- Portrait image path: [PATH TO MY PHOTO]

Please inspect the existing repository and scripts first. Do not copy or modify nested .git or .venv folders. Update only the EDIT ME section in scripts/make_info_card.py and the personal headings, badges, and links in README.md. Prepare the portrait, generate avi-ascii.svg and info-card.svg, compose whoami.svg, fetch my live contribution data if internet access is available, render contrib-heatmap.svg, and validate all generated SVG files and local Markdown links. Preserve the terminal design and animations. Verify that the workflow supports the default branch and is correctly placed. Do not change unrelated files, and do not commit or push unless I explicitly ask.
```

## Common problems

- **Portrait generation uses too much memory:** use the basic method with `--no-rembg`.
- **Portrait has a noisy background:** use a cut-out image or the full background-removal method.
- **Two panels do not align:** rerun `make_info_card.py`, then `compose_whoami.py` last.
- **Contribution data is wrong:** pass the exact username to `fetch_contributions.py` or run the Action in the correct profile repository.
