import re
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s::%(lineno)d - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
def regex_test(matcher, test_str):
    result = True if matcher.match(test_str) is not None else False
    logger.info(f"test_str is {test_str}, result is {result}")

compiled_regex=re.compile(r'(?i)^\s*(?:asce)*[-_\s]*7[-_\s]*([0-9]+)\s*')
regex_test(compiled_regex, "   aSce 7-22")
regex_test(compiled_regex, "   asce 7-22")
regex_test(compiled_regex, "    7-22")

