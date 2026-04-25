from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    Attributes
    ----------
    openai_api_key : str
        API key for OpenAI services.
    openai_planner_model : str
        Model used for planning.
    openai_planner_temperature : float
        Sampling temperature for planner model.
    openai_executor_model : str
        Model used for execution.
    openai_executor_temperature : float
        Sampling temperature for executor model.
    openai_summarizer_model : str
        Model used for summarization.
    openai_summarizer_temperature : float
        Sampling temperature for summarizer model.
    """
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    openai_planner_model: str = Field(default="gpt-4.1-mini", env="OPENAI_PLANNER_MODEL")
    openai_planner_temperature: float = Field(default=0.2, env="OPENAI_PLANNER_TEMPERATURE")

    openai_executor_model: str = Field(default="gpt-4.1-mini", env="OPENAI_EXECUTOR_MODEL")
    openai_executor_temperature: float = Field(default=0.8, env="OPENAI_EXECUTOR_TEMPERATURE")

    openai_summarizer_model: str = Field(
        default="gpt-4.1-mini", env="OPENAI_SUMMARIZER_MODEL"
    )
    openai_summarizer_temperature: float = Field(
        default=0.2, env="OPENAI_SUMMARIZER_TEMPERATURE"
    )

    class Config:
        """
        Pydantic configuration.

        Attributes
        ----------
        env_file : str
            Path to the environment variables file.
        """
        env_file = ".env"


settings = Settings()
