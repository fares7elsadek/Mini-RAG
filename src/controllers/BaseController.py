from helper.config import get_settings, Settings
import os
import string
import random
import re

class BaseController:

    def __int__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_dir,"assets/files")


    def generate_random_string(length: int = 10) -> str:
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))


    def remove_special_characters(text: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_.]', '', text)