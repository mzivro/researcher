import pytest
from pydantic import ValidationError

from settings import Settings


class TestSettings:
    def test_valid_defaults(self):
        settings = Settings(openai_api_key="sk-test-key")
        assert settings.openai_planner_model == "gpt-4.1-mini"
        assert settings.openai_planner_temperature == 0.0
        assert settings.openai_executor_model == "gpt-4.1-mini"
        assert settings.openai_summarizer_model == "gpt-4.1-mini"

    def test_strips_api_key(self):
        settings = Settings(openai_api_key="  sk-test-key  ")
        assert settings.openai_api_key == "sk-test-key"

    @pytest.mark.parametrize(
        "field,value",
        [
            ("openai_planner_temperature", -0.1),
            ("openai_planner_temperature", 2.1),
            ("openai_executor_temperature", -0.1),
            ("openai_executor_temperature", 2.1),
            ("openai_summarizer_temperature", -0.1),
            ("openai_summarizer_temperature", 2.1),
        ],
    )
    def test_temperature_out_of_range(self, field, value):
        with pytest.raises(ValidationError):
            Settings(openai_api_key="sk-test", **{field: value})

    @pytest.mark.parametrize(
        "field,value",
        [
            ("openai_planner_temperature", 0.0),
            ("openai_planner_temperature", 2.0),
            ("openai_executor_temperature", 1.5),
            ("openai_summarizer_temperature", 0.5),
        ],
    )
    def test_temperature_in_range(self, field, value):
        settings = Settings(openai_api_key="sk-test", **{field: value})
        assert getattr(settings, field) == value

    def test_empty_api_key_rejected(self):
        with pytest.raises(ValidationError, match="No OpenAI API key"):
            Settings(openai_api_key="   ")

    def test_custom_models(self):
        settings = Settings(
            openai_api_key="sk-test",
            openai_planner_model="gpt-4o",
            openai_executor_model="gpt-4o-mini",
            openai_summarizer_model="gpt-4.1",
        )
        assert settings.openai_planner_model == "gpt-4o"
        assert settings.openai_executor_model == "gpt-4o-mini"
        assert settings.openai_summarizer_model == "gpt-4.1"
