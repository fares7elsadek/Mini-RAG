from helper.config import get_settings, Settings


class BaseController:

    def __int__(self):
        self.app_settings = get_settings()