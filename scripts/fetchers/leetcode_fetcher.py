"""LeetCode profile scraper and metrics calculator."""

import json
import sys
from pathlib import Path

# Ensure scripts directory is on sys.path
scripts_dir = Path(__file__).resolve().parent.parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

import requests

from utils.file_utils import ensure_dir, get_project_root, read_json, write_json
from utils.logger import get_logger

logger = get_logger("leetcode_fetcher")


def fetch_leetcode_stats(username: str = "Sg19o") -> Dict[str, Any]:
    """Fetch public LeetCode user statistics via GraphQL/REST API with graceful fallback.

    Args:
        username: LeetCode profile handle.

    Returns:
        Dictionary containing parsed LeetCode metrics.
    """
    root = get_project_root()
    cache_json_path = root / "cache" / "leetcode.json"
    ensure_dir(cache_json_path.parent)

    parsed_stats = {
        "username": username,
        "total_solved": 0,
        "easy_solved": 0,
        "easy_total": 820,
        "medium_solved": 0,
        "medium_total": 1720,
        "hard_solved": 0,
        "hard_total": 730,
        "acceptance_rate": 65.4,
        "ranking": 0,
        "contribution_points": 0,
    }

    # Attempt 1: LeetCode Official GraphQL API
    graphql_url = "https://leetcode.com/graphql"
    query = """
    query userPublicProfile($username: String!) {
      matchedUser(username: $username) {
        username
        profile {
          ranking
          reputation
        }
        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
      allQuestionsCount {
        difficulty
        count
      }
    }
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/",
    }

    fetched_ok = False
    try:
        logger.info(f"Fetching LeetCode statistics for user '{username}'...")
        resp = requests.post(
            graphql_url,
            json={"query": query, "variables": {"username": username}},
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            user_data = data.get("matchedUser")
            all_questions = data.get("allQuestionsCount", [])

            if user_data:
                profile = user_data.get("profile", {})
                parsed_stats["ranking"] = profile.get("ranking", 0)

                sub_nums = user_data.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
                for item in sub_nums:
                    diff = item.get("difficulty")
                    cnt = item.get("count", 0)
                    if diff == "All":
                        parsed_stats["total_solved"] = cnt
                    elif diff == "Easy":
                        parsed_stats["easy_solved"] = cnt
                    elif diff == "Medium":
                        parsed_stats["medium_solved"] = cnt
                    elif diff == "Hard":
                        parsed_stats["hard_solved"] = cnt

                for q in all_questions:
                    diff = q.get("difficulty")
                    cnt = q.get("count", 0)
                    if diff == "Easy":
                        parsed_stats["easy_total"] = cnt
                    elif diff == "Medium":
                        parsed_stats["medium_total"] = cnt
                    elif diff == "Hard":
                        parsed_stats["hard_total"] = cnt

                fetched_ok = True
                logger.info(f"Successfully fetched GraphQL stats for {username}: {parsed_stats['total_solved']} solved.")
    except Exception as err:
        logger.warning(f"GraphQL fetch failed for LeetCode: {err}")

    # Attempt 2: LeetCode REST API fallback
    if not fetched_ok:
        try:
            rest_url = f"https://leetcode-stats-api.herokuapp.com/{username}"
            resp = requests.get(rest_url, timeout=8)
            if resp.status_code == 200:
                res = resp.json()
                if res.get("status") == "success":
                    parsed_stats["total_solved"] = res.get("totalSolved", 0)
                    parsed_stats["easy_solved"] = res.get("easySolved", 0)
                    parsed_stats["medium_solved"] = res.get("mediumSolved", 0)
                    parsed_stats["hard_solved"] = res.get("hardSolved", 0)
                    parsed_stats["acceptance_rate"] = res.get("acceptanceRate", 65.4)
                    parsed_stats["ranking"] = res.get("ranking", 0)
                    fetched_ok = True
                    logger.info("Fetched stats from LeetCode REST API fallback.")
        except Exception as fallback_err:
            logger.warning(f"REST fallback failed for LeetCode: {fallback_err}")

    # Fallback to cached data if network failed
    if not fetched_ok and cache_json_path.exists():
        logger.info("Using cached LeetCode stats...")
        cached_data = read_json(cache_json_path, fallback=None)
        if cached_data:
            return cached_data

    write_json(cache_json_path, parsed_stats)
    return parsed_stats


if __name__ == "__main__":
    fetch_leetcode_stats("Sg19o")
