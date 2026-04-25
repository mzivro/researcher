from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from settings import settings
from logger import logger

import pypandoc
import os


class Summarizer:
    """
    Generates a Markdown summary of executed plan results and converts it to PDF.

    Attributes
    ----------
    llm : ChatOpenAI
        Language model used for summarization.
    summarizer_prompt_template : str
        Prompt defining formatting constraints for output.
    pdf_file : str or None
        Path to the generated PDF file.
    """
    def __init__(self):
        """
        Initialize summarizer with LLM and prompt template.
        """
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_summarizer_model,
            temperature=settings.openai_summarizer_temperature,
        )

        self.summarizer_prompt_template = (
            "You are a research plan results summarizer.\n"
            "Output STRICTLY valid GitHub-Flavored Markdown.\n"
            "Rules:\n"
            "- Use #, ##, ### headings\n"
            "- Use proper bullet points (-)\n"
            "- No HTML\n"
            "- No trailing incomplete structures\n"
            "- Close all code blocks\n"
            "- Do not include explanations outside Markdown\n"
        )

        self.pdf_file = None

    def __call__(self, plan: list[str], plan_name: str):
        """
        Generate a summary and export it to PDF.

        Parameters
        ----------
        plan : list of str
            Executed plan steps including results.
        plan_name : str
            Name of the plan used for output file naming.
        """
        summarizer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.summarizer_prompt_template),
                ("user", "Summarize these plan results in markdown:\n{plan}\n"),
            ]
        )

        summarizer = summarizer_prompt | self.llm

        logger("Calling summarizer")

        summary = summarizer.invoke({"plan": "\nSTEP: ".join(plan)})

        self._make_pdf(summary.content, plan_name)

    def _clean_markdown(self, md: str) -> str:
        """
        Clean and fix Markdown formatting issues.

        Parameters
        ----------
        md : str
            Raw Markdown text.

        Returns
        -------
        str
            Cleaned Markdown text.
        """
        # delete weird characters
        md = md.replace("\x00", "")

        # close open codeblocks
        if md.count("```") % 2 != 0:
            md += "\n```"

        return md

    def _make_pdf(self, summary: str, plan_name: str):
        """
        Convert Markdown summary to PDF and save files.

        Parameters
        ----------
        summary : str
            Markdown-formatted summary.
        plan_name : str
            Name used for output file naming.
        """
        os.makedirs("results", exist_ok=True)

        self.pdf_file = os.path.join("results", f"{plan_name} Result.pdf")
        md_file = os.path.join("results", f"{plan_name} Result.md")

        summary = self._clean_markdown(summary)

        with open(md_file, "w", encoding="utf-8") as file:
            file.write(summary)

        try:
            pypandoc.convert_text(
                summary,
                "pdf",
                format="md",
                outputfile=self.pdf_file,
                extra_args=["--standalone", "--pdf-engine=xelatex"],
            )
        except RuntimeError as e:
            logger(f"PDF generation failed: {e}")

        logger(f"output file created - {self.pdf_file}")
