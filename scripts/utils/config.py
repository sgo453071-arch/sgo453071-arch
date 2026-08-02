"""Configuration loader and manager."""

from pathlib import Path
from typing import Any, Dict, Optional

from .file_utils import get_project_root, read_json
from .logger import get_logger

logger = get_logger("config_loader")


class ConfigManager:
    """Singleton configuration loader managing profile, themes, animation, and project settings."""

    def __init__(self, theme_override: Optional[str] = None):
        self.root = get_project_root()
        self.profile = read_json(self.root / "config" / "profile.json", fallback={})
        self.animation = read_json(self.root / "config" / "animation.json", fallback={})
        self.projects = read_json(self.root / "config" / "projects.json", fallback=[])

        # Determine theme name
        theme_pointer = read_json(self.root / "config" / "theme.json", fallback={"active_theme": "github"})
        theme_name = theme_override or theme_pointer.get("active_theme", "github")

        theme_file = self.root / "themes" / f"{theme_name}.json"
        if not theme_file.exists():
            logger.warning(f"Theme '{theme_name}' not found at {theme_file}, falling back to 'github'")
            theme_file = self.root / "themes" / "github.json"

        self.theme = read_json(theme_file, fallback={})
        self.theme_name = theme_name
        logger.info(f"Loaded active theme: '{self.theme.get('name', theme_name)}'")

    def get_username(self) -> str:
        return self.profile.get("username", "sgo453071-arch")

    def get_name(self) -> str:
        return self.profile.get("name", "Shourya")
