from unittest.mock import MagicMock, patch

import pytest

from executor import Executor


@pytest.fixture
def executor():
    with (
        patch("executor.load_tools", return_value=[]),
        patch("executor.hub.pull"),
        patch("executor.create_react_agent"),
        patch("executor.ChatOpenAI"),
        patch("executor.AgentExecutor"),
    ):
        ex = Executor()
        ex.ddg_wrapper = MagicMock()
        ex.wiki_wrapper = MagicMock()
        ex.arxiv_tool_runner = MagicMock()
        ex.agent_executor = MagicMock()
        return ex


class TestExecutorSafeRuns:
    def test_safe_ddg_run_returns_result(self, executor):
        executor.ddg_wrapper.run.return_value = "search results"
        assert executor._safe_ddg_run("query") == "search results"

    def test_safe_ddg_run_empty_result_message(self, executor):
        executor.ddg_wrapper.run.return_value = ""
        assert executor._safe_ddg_run("query") == "No search query results found"

    def test_safe_ddg_run_handles_exception(self, executor):
        executor.ddg_wrapper.run.side_effect = RuntimeError("network")
        assert executor._safe_ddg_run("query") == "Search temporarily unavailable"

    def test_safe_wikipedia_run_returns_result(self, executor):
        executor.wiki_wrapper.run.return_value = "wiki page"
        assert executor._safe_wikipedia_run("topic") == "wiki page"

    def test_safe_wikipedia_run_empty_result_message(self, executor):
        executor.wiki_wrapper.run.return_value = None
        assert executor._safe_wikipedia_run("topic") == "No wikipedia query results found"

    def test_safe_wikipedia_run_handles_exception(self, executor):
        executor.wiki_wrapper.run.side_effect = RuntimeError("timeout")
        assert executor._safe_wikipedia_run("topic") == "Wikipedia temporarily unavailable"

    def test_safe_arxiv_run_returns_result(self, executor):
        executor.arxiv_tool_runner.run.return_value = "paper abstract"
        assert executor._safe_arxiv_run("transformers") == "paper abstract"

    def test_safe_arxiv_run_empty_result_message(self, executor):
        executor.arxiv_tool_runner.run.return_value = ""
        assert executor._safe_arxiv_run("query") == "No arXiv query results found"

    def test_safe_arxiv_run_handles_exception(self, executor):
        executor.arxiv_tool_runner.run.side_effect = RuntimeError("arxiv down")
        assert executor._safe_arxiv_run("query") == "arXiv temporarily unavailable"


class TestExecutorCall:
    def test_call_skips_blank_steps(self, executor):
        executor.agent_executor.invoke.return_value = {"output": "done"}

        plan = ["Research topic", "", "   ", "Summarize sources"]
        results = executor(plan)

        assert len(results) == 2
        assert all("\nRESULT: done" in step for step in results)
        assert executor.agent_executor.invoke.call_count == 2

    def test_execute_step_appends_result(self, executor):
        executor.agent_executor.invoke.return_value = {"output": "found data"}

        with patch("executor.logger"):
            result = executor._execute_step(["step 1"], "step 2")

        assert result == "step 2\nRESULT: found data"
        prompt = executor.agent_executor.invoke.call_args[0][0]["input"]
        assert "step 2" in prompt
        assert "STEP: step 1" in prompt
