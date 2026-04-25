from langchain_core.prompts import ChatPromptTemplate
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
    llm : ChatOpenAI
        Language model used for plan generation.
    planner_prompt_template : str
        System prompt guiding plan generation behavior.
    """
    def __init__(self):
        """
        Initialize the Planner with configured LLM and prompt template.
        """
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_planner_model,
            temperature=settings.openai_planner_temperature,
        )

        self.planner_prompt_template = (
            "You're a research planner, which create plans for "
            "research tasks.\n"
            "For the given task, come up with a step by step plan.\n"
            "This plan should involve individual tasks, that if executed correctly will "
            "yield the correct answer. Do not add any superfluous steps.\n"
            "The result of the final step should be the final answer. Make sure that each "
            "step has all the information needed - do not skip any steps except the summary steps.\n"
        )

    def __call__(self, task: str):
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
        planner_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.planner_prompt_template),
                (
                    "user",
                    "Prepare a plan of how to solve the following task:\n{task}\n",
                ),
            ]
        )

        planner = planner_prompt | self.llm.with_structured_output(PlanModel)

        return planner.invoke({"task": task})
