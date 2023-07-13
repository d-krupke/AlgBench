import logging

from algbench import JsonLogCapture, JsonLogHandler


def test_logger_basics():
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    json_log = JsonLogHandler()
    logger.addHandler(json_log)
    logger.info("test")
    assert len(json_log.get_entries()) == 1
    print(json_log.get_entries())


def test_log_catcher():
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.ERROR)
    # The following case should catch the log, as we set the level to INFO
    with JsonLogCapture("test_logger", logging.INFO) as catcher:
        logger.info("test")
    assert len(catcher.get_entries()) == 1
    # The following case should not catch anything
    with JsonLogCapture("test_logger", logging.CRITICAL) as catcher:
        logger.info("test")
    assert len(catcher.get_entries()) == 0
