
import os
from pathlib import Path
from git import Repo

def git_push(repo_path, message: str):
    # Detecta raíz del repo si no se pasa
    if not repo_path:
        repo_path = str(Path(__file__).resolve().parents[1])
    repo = Repo(repo_path)
    if repo.is_dirty(untracked_files=True):
        repo.git.add(A=True)  # add all
        try:
            repo.index.commit(message)
        except Exception:
            pass
        remote_name = os.getenv("REMOTE_NAME", "origin")
        branch = os.getenv("BRANCH", "main")
        origin = repo.remote(remote_name)
        origin.push(branch)
        return True
    return False
