from logger import Logger


class TestLogger:
    def test_disabled_logger_writes_nothing(self, tmp_log_dir):
        log = Logger()
        log.enabled = False
        log("should not appear")

        assert list(tmp_log_dir.iterdir()) == []

    def test_enabled_logger_writes_timestamped_line(self, tmp_log_dir):
        log = Logger()
        log.enabled = True
        log("test message")

        logfile = tmp_log_dir / "logfile.txt"
        assert logfile.exists()
        content = logfile.read_text()
        assert "test message" in content
        assert content.endswith("\n")

    def test_multiple_writes_append(self, tmp_log_dir):
        log = Logger()
        log.enabled = True
        log("first")
        log("second")

        lines = (tmp_log_dir / "logfile.txt").read_text().strip().split("\n")
        assert len(lines) == 2
        assert "first" in lines[0]
        assert "second" in lines[1]
