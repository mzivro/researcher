from langchain_core.prompts import ChatPromptTemplate
from prompts import summarizer_prompt_template
from langchain_openai import ChatOpenAI
from settings import settings
from logger import logger
from pathlib import Path

import tempfile
import pypandoc
import os


class Summarizer:
    """
    Generates a Markdown summary of executed plan results and converts it to PDF.

    Attributes
    ----------
    summarizer_prompt : ChatPromptTemplate
        Prompt template used to generate summaries.
    llm : ChatOpenAI
        Language model used for summarization.
    pdf_bytes : str or None
        Path to the generated PDF temporary file.
    """

    def __init__(self):
        """
        Initialize summarizer with LLM and prompt template.
        """
        self.summarizer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", summarizer_prompt_template),
                ("user", "Summarize these plan results in markdown:\n{plan}\n"),
            ]
        )

        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_summarizer_model,
            temperature=settings.openai_summarizer_temperature,
        )

        self.pdf_bytes = None

    def __call__(self, plan):
        """
        Generate a summary and export it to PDF.

        Parameters
        ----------
        plan : list of str
            Executed plan steps including results.
        """

        summarizer = self.summarizer_prompt | self.llm

        logger("Calling summarizer")

        summary = summarizer.invoke({"plan": "\nSTEP: ".join(plan)})

        self._make_pdf(summary.content)

    def _clean_markdown(self, md):
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

    def _make_pdf(self, summary):
        """
        Convert Markdown summary to PDF and save files.

        Parameters
        ----------
        summary : str
            Markdown-formatted summary.
        """
        summary = self._clean_markdown(summary)

        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                pypandoc.convert_text(
                    summary,
                    "pdf",
                    format="md",
                    outputfile=tmp.name,
                    extra_args=["--standalone", "--pdf-engine=xelatex"],
                )

                self.pdf_bytes = Path(tmp.name).read_bytes()
        except RuntimeError as e:
            logger(f"PDF generation failed: {e}")

        logger(f"output file created")
