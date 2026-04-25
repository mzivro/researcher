from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI
from langchain_classic import hub
from settings import settings
from logger import logger


class Executor:
    """
    Executes a research plan step-by-step using a ReAct agent.

    This class wraps a LangChain agent configured with multiple tools
    (search, arXiv, Wikipedia, math) and applies it iteratively to each
    step of a research plan.

    Attributes
    ----------
    executor_prompt_template : str
        Template used to instruct the agent how to execute each step.
    agent_executor : AgentExecutor
        Configured LangChain executor responsible for running the agent.
    """
    def __init__(self):
        """
        Initialize the Executor with LLM, tools, and agent configuration.
        """
        self.executor_prompt_template = (
            "You're a seasoned research plan executioner, "
            "which executes steps of research plans.\n\n"
            "This is whole plan with results:\n"
            "{plan}\n\n"
            "This is current step:\n"
            "{step}\n\n"
            "Execute the current step - if step description "
            "is not understandable, just write 'None'\n"
            "Make sure to add sources to answer.\n"
        )

        llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_executor_model,
            temperature=settings.openai_executor_temperature,
        )

        tools = load_tools(
            tool_names=["ddg-search", "arxiv", "wikipedia", "llm-math"], llm=llm
        )

        prompt = hub.pull("hwchase17/react")

        agent = create_react_agent(llm, tools, prompt)

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=4,
            handle_parsing_errors=True,
        )

    def __call__(self, plan: list[str]) -> list[str]:
        """
        Execute all steps in the provided plan.

        Parameters
        ----------
        plan : list of str
            List of textual steps describing the research plan.

        Returns
        -------
        list of str
            List of steps augmented with execution results.
        """
        plan_with_results = []

        for i, step in enumerate(plan):
            if step.strip() == "":
                continue

            plan[i] = self._execute_step(plan, step)

            plan_with_results.append(plan[i])

        return plan_with_results

    def _execute_step(self, plan: list[str], step: str) -> str:
        """
        Execute a single step of the plan.

        Parameters
        ----------
        plan : list of str
            Full plan context including previous steps and results.
        step : str
            Current step to execute.

        Returns
        -------
        str
            Step description combined with execution result.
        """
        input_ = self.executor_prompt_template.format(
            plan="\nSTEP: ".join(plan), step=step
        )

        logger("Passed prompt to executor: " + input_)

        result = self.agent_executor.invoke({"input": input_})

        logger("Executor's final answer: " + result["output"])

        return step + "\nRESULT: " + result["output"]
