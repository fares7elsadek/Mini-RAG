import logging
import os
import re

from fastapi import UploadFile

from .BaseController import BaseController
from controllers.ProjectController import ProjectController
from models import ResponseSignal

logger = logging.getLogger(__name__)


class DataController(BaseController):

    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024

    def validate_uploaded_file(self, file: UploadFile) -> tuple[bool, str]:
        """Validate file type, extension, and size against app settings."""

        # file type
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        # file extension – guard against filenames without an extension
        filename = file.filename or ""
        if "." not in filename:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if filename.rsplit(".", 1)[-1].lower() not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        # file size
        if file.size is not None and file.size > self.app_settings.FILE_MAX_SIZE_IN_MB * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATED_SUCCESSFULLY.value

    def get_unique_file_name(self, filename: str, project_id: str) -> tuple[str, str]:
        """Return (full_path, file_id) with a collision-free random prefix."""

        # Sanitize project_id before using in path
        safe_project_id = self.sanitize_path_component(project_id)
        project_path = ProjectController.get_project_path(project_id=safe_project_id)

        random_file_name = self.generate_random_string()
        clean_filename = self._remove_special_characters(filename)
        file_id = f"{random_file_name}_{clean_filename}"

        final_file_path = os.path.join(project_path, file_id)

        while os.path.exists(final_file_path):
            random_file_name = self.generate_random_string()
            file_id = f"{random_file_name}_{clean_filename}"
            final_file_path = os.path.join(project_path, file_id)

        return final_file_path, file_id 

    @staticmethod
    def _remove_special_characters(text: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_.]', '', text)

    @staticmethod
    def _remove_file(file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except OSError:
            logger.exception("Failed to delete file: %s", file_path)
            return False