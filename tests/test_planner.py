from unittest.mock import MagicMock, patch

from model import PlanModel
from planner import Planner


class TestPlanner:
    def test_call_returns_plan_from_llm(self):
        expected = PlanModel(
            name="AI research plan",
            steps=["Gather sources", "Analyze findings"],
        )
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = expected

        with (
            patch("planner.ChatOpenAI"),
            patch("planner.ChatPromptTemplate.from_messages"),
        ):
            planner = Planner()
            planner.planner_prompt = MagicMock()
            planner.llm = MagicMock()
            planner.planner_prompt.__or__ = MagicMock(return_value=mock_chain)
            planner.llm.with_structured_output = MagicMock(return_value=MagicMock())

            # Rebuild chain mock: planner_prompt | llm.with_structured_output(...)
            chain = MagicMock()
            chain.invoke.return_value = expected
            planner.planner_prompt.__or__.return_value = chain

            result = planner("What is RAG?")

        assert result == expected
        chain.invoke.assert_called_once_with({"task": "What is RAG?"})
