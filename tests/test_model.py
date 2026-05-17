import pytest

from model import PlanModel


class TestPlanModel:
    def test_valid_plan(self):
        plan = PlanModel(name="Research AI safety", steps=["Search papers", "Compare findings"])
        assert plan.name == "Research AI safety"
        assert len(plan.steps) == 2

    def test_serialization_roundtrip(self):
        plan = PlanModel(name="Test plan", steps=["Step A", "Step B"])
        data = plan.model_dump()
        restored = PlanModel.model_validate(data)
        assert restored == plan

    def test_requires_name_and_steps(self):
        with pytest.raises(Exception):
            PlanModel(steps=["only steps"])
