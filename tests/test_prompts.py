from prompts import (
    executor_prompt_template,
    planner_prompt_template,
    summarizer_prompt_template,
)


class TestPrompts:
    def test_planner_prompt_defines_role(self):
        assert "Research Planner" in planner_prompt_template
        assert "planning" in planner_prompt_template.lower()

    def test_executor_prompt_has_placeholders(self):
        assert "{plan}" in executor_prompt_template
        assert "{step}" in executor_prompt_template
        formatted = executor_prompt_template.format(plan="p", step="s")
        assert "p" in formatted
        assert "s" in formatted

    def test_summarizer_prompt_requires_markdown(self):
        assert "Markdown" in summarizer_prompt_template
        assert "# Final Answer" in summarizer_prompt_template
