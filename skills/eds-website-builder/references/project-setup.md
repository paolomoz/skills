# Project Setup — Detailed Guide

## Prerequisites

- Node.js 18+ and npm
- Git + GitHub account
- AEM CLI: `npm install -g @adobe/aem-cli`

## Creating a New Project

### From the AEM Boilerplate

The [aem-boilerplate](https://github.com/adobe/aem-boilerplate) is the canonical starting point. It provides:
- Pre-configured ESLint (Airbnb rules) and Stylelint
- Core `aem.js` library for page decoration
- `scripts.js` with three-phase loading pattern
- Example header/footer blocks
- `.hlxignore` for excluding files from serving

```bash
# 1. Create from template (recommended)
gh repo create my-org/my-site --template adobe/aem-boilerplate --public --clone

# 2. Install dependencies
cd my-site && npm install

# 3. Start dev server
aem up --no-open
```

### Content Source Configuration

Edit `fstab.yaml` to point at your content:

**Document Authoring (DA):**
```yaml
mountpoints:
  /: https://content.da.live/my-org/my-site/
```

**Google Drive:**
```yaml
mountpoints:
  /: https://drive.google.com/drive/folders/FOLDER_ID
```

**SharePoint:**
```yaml
mountpoints:
  /: https://my-org.sharepoint.com/:f:/r/sites/my-site/Shared%20Documents
```

### Local-Only Development (No CMS)

Create draft content as static HTML files:

```bash
mkdir drafts

# Create a page
cat > drafts/index.plain.html << 'EOF'
<body>
  <header></header>
  <main>
    <div>
      <h1>Welcome to My Site</h1>
      <p>This is a draft page for local development.</p>
    </div>
    <div>
      <div class="hero">
        <div>
          <div>
            <picture><img src="https://placehold.co/1200x400" alt="Hero image"></picture>
          </div>
          <div>
            <h2>Hero Heading</h2>
            <p>Hero description text goes here.</p>
            <p><strong><a href="/learn-more">Learn More</a></strong></p>
          </div>
        </div>
      </div>
    </div>
  </main>
  <footer></footer>
</body>
EOF

# Start with local content
aem up --no-open --html-folder drafts
```

Draft files use `.plain.html` or `.html` extensions. They follow the same markup structure as CMS-delivered content.

### head.html Configuration

The `head.html` file is injected into every page's `<head>`. Common contents:

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<link rel="stylesheet" href="/styles/styles.css">
<script src="/scripts/aem.js" type="module"></script>
<script src="/scripts/scripts.js" type="module"></script>
```

### .hlxignore

Prevent files from being served on aem.live (same syntax as .gitignore):

```
# Don't serve these
drafts/
tools/
analysis/
*.md
.env
```

## Dev Server

### Starting

```bash
# Standard
aem up --no-open

# With local content
aem up --no-open --html-folder drafts

# With port specification
aem up --no-open --port 3001

# With browser log forwarding (useful for debugging)
aem up --no-open --forward-browser-logs
```

### How It Works

The dev server at `http://localhost:3000`:
- Serves your local code (CSS, JS, blocks) — even uncommitted changes
- Fetches content from the configured content source (or local `drafts/` folder)
- Auto-reloads when files change
- Mirrors the same behavior as the aem.page preview environment

### Troubleshooting

**Server won't start:**
- Check if port 3000 is already in use: `lsof -i :3000`
- Try a different port: `aem up --port 3001`
- Ensure `fstab.yaml` exists and is valid YAML

**Content not loading:**
- Verify content source URL in `fstab.yaml`
- For DA: ensure content has been previewed (published to preview tier)
- For Drive/SharePoint: ensure sharing permissions are correct
- Check network tab in browser dev tools for 404s

**Blocks not loading:**
- Verify block directory name matches the block name in content
- Check browser console for JavaScript errors
- Ensure `.js` file extension is included in all imports

## GitHub Integration

AEM Code Sync watches your GitHub repository and automatically processes changes:

1. **Push to any branch** → Available at `https://{branch}--{repo}--{owner}.aem.page/`
2. **Merge to main** → Available at `https://main--{repo}--{owner}.aem.page/` (preview) and `.aem.live/` (live)

The Code Sync bot runs checks on PRs. Verify with:
```bash
gh pr checks
```

## CI/CD Pipeline

### GitHub Actions Workflow

Create a lint-on-push workflow at `.github/workflows/main.yaml`:

```yaml
name: Build
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v6
    - name: Use Node.js
      uses: actions/setup-node@v6
      with:
        node-version: 24
    - run: npm ci
    - run: npm run lint
```

This runs ESLint + Stylelint on every push. AEM Code Sync also runs its own checks on PRs (performance, sync status).

### Pull Request Template

Create `.github/pull_request_template.md` to enforce preview URLs on every PR:

```markdown
Please always provide the [GitHub issue(s)](../issues) your PR is for, as well as test URLs where your change can be observed (before and after):

Fix #<gh-issue-id>

Test URLs:
- Before: https://main--{repo}--{owner}.aem.live/
- After: https://<branch>--{repo}--{owner}.aem.live/
```

**Important**: PRs without a preview URL showing the change will be rejected. The preview URL must point to a page that demonstrates the block or feature being added/modified.

### Verifying PR Checks

```bash
# Check status of all PR checks (lint, code sync, performance)
gh pr checks

# View PR details
gh pr view
```

## Repository Settings

Configure via GitHub repository settings:
- Enable GitHub Pages (not required for EDS, but useful for docs)
- Add branch protection rules for `main`
- Configure the AEM Code Sync GitHub App if not auto-detected
