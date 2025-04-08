from pathlib import Path
from dotenv import load_dotenv
import os

class EnvHelper:
    """Helper class to manage .env file loading across multiple files."""

    _env_loaded = False

    @staticmethod
    def get_env_path():
        env_mode = os.getenv("ENV_MODE", "dev").lower()
        env_file_name = ".env.prod" if env_mode == "prod" else ".env.local"

        """Returns the absolute path to the .env file."""

        current_dir = Path.cwd()
        while current_dir.parent != current_dir:
            env_file = current_dir / env_file_name
            if env_file.exists():
                return str(env_file)
            current_dir = current_dir.parent
        raise FileNotFoundError("Keine .env Datei gefunden")

    @classmethod
    def load_env(cls):
        if not cls._env_loaded:
            env_path = cls.get_env_path()
            load_dotenv(env_path)
            cls._env_loaded = True
        return os.environ

    @classmethod
    def get_env_var(cls, key, default=None):
        cls.load_env()
        return os.environ.get(key, default)

