"""Configuration loading from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    """Bot configuration loaded from environment variables."""
    
    bot_token: str
    lms_api_url: str
    lms_api_key: str
    llm_api_key: str
    llm_api_base_url: str
    llm_api_model: str
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.
        
        Loads .env.bot.secret from the bot/ directory if it exists.
        
        Returns:
            Config instance with loaded values.
            
        Raises:
            ValueError: If required environment variables are missing.
        """
        # Load .env.bot.secret from bot/ directory
        env_path = Path(__file__).parent / ".env.bot.secret"
        if env_path.exists():
            load_dotenv(env_path)
        
        bot_token = os.getenv("BOT_TOKEN")
        lms_api_url = os.getenv("LMS_API_URL")
        lms_api_key = os.getenv("LMS_API_KEY")
        llm_api_key = os.getenv("LLM_API_KEY")
        llm_api_base_url = os.getenv("LLM_API_BASE_URL")
        llm_api_model = os.getenv("LLM_API_MODEL")
        
        # Validate required variables
        missing = []
        if not bot_token:
            missing.append("BOT_TOKEN")
        if not lms_api_url:
            missing.append("LMS_API_URL")
        if not lms_api_key:
            missing.append("LMS_API_KEY")
        if not llm_api_key:
            missing.append("LLM_API_KEY")
        if not llm_api_base_url:
            missing.append("LLM_API_BASE_URL")
        if not llm_api_model:
            missing.append("LLM_API_MODEL")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return cls(
            bot_token=bot_token,
            lms_api_url=lms_api_url,
            lms_api_key=lms_api_key,
            llm_api_key=llm_api_key,
            llm_api_base_url=llm_api_base_url,
            llm_api_model=llm_api_model,
        )


# Global config instance (lazy-loaded)
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance.
    
    Returns:
        Config instance loaded from environment variables.
    """
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
