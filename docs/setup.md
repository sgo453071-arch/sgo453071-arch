# Setup & Installation Guide

This guide walks you through setting up and running the Animated Linux Terminal GitHub Profile engine locally.

## Prerequisites

- **Python 3.11+** installed.
- **Git** installed.

## Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sgo453071-arch/sgo453071-arch.git
   cd sgo453071-arch
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install -r scripts/requirements.txt
   ```

## Running the Build Engine

Run the master build script to generate all SVGs and README.md:

```bash
python scripts/build.py
```

### Switching Color Themes

You can switch the active terminal color theme using the `--theme` flag:

```bash
python scripts/build.py --theme matrix
python scripts/build.py --theme dracula
python scripts/build.py --theme catppuccin
python scripts/build.py --theme nord
python scripts/build.py --theme tokyonight
python scripts/build.py --theme github
```

## GitHub Actions Automation

The repository includes a GitHub Action workflow (`.github/workflows/update-profile.yml`) that runs daily at midnight UTC. It automatically scrapes your latest contribution graph and regenerates the profile graphics.

Ensure GitHub repository settings permit GitHub Actions to write:
- Navigate to **Settings** > **Actions** > **General**.
- Under **Workflow permissions**, select **Read and write permissions**.
