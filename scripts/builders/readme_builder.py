"""Master README.md Document Builder."""

from pathlib import Path
from typing import Dict

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.logger import get_logger

logger = get_logger("readme_builder")


def build_readme_file(config_mgr: "ConfigManager") -> Path:
    """Generate production-ready centered terminal README.md document using verified real details.

    Args:
        config_mgr: ConfigManager instance.

    Returns:
        Path to output README.md file.
    """
    root = get_project_root()
    readme_path = root / "README.md"

    prof = config_mgr.profile
    username = config_mgr.get_username()
    socials = prof.get("socials", {})

    readme_content = f"""<div align="center">

<!-- Terminal Header Banner -->
<img src="assets/generated/terminal-banner.svg" alt="Terminal Header Banner" width="800"/>

<br/><br/>

<!-- SECTION 1: CONTRIBUTIONS -->
<h3><code>{username}@github ~ $ ./contributions.sh</code></h3>

<img src="assets/generated/contribution-graph.svg" alt="Animated Contribution Heatmap" width="800"/>

<br/><br/>

<!-- SECTION 2: WHOAMI (ASCII PORTRAIT + NEOFETCH INFO CARD) -->
<h3><code>{username}@github ~ $ whoami</code></h3>

<table border="0" cellspacing="0" cellpadding="0" style="border: none; border-collapse: collapse;">
  <tr style="border: none;">
    <td align="center" valign="top" style="border: none; padding: 4px;">
      <img src="assets/generated/ascii-profile.svg" alt="ASCII Portrait" width="390"/>
    </td>
    <td align="center" valign="top" style="border: none; padding: 4px;">
      <img src="assets/generated/info-card.svg" alt="Neofetch Info Card" width="390"/>
    </td>
  </tr>
</table>

<br/><br/>

<!-- SECTION 3: PROJECTS SHOWCASE -->
<h3><code>{username}@github ~ $ ls -l ./projects/</code></h3>

<table border="0" cellspacing="0" cellpadding="0" style="border: none; border-collapse: collapse;">
  <tr style="border: none;">
    <td align="center" valign="top" style="border: none; padding: 4px;">
      <a href="{socials.get('github', '#')}">
        <img src="assets/generated/project-disha.svg" alt="DISHA FOR INDIA Card" width="380"/>
      </a>
    </td>
    <td align="center" valign="top" style="border: none; padding: 4px;">
      <a href="{socials.get('github', '#')}">
        <img src="assets/generated/project-ai.svg" alt="Future AI Projects Card" width="380"/>
      </a>
    </td>
  </tr>
  <tr style="border: none;">
    <td align="center" colspan="2" valign="top" style="border: none; padding: 4px;">
      <a href="{socials.get('github', '#')}">
        <img src="assets/generated/project-portfolio.svg" alt="Portfolio Engine Card" width="380"/>
      </a>
    </td>
  </tr>
</table>

<br/><br/>

<!-- SECTION 4: SKILLS MATRIX -->
<h3><code>{username}@github ~ $ cat ./skills.json</code></h3>

<img src="assets/generated/skills.svg" alt="Skills Matrix" width="800"/>

<br/><br/>

<!-- SECTION 5: SOCIAL CONNECT & FOOTER -->
<h3><code>{username}@github ~ $ cat ./socials.txt</code></h3>

<p align="center">
  <a href="{socials.get('github', '#')}">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
  </a>
  &nbsp;
  <a href="{socials.get('linkedin', '#')}">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
  </a>
  &nbsp;
  <a href="{socials.get('leetcode', '#')}">
    <img src="https://img.shields.io/badge/LeetCode-FFA116?style=for-the-badge&logo=leetcode&logoColor=black" alt="LeetCode"/>
  </a>
  &nbsp;
  <a href="mailto:{socials.get('email', '')}">
    <img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/>
  </a>
</p>

<br/>

<hr width="800"/>

<p align="center">
  <sub>⚡ Handcrafted locally with Python, OpenCV &amp; SVG. Zero third-party profile widgets. Automated via GitHub Actions.</sub>
</p>

</div>
"""

    write_text(readme_path, readme_content)
    logger.info(f"Built master README.md -> {readme_path}")
    return readme_path
