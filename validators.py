import logging

from regex_patterns import github_ui_repo_re

logger = logging.getLogger('Olympus')

def parse_int(value) -> int:
    try:
        i = int(value)
    except:
        logger.error(ValueError(f"Expected integer, got {value}."))
        i=8192
    return i

def check_url(value):
    match = github_ui_repo_re.match(value)

    if match:
        return match
    else:
        logger.error(ValueError(f"Expected value to match pattern:\n{github_ui_repo_re.pattern}\nActual value: {value}"))
        return None