import re
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s::%(lineno)d - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
# compiled_regex = re.compile(r'https*://localhost:[0-9]+')
compiled_regex = re.compile(r'https*://(www\.)*(app\.)*(localhost|terean|47\.48\.84\.166|172\.16\.1\.[0-9]*)(\.com)*:*[0-9]*')
# compiled_regex = re.compile(r'https*://(www\.)*(app\.)(localhost|terean|47\.48\.84\.166)(\.com)*:[0-9]+')
def regex_test(test_str, matcher=compiled_regex):
    result = True if matcher.match(test_str) is not None else False
    logger.info(f"test_str is {test_str}, result is {result}")
regex_test("http://localhost")
regex_test("http://localhost:1234")
regex_test("https://localhost:1234")
regex_test("http://172.16.1.1:1234")
regex_test("https://172.16.1.1:1234")
regex_test("http://47.48.84.166:1234")
regex_test("https://47.48.84.166:1234")
regex_test("http://www.app.terean.com:1234")
regex_test("https://www.app.terean.com:1234")
regex_test("http://www.terean.com:1234")
regex_test("https://www.terean.com:1234")

