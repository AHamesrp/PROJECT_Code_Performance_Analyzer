"""Simple CLI to analyze a remote repository using existing analyzers.

Usage:
    python scripts/analyze_repo.py --url <repo_url> [--detailed]

"""
import argparse
import logging
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from services.repo_manager import RepoManager
from services.git_analyzer import GitAnalyzer
from services.metrics_calculator import MetricsCalculator
from services.ai_analyzer import AIAnalyzer
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze(url: str, detailed: bool = False):
    repo_manager = RepoManager()

    if not repo_manager.validate_git_url(url):
        logger.error("URL inválida")
        return

    repo = repo_manager.clone_or_update(url)
    git_an = GitAnalyzer()

    repo_info = git_an.get_repository_info(repo)
    commits = git_an.get_commits_with_files(repo, limit=50)

    repo_path = str(repo.working_dir)

    for commit in commits:
        try:
            try:
                repo.git.checkout(commit.get("full_sha") or commit.get("sha"))
            except Exception:
                repo.git.checkout(commit.get("sha"))

            complexity, _ = MetricsCalculator.calculate_complexity(repo_path)
        except Exception:
            complexity = 0.0
        commit["complexity"] = complexity

    from services.non_ai_analyzer import NonAIAnalyzer

    report = NonAIAnalyzer.generate_text_report(commits, repo_info)

    print(report)

    if detailed:
        ai = AIAnalyzer(settings.ANTHROPIC_API_KEY)
        ai_res = ai.analyze_performance_degradation(commits, repo_info)
        print("\n\n=== IA ANALYSIS ===\n")
        print(ai_res.get("analysis"))

    # cleanup
    repo_manager.cleanup(repo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=False, help="URL do repositório git")
    parser.add_argument("--detailed", action="store_true", help="Executa análise detalhada com IA")
    args = parser.parse_args()

    default = "https://github.com/AHamesrp/academia_fabiano_lp.git"
    url = args.url or default

    analyze(url, detailed=args.detailed)
