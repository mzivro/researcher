from pydantic import ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    Raises
    ------
    ValueError
        If any configuration parameter is invalid.
    """

    openai_api_key: str

    openai_planner_model: str = "gpt-4.1-mini"
    openai_planner_temperature: float = 0.0

    openai_executor_model: str = "gpt-4.1-mini"
    openai_executor_temperature: float = 0.0

    openai_summarizer_model: str = "gpt-4.1-mini"
    openai_summarizer_temperature: float = 0.0

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @field_validator("openai_api_key")
    def validate_openai_api_key(cls, v):
        """
        Validate OpenAI API key.

        Parameters
        ----------
        v : str
            API key string.

        Returns
        -------
        str
            Stripped API key.

        Raises
        ------
        ValueError
            If API key is empty.
        """
        v = v.strip()
        if not v:
            raise ValueError("No OpenAI API key provided")
        return v

    @field_validator("openai_planner_temperature")
    def validate_openai_planner_temperature(cls, v):
        """
        Validate planner temperature.

        Parameters
        ----------
        v : float
            Planner temperature.

        Returns
        -------
        float
            Validated planner temperature.

        Raises
        ------
        ValueError
            If planner temperature is not in range.
        """
        if 0.0 <= v <= 2.0:
            return v
        raise ValueError("Planner temperature must be in <0; 2> range")

    @field_validator("openai_executor_temperature")
    def validate_openai_executor_temperature(cls, v):
        """
        Validate executor temperature.

        Parameters
        ----------
        v : float
            Executor temperature.

        Returns
        -------
        float
            Validated executor temperature.

        Raises
        ------
        ValueError
            If executor temperature is not in range.
        """
        if 0.0 <= v <= 2.0:
            return v
        raise ValueError("Executor temperature must be in <0; 2> range")

    @field_validator("openai_summarizer_temperature")
    def validate_openai_summarizer_temperature(cls, v):
        """
        Validate executor temperature.

        Parameters
        ----------
        v : float
            Summarizer temperature.

        Returns
        -------
        float
            Validated summarizer temperature.

        Raises
        ------
        ValueError
            If summarizer temperature is not in range.
        """
        if 0.0 <= v <= 2.0:
            return v
        raise ValueError("Summarizer temperature must be in <0; 2> range")


try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Invalid configuration:\n{e}") from e
