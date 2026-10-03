from prepza_common.user import Language
from pydantic import BaseModel


class SettingsIn(BaseModel):
    language: Language
