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








# compiled_regex = re.compile(r'https*://localhost:[0-9]+')
# compiled_regex = re.compile(r'https*://(www\.)*(app\.)*(localhost|terean|47\.48\.84\.166|172\.16\.1\.[0-9]*)(\.com)*:*[0-9]*')
# compiled_regex = re.compile(r'https*://(www\.)*(app\.)(localhost|terean|47\.48\.84\.166)(\.com)*:[0-9]+')
# regex_test(compiled_regex, "http://localhost")
# regex_test(compiled_regex, "http://localhost:1234")
# regex_test(compiled_regex, "https://localhost:1234")
# regex_test(compiled_regex, "http://172.16.1.1:1234")
# regex_test(compiled_regex, "https://172.16.1.1:1234")
# regex_test(compiled_regex, "http://47.48.84.166:1234")
# regex_test(compiled_regex, "https://47.48.84.166:1234")
# regex_test(compiled_regex, "http://www.app.terean.com:1234")
# regex_test(compiled_regex, "https://www.app.terean.com:1234")
# regex_test(compiled_regex, "http://www.terean.com:1234")
# regex_test(compiled_regex, "https://www.terean.com:1234")

