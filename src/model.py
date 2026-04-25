from pydantic import BaseModel, Field


class PlanModel(BaseModel):
    """
    Data model representing a research plan.

    Attributes
    ----------
    name : str
        General name or description of the plan.
    steps : list of str
        Ordered list of steps required to complete the task.
    """
    name: str = Field(description="General name of the plan")
    steps: list[str] = Field(
        description="Different steps to follow, should be in sorted order."
    )
