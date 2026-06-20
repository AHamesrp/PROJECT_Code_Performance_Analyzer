import hashlib
import logging
from pathlib import Path
import shutil
import tempfile
import re
from git import Repo, GitCommandError
from typing import Optional

logger = logging.getLogger(__name__)


class RepoManager:
    """Gerencia clonagem e atualização de repositórios remotos."""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path.cwd() / "_repos"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _normalize_repo_name(self, url: str) -> str:
        name = url.split("/")[-1].replace('.git', '')
        return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)

    def _link_path_for_url(self, url: str) -> Path:
        name = self._normalize_repo_name(url)
        url_hash = hashlib.sha1(url.encode('utf-8')).hexdigest()[:8]
        return self.base_dir / f"{name}_{url_hash}.txt"

    def save_repo_link(self, url: str):
        link_path = self._link_path_for_url(url)
        if not link_path.exists():
            link_path.write_text(url + "\n", encoding="utf-8")

    def _create_temp_clone_dir(self) -> Path:
        temp_dir = tempfile.mkdtemp(prefix="repo_clone_")
        return Path(temp_dir)

    def clone_or_update(self, url: str, force_clone: bool = False) -> Repo:
        """Salva somente o link do repositório e faz clone temporário para análise."""
        self.save_repo_link(url)
        repo_path = self._create_temp_clone_dir()

        try:
            logger.info(f"Clonando {url} em {repo_path}")
            repo = Repo.clone_from(url, to_path=str(repo_path))
            return repo
        except GitCommandError as e:
            logger.error(f"Erro ao clonar {url}: {e}")
            self._remove_path(repo_path)
            raise

    def validate_git_url(self, url: str) -> bool:
        """Valida uma URL básica de git (.git ou github/gitlab ssh/http)"""
        if not url or not isinstance(url, str):
            return False
        return url.endswith('.git') or url.startswith('git@') or 'github.com' in url or 'gitlab.com' in url

    def cleanup(self, repo: Repo):
        try:
            if hasattr(repo, 'close'):
                repo.close()
        except Exception:
            pass

        path = Path(repo.working_dir)
        if path.exists():
            self._remove_path(path)

    def _force_chmod(self, path: Path):
        for root, dirs, files in __import__("os").walk(path, topdown=False):
            for name in files:
                filepath = Path(root) / name
                try:
                    filepath.chmod(0o777)
                except Exception:
                    pass
            for name in dirs:
                dirpath = Path(root) / name
                try:
                    dirpath.chmod(0o777)
                except Exception:
                    pass

    def _remove_path(self, path: Path):
        def on_rm_error(func, p, exc_info):
            try:
                p.chmod(0o777)
            except Exception:
                pass
            try:
                func(p)
            except Exception as exc:
                logger.warning(f"Erro ao remover {p} na segunda tentativa: {exc}")

        try:
            self._force_chmod(path)
            shutil.rmtree(path, onerror=on_rm_error)
            if path.exists():
                raise OSError(f"Path still exists after initial removal: {path}")
            logger.info(f"Removido {path}")
            return
        except Exception as e:
            logger.warning(f"Primeira tentativa de remoção falhou para {path}: {e}")

        if __import__("os").name == "nt":
            try:
                import subprocess
                subprocess.run(["cmd", "/c", "rmdir", "/s", "/q", str(path)], check=False, shell=False)
            except Exception as exc:
                logger.warning(f"Falha ao remover {path} com rmdir: {exc}")
        else:
            try:
                import subprocess
                subprocess.run(["rm", "-rf", str(path)], check=False, shell=False)
            except Exception as exc:
                logger.warning(f"Falha ao remover {path} com rm -rf: {exc}")

        if path.exists():
            logger.warning(f"Diretório ainda existe após tentativas de remoção: {path}")
        else:
            logger.info(f"Removido {path} após tentativa de fallback")
