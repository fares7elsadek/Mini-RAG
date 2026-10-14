from .BaseController import BaseController
from fastapi import UploadFile

class DataController(BaseController):

    def __int__(self):
        super().__int__()
        self.size_scale = 1024 * 1024

    
    def validate_uploaded_file(self,file: UploadFile):

        # file type
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False

        # file extension
        if file.filename.split('.')[-1] not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False

        # file size
        if file.size > self.app_settings.FILE_MAX_SIZE_IN_MB * self.size_scale:
            return False

        return True
    