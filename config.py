from pydantic_settings import BaseSettings

class SalamanderConfig(BaseSettings):
    block_threshold: int = 45
    suspicious_threshold: int = 25
    enable_ml: bool = True
    enable_chinese: bool = True
    enable_english: bool = True
    custom_patterns_path: str | None = None
    model_path: str = "data/models/model.joblib"

    class Config:
        env_prefix = "SALAMANDER_"
