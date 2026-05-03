from langchain_core.prompts import ChatPromptTemplate
from prompts import planner_prompt_template
from langchain_openai import ChatOpenAI
from settings import settings
from model import PlanModel


class Planner:
    """
    Generates structured research plans using an LLM.

    This class uses a prompt template and structured output parsing
    to produce a PlanModel instance for a given task.

    Attributes
    ----------
    planner_prompt : ChatPromptTemplate
        Prompt template defining system and user instructions for plan generation.
    llm : ChatOpenAI
        Language model used for plan generation.
    """

    def __init__(self):
        """
        Initialize the Planner with configured LLM and prompt template.
        """
        self.planner_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", planner_prompt_template),
                (
                    "user",
                    "Prepare a plan of how to solve the following task:\n{task}\n",
                ),
            ]
        )

        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_planner_model,
            temperature=settings.openai_planner_temperature,
        )

    def __call__(self, task):
        """
        Generate a plan for a given task.

        Parameters
        ----------
        task : str
            Description of the research task.

        Returns
        -------
        PlanModel
            Structured plan containing name and ordered steps.
        """
        planner = self.planner_prompt | self.llm.with_structured_output(PlanModel)

        return planner.invoke({"task": task})
