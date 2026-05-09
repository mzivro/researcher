from streamlit_pdf_viewer import pdf_viewer
from summarizer import Summarizer
from executor import Executor
from planner import Planner
from logger import logger

import streamlit as st
import pandas as pd


class Researcher:
    """
    Main Streamlit application orchestrating the research workflow.

    This class coordinates planning, editing, execution, and summarization
    of research tasks using session state.

    Methods
    -------
    run()
        Launch the application UI.
    """

    def __init__(self):
        """
        Initialize application state and required components.

        Sets up session state variables including planner, executor,
        summarizer, and plan data.
        """
        if "plan" not in st.session_state:
            num = 3

            st.session_state.plan = pd.DataFrame(
                {"Plan": [f"Step {i}" for i in range(num)]}
            )

        if "plan_name" not in st.session_state:
            st.session_state.plan_name = "Custom plan"

        if "plan_with_results" not in st.session_state:
            st.session_state.plan_with_results = None

        if "ready" not in st.session_state:
            st.session_state.ready = False

        if "planner" not in st.session_state:
            st.session_state.planner = Planner()

        if "executor" not in st.session_state:
            st.session_state.executor = Executor()

        if "summarizer" not in st.session_state:
            st.session_state.summarizer = Summarizer()

    def run(self):
        """
        Run the full application workflow.

        Executes planner input, plan editing, and summarization sections.
        """
        self._planner_section()
        self._plan_editor_section()
        self._summary_section()

    def _planner_section(self):
        """
        Render and handle the planner input UI section.

        Allows the user to define a task and generate a plan.
        """
        task = st.text_input(
            "Enter your task",
            help="Write some task which researcher should resolve",
        )

        if st.button("Create plan", width="stretch"):
            plan = st.session_state.planner(task)

            st.session_state.plan_name = plan.name

            st.session_state.plan = pd.DataFrame(
                {
                    "Plan": plan.steps,
                }
            )

            logger("Created new plan: " + plan.name)

        logger.enabled = st.checkbox(
            "Enable logging",
            help=("Save debug logs in log file"),
        )

    def _plan_editor_section(self):
        """
        Render and handle the plan editing UI section.

        Allows modification and execution of the plan.
        """
        st.title(st.session_state.plan_name)

        st.session_state.plan = st.data_editor(
            st.session_state.plan,
            column_config={
                "Plan": st.column_config.TextColumn(
                    "Plan",
                    help="Plan steps which will be applied by researcher",
                    default="Step placeholder",
                    width="large",
                    required=True,
                )
            },
            num_rows="dynamic",
            hide_index=True,
        )

        if st.button("Execute plan", width="stretch"):
            logger("Executing plan - " + st.session_state.plan_name)

            with st.spinner("Executing plan..."):
                st.session_state.plan_with_results = st.session_state.executor(
                    st.session_state.plan.Plan.tolist()
                )

            st.session_state.ready = True

    def _summary_section(self):
        """
        Render the summary section after plan execution.

        Triggers summarization and displays generated PDF output.
        """
        if st.session_state.ready:
            logger("Summarizing engaged")

            with st.spinner("Summarizing..."):
                st.session_state.summarizer(st.session_state.plan_with_results)

            st.download_button(
                "Download report",
                width="stretch",
                data=st.session_state.summarizer.pdf_bytes,
                file_name=f"{st.session_state.plan_name} Result.pdf",
                mime="application/pdf",
            )

            pdf_viewer(st.session_state.summarizer.pdf_bytes)
