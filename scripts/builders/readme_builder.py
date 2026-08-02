"""Master README.md Document Builder."""

from pathlib import Path
from typing import TYPE_CHECKING, Dict

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.logger import get_logger

if TYPE_CHECKING:
    from utils.config import ConfigManager

logger = get_logger("readme_builder")


def build_readme_file(config_mgr: "ConfigManager") -> Path:
    """Generate minimal production-ready centered terminal README.md document.

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

    github_url = socials.get('github', 'https://github.com/sgo453071-arch')
    linkedin_url = socials.get('linkedin', 'https://www.linkedin.com/in/sg19o/')
    leetcode_url = socials.get('leetcode', 'https://leetcode.com/u/Sg19o/')
    email_url = f"mailto:{socials.get('email', 'sgo453071@gmail.com')}"

    readme_content = f"""<div align="center">

<!-- SECTION 1: LEETCODE CALENDAR HEATMAP (AT TOP) -->
<a href="{leetcode_url}" target="_blank">
  <img src="assets/generated/leetcode-heatmap.svg" alt="Animated LeetCode Submission Heatmap" width="800"/>
</a>

<br/><br/>

<!-- SECTION 2: GITHUB CONTRIBUTIONS HEATMAP -->
<a href="{github_url}">
  <img src="assets/generated/contribution-graph.svg" alt="Animated GitHub Contribution Heatmap" width="800"/>
</a>

<br/><br/>

<!-- SECTION 3: WHOAMI (HD DEVELOPER PORTRAIT + NEOFETCH INFO CARD) -->
<table border="0" cellspacing="0" cellpadding="0" style="border: none; border-collapse: collapse;">
  <tr style="border: none;">
    <td align="center" valign="top" style="border: none; padding: 4px;">
      <a href="{github_url}">
        <img src="assets/source-prepped.png" alt="Developer HD Portrait" width="390" style="border-radius: 8px;"/>
      </a>
    </td>
    <td align="center" valign="top" style="border: none; padding: 4px;">
      <a href="{linkedin_url}">
        <img src="assets/generated/info-card.svg" alt="Neofetch Info Card" width="390"/>
      </a>
    </td>
  </tr>
</table>

<br/><br/>

<!-- SECTION 4: SOCIAL CONNECT BADGES -->
<p align="center">
  <a href="{github_url}" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
  </a>
  &nbsp;
  <a href="{linkedin_url}" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
  </a>
  &nbsp;
  <a href="{leetcode_url}" target="_blank">
    <img src="https://img.shields.io/badge/LeetCode-FFA116?style=for-the-badge&logo=leetcode&logoColor=black" alt="LeetCode"/>
  </a>
  &nbsp;
  <a href="{email_url}">
    <img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/>
  </a>
</p>

</div>
"""

    write_text(readme_path, readme_content)
    logger.info(f"Built master README.md -> {readme_path}")
    return readme_path
