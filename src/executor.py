from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools import ArxivQueryRun
from prompts import executor_prompt_template
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
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
    agent_executor : AgentExecutor
        Configured LangChain executor responsible for running the agent.
    ddg_wrapper : DuckDuckGoSearchAPIWrapper
        Wrapper for DuckDuckGo search API.
    wiki_wrapper : WikipediaAPIWrapper
        Wrapper for Wikipedia API.
    arxiv_tool_runner : ArxivQueryRun
        Tool interface for querying arXiv.
    """

    def __init__(self):
        """
        Initialize the Executor with LLM, tools, and agent configuration.
        """
        llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_executor_model,
            temperature=settings.openai_executor_temperature,
        )

        tools = load_tools(tool_names=["llm-math"], llm=llm)

        # create duckduckgo search tool with safe run
        self.ddg_wrapper = DuckDuckGoSearchAPIWrapper()

        ddg_tool = Tool(
            name="ddg-search",
            func=self._safe_ddg_run,
            description="Search the web using DuckDuckGo. Input should be a search query.",
        )
        tools.append(ddg_tool)

        # create wikipedia tool with safe run
        self.wiki_wrapper = WikipediaAPIWrapper()

        wiki_tool = Tool(
            name="wikipedia",
            func=self._safe_wikipedia_run,
            description="Search Wikipedia for general knowledge. Input should be a search query.",
        )
        tools.append(wiki_tool)

        # create arxiv tool with safe run
        arxiv_wrapper = ArxivAPIWrapper(top_k_results=3)

        self.arxiv_tool_runner = ArxivQueryRun(api_wrapper=arxiv_wrapper)

        arxiv_tool = Tool(
            name="arxiv",
            func=self._safe_arxiv_run,
            description="Search scientific papers on arXiv. Input should be a research query.",
        )
        tools.append(arxiv_tool)

        # create react agent
        react_prompt = hub.pull("hwchase17/react")

        agent = create_react_agent(llm, tools, react_prompt)

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,  # executor sometimes falls into endless loops for some reason, better not remove this
            handle_parsing_errors=True,
        )

    def __call__(self, plan):
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

    def _safe_ddg_run(self, query):
        """
        Safely executes duckduckgo query with fallbacks.

        Parameters
        ----------
        query : str
            Search query for DuckDuckGo API.

        Returns
        -------
        str
            Result of the query.
        """
        try:
            result = self.ddg_wrapper.run(query)
            return result if result else "No search query results found"
        except Exception:
            return "Search temporarily unavailable"

    def _safe_wikipedia_run(self, query):
        """
        Safely executes wikipedia query with fallbacks.

        Parameters
        ----------
        query : str
            Search query for wikipedia API.

        Returns
        -------
        str
            Result of the query.
        """
        try:
            result = self.wiki_wrapper.run(query)
            return result if result else "No wikipedia query results found"
        except Exception:
            return "Wikipedia temporarily unavailable"

    def _safe_arxiv_run(self, query):
        """
        Safely executes arxiv query with fallbacks.

        Parameters
        ----------
        query : str
            Search query for arxiv API.

        Returns
        -------
        str
            Result of the query.
        """
        try:
            result = self.arxiv_tool_runner.run(query)
            return result if result else "No arXiv query results found"
        except Exception:
            return "arXiv temporarily unavailable"

    def _execute_step(self, plan, step):
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
        input_ = executor_prompt_template.format(
            plan="STEP: " + "\nSTEP: ".join(plan), step=step
        )

        logger("Passed prompt to executor: " + input_)

        result = self.agent_executor.invoke({"input": input_})

        logger("Executor's final answer: " + result["output"])

        return step + "\nRESULT: " + result["output"]
