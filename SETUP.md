# Ember Command — Setup Guide

This template creates the red, orange, and amber profile shown in this folder. It generates two SVG files from your public GitHub data and refreshes them automatically with GitHub Actions.

## Fastest setup

1. Create a public repository named exactly like your GitHub username.
2. Copy **the contents** of `Ember-Command` into that repository.
3. Edit `config.json` and the three contact links in `README.md`.
4. Run `python scripts/generate.py --demo`.
5. Push the files and manually run the included GitHub Action once.

## Requirements

- A GitHub account
- Python 3.10 or newer for local generation
- Git, GitHub Desktop, or GitHub’s web uploader

No Python packages or paid services are required.

## 1. Create your profile repository

Create a **public** GitHub repository whose name exactly matches your username. For example, the user `octocat` needs a repository named `octocat`.

GitHub displays the root `README.md` from this special repository on your profile.

## 2. Copy the template

Copy everything **inside** `Ember-Command` into the root of your profile repository:

```text
your-username/
├── .github/workflows/update-profile.yml
├── assets/
│   ├── hero.svg
│   └── signal.svg
├── scripts/generate.py
├── config.json
├── README.md
└── SETUP.md
```

Important: `.github` may be hidden by your file manager. Make sure it is copied, or automatic updates will not work.

## 3. Personalize `config.json`

Replace every example value:

- `username`: your exact GitHub username
- `name`, `role`, `location`, `status`, and `focus`: your profile text
- `website`: your complete website URL
- `skills`: up to six short skill names
- `featured_repos`: up to four exact public repository names

If a featured repository cannot be found, the generator automatically uses one of your most-starred public repositories.

## 4. Update the contact buttons

At the bottom of `README.md`, replace the portfolio, GitHub, and LinkedIn URLs. Remove any button you do not need.

## 5. Generate the assets

Run this command from the repository root:

```bash
python scripts/generate.py --demo
```

This creates a reliable offline preview. Generate with your live public GitHub data afterward:

```bash
python scripts/generate.py
```

The live command needs internet access. If GitHub temporarily rate-limits local requests, push the template and run the Action instead; it receives an automatic GitHub token.

## 6. Preview the result

- In VS Code, open `README.md` and press `Ctrl+Shift+V`.
- For the exact GitHub result, push the repository and open it on GitHub.

Do not rename `assets/hero.svg` or `assets/signal.svg` unless you also update their paths in `README.md`.

## 7. Enable automatic updates

Push the repository, then open **Actions → Update Ember Command → Run workflow**. The workflow refreshes the assets every Monday and Thursday.

If the Action cannot push its update:

1. Open **Settings → Actions → General**.
2. Find **Workflow permissions**.
3. Select **Read and write permissions**.
4. Save and run the workflow again.

## Customize the palette

Edit the color constants near the top of `scripts/generate.py`:

```python
RED = "#ff4d3d"
ORANGE = "#ff8a1f"
GOLD = "#ffc857"
CREAM = "#fff4e6"
```

Rerun the generator after changing colors or content.

## AI-assisted setup prompt

Copy this prompt into Codex, ChatGPT, Claude, or another coding assistant while the profile repository is open:

```text
Set up the Ember Command GitHub profile template in this repository for me.

My details:
- GitHub username: [USERNAME]
- Full name: [NAME]
- Role: [ROLE]
- Location: [LOCATION]
- Short status: [STATUS]
- Current focus: [FOCUS]
- Website: [WEBSITE URL]
- Skills, maximum 6: [SKILLS]
- Featured repositories, maximum 4: [REPOSITORIES]
- LinkedIn URL: [LINKEDIN URL]

Please inspect the existing files first. Update config.json and the contact links in README.md, preserve the Ember Command design and animations, generate the assets, validate the SVG files and Markdown links, and confirm the GitHub Action is correctly placed. Use demo generation first and live generation if internet access is available. Do not delete unrelated files, and do not commit or push unless I explicitly ask.
```

## Common problems

- **Images are missing:** run the generator from the repository root and commit the generated `assets` files.
- **The Action is missing:** verify `.github/workflows/update-profile.yml` was copied.
- **Wrong account data appears:** correct `username` in `config.json`; the Action automatically uses the repository owner.
