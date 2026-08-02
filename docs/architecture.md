# System Architecture Overview

The profile engine is built as a static site generator for GitHub profile graphics.

```
                  +-----------------------+
                  |     config/*.json     |
                  |     themes/*.json     |
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  |  scripts/build.py     |
                  |  (ConfigManager)      |
                  +-----------+-----------+
                              |
     +------------------------+------------------------+
     |                        |                        |
     v                        v                        v
+----+-------------------+ +--+-------------------+ +--+-------------------+
| processors/photo_proc. | | fetchers/github_proc | | builders/*.py        |
+----+-------------------+ +--+-------------------+ +--+-------------------+
     |                        |                        |
     +------------------------+------------------------+
                              |
                              v
                  +-----------------------+
                  |  assets/generated/*.svg|
                  |  README.md            |
                  +-----------------------+
```

## Core Modules

### 1. Configuration & Theme System
- `config/profile.json`: User profile identity, roles, stacks, socials.
- `config/theme.json`: Theme selector configuration.
- `config/animation.json`: Animation timings (typing, delay, keyframes).
- `config/projects.json`: Project showcases and metadata.
- `themes/*.json`: Multi-theme presets (`github`, `matrix`, `dracula`, `catppuccin`, `nord`, `tokyonight`).

### 2. Utility Layer (`scripts/utils/`)
- `config.py`: Merges JSON configurations into unified Python object.
- `logger.py`: Centralized colored terminal logger.
- `file_utils.py`: Safe JSON and text I/O operations.
- `image_utils.py`: Image loading, contrast enhancement, ASCII conversion.
- `svg_utils.py`: Terminal window frame builder and SVG minifier.

### 3. Builders (`scripts/builders/`)
- `ascii_builder.py`: Renders monochrome row-by-row animated ASCII art SVG.
- `banner_builder.py`: Renders Linux prompt command typewriter header SVG.
- `card_builder.py`: Renders Linux `neofetch` info card SVG.
- `contribution_builder.py`: Scrapes and renders diagonal-reveal contribution graph SVG.
- `skills_builder.py`: Renders category matrix skill boxes SVG.
- `project_builder.py`: Renders terminal-styled project card SVGs.
- `readme_builder.py`: Assembles centered `README.md` document referencing all generated assets.

### 4. Validation & Automation (`scripts/validators/` & `.github/workflows/`)
- `validate.py`: Pre-flight configuration checker and SVG XML syntax validator.
- `update-profile.yml`: Daily cron workflow for automated commit & push.
