import logging
import os
import secrets
import re

from helper.config import get_settings, Settings

logger = logging.getLogger(__name__)


class BaseController:

    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_dir, "assets/files")

        self.database_dir = os.path.join(self.base_dir, "assets/databases")

    def generate_random_string(self, length: int = 12) -> str:
        """Generate a URL-safe random string (cryptographically secure)."""
        return secrets.token_urlsafe(length)[:length]

    @staticmethod
    def sanitize_path_component(value: str) -> str:
        """Validate that a path component contains only safe characters.

        Prevents path traversal attacks when building file system paths
        from user-supplied values (e.g. project_id).
        """
        if not re.match(r'^[a-zA-Z0-9_\-]+$', value):
            raise ValueError(f"Invalid path component: '{value}'")
        return value

    def get_database_path(self, db_name) -> str:
        database_path = os.path.join(
            self.database_dir, db_name
        )

        if not os.path.exists(database_path):
            os.makedirs(database_path)

        return database_path