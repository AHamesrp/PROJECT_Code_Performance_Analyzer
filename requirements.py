"""Instalador de dependências do projeto.

Execute este script com o ambiente virtual ativado para instalar todas as
dependências usadas pelo projeto e forçar a reinstalação quando necessário.
"""

from __future__ import annotations
import subprocess
import sys

DEPENDENCIES = [
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "gitpython==3.1.40",
    "radon==6.0.1",
    "python-dotenv==1.0.0",
    "pydantic==2.13.4",
    "pydantic-settings==2.1.0",
    "requests==2.31.0",
    "numpy==2.4.6",
    "aiofiles==23.2.1",
    "pytest==7.4.3",
    "httpx==0.25.2",
]


def install_dependencies(force: bool = True, upgrade: bool = True) -> None:
    """Instala todas as dependências do projeto."""
    pip_command = [sys.executable, "-m", "pip", "install"]

    if upgrade:
        pip_command.append("--upgrade")
    if force:
        pip_command.append("--force-reinstall")

    pip_command.extend(DEPENDENCIES)

    print("[requirements.py] Instalando dependências do projeto...")
    print("[requirements.py] Comando:", " ".join(pip_command))

    try:
        subprocess.check_call(pip_command)
        print("[requirements.py] Instalação concluída com sucesso.")
    except subprocess.CalledProcessError as exc:
        print("[requirements.py] Erro ao instalar dependências.")
        raise SystemExit(exc.returncode) from exc


if __name__ == "__main__":
    install_dependencies()
