from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
from controllers.ProjectController import ProjectController
import os
import re

class DataController(BaseController):

    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024

    
    def validate_uploaded_file(self,file: UploadFile):
        
        # file type
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        # file extension
        if file.filename.split('.')[-1] not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        # file size
        if file.size > self.app_settings.FILE_MAX_SIZE_IN_MB * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VLAIDATED_SUCCESSFULLY.value

    def get_unique_file_name(self,filename: str, project_id: str):

        random_file_name = self.generate_random_string()
        project_path = ProjectController.get_project_path(project_id=project_id)

        final_file_path = os.path.join(
            project_path,
            random_file_name + "_" + self.remove_special_characters(filename)
        )

        while os.path.exists(final_file_path):
            random_file_name = self.generate_random_string()
            final_file_path = os.path.join(
                project_path,
                random_file_name + "_" + self.remove_special_characters(filename)
            )

        return final_file_path, random_file_name + "_" + self.remove_special_characters(filename)


    def remove_special_characters(self, text: str):
            return re.sub(r'[^a-zA-Z0-9_.]', '', text)