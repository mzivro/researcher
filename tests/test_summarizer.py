from unittest.mock import MagicMock, patch

import pytest

from summarizer import Summarizer


@pytest.fixture
def summarizer():
    with (
        patch("summarizer.ChatOpenAI"),
        patch("summarizer.ChatPromptTemplate.from_messages"),
    ):
        return Summarizer()


class TestSummarizerCleanMarkdown:
    def test_removes_null_bytes(self, summarizer):
        assert summarizer._clean_markdown("hello\x00world") == "helloworld"

    def test_closes_unclosed_code_fence(self, summarizer):
        md = "# Title\n\n```python\nprint('hi')"
        cleaned = summarizer._clean_markdown(md)
        assert cleaned.count("```") % 2 == 0
        assert cleaned.endswith("```")

    def test_leaves_balanced_code_fences_unchanged(self, summarizer):
        md = "```\ncode\n```"
        assert summarizer._clean_markdown(md) == md


class TestSummarizerMakePdf:
    def test_make_pdf_sets_bytes_on_success(self, summarizer, tmp_path):
        pdf_file = tmp_path / "report.pdf"
        pdf_file.write_bytes(b"%PDF-fake")

        with (
            patch("summarizer.tempfile.NamedTemporaryFile") as tmp_cls,
            patch("summarizer.pypandoc.convert_text") as convert,
            patch("summarizer.Path") as path_cls,
        ):
            tmp_cls.return_value.__enter__.return_value.name = str(pdf_file)
            path_cls.return_value.read_bytes.return_value = b"%PDF-fake"
            convert.return_value = None

            summarizer._make_pdf("# Report\n\nContent")

        assert summarizer.pdf_bytes == b"%PDF-fake"
        convert.assert_called_once()

    def test_make_pdf_handles_runtime_error(self, summarizer):
        with (
            patch("summarizer.tempfile.NamedTemporaryFile") as tmp_cls,
            patch("summarizer.pypandoc.convert_text", side_effect=RuntimeError("no latex")),
            patch("summarizer.logger") as mock_logger,
        ):
            tmp_cls.return_value.__enter__.return_value.name = "/tmp/x.pdf"
            summarizer._make_pdf("# Report")

        assert summarizer.pdf_bytes is None
        mock_logger.assert_any_call("PDF generation failed: no latex")
