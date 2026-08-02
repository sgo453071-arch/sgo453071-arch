# Customization & Configuration Guide

Everything rendered on the GitHub profile is configuration-driven. No Python code edits are required to update your profile details or theme.

## Updating Personal Info

Edit `config/profile.json`:

```json
{
  "name": "Your Name",
  "username": "your-github-username",
  "tagline": "Full Stack Developer & Systems Engineer",
  "roles": ["Software Engineer", "Systems Architect"],
  "learning": "Distributed Systems & Machine Learning",
  "current_focus": "Building AI-powered developer tools",
  "editor": "VS Code",
  "os": "Linux / Windows (WSL2)",
  "stacks": {
    "languages": ["Python", "TypeScript", "C++", "SQL"],
    "backend": ["FastAPI", "Node.js", "Django"],
    "frontend": ["React", "Next.js", "Tailwind CSS"],
    "database": ["PostgreSQL", "MongoDB", "Redis"],
    "cloud": ["AWS", "Docker", "Vercel"],
    "devops": ["Git", "GitHub Actions", "Docker"],
    "tools": ["Git", "VS Code", "Postman"]
  },
  "socials": {
    "github": "https://github.com/your-username",
    "linkedin": "https://linkedin.com/in/your-profile",
    "twitter": "https://twitter.com/your-handle",
    "portfolio": "https://your-portfolio.dev",
    "email": "your-email@example.com",
    "leetcode": "https://leetcode.com/your-username"
  }
}
```

## Adding / Editing Projects

Edit `config/projects.json`:

Add or modify objects in the JSON array:

```json
[
  {
    "id": "my-project",
    "output_file": "project-disha.svg",
    "title": "Project Title",
    "subtitle": "Short Subtitle",
    "description": "Comprehensive project description...",
    "tech_stack": ["Python", "FastAPI", "Docker"],
    "status": "ACTIVE",
    "highlights": [
      "Key feature 1",
      "Key feature 2"
    ],
    "github_url": "https://github.com/username/project"
  }
]
```

## Customizing Profile Picture

1. Place your desired photo at `assets/profile.jpg`.
2. Run `python scripts/build.py`.
3. The engine will automatically crop, boost contrast, and convert your photo into the animated ASCII portrait!

## Creating Custom Color Themes

Create a new JSON file inside `themes/my-theme.json`:

```json
{
  "name": "My Custom Theme",
  "background": "#0d1117",
  "card_bg": "#161b22",
  "header_bg": "#21262d",
  "border": "#30363d",
  "text_main": "#c9d1d9",
  "text_muted": "#8b949e",
  "accent": "#58a6ff",
  "accent_secondary": "#bc8cff",
  "success": "#3fb950",
  "warning": "#d29922",
  "heatmap_levels": [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353"
  ]
}
```

Run the build engine with your new theme:

```bash
python scripts/build.py --theme my-theme
```
