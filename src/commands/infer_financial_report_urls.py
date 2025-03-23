import csv
import logging
import aiohttp
from bs4 import BeautifulSoup
from commands.get_url import get_url

logger = logging.getLogger(__name__)

async def infer_financial_report_urls(input_file, limit=None):
    """
    Infers the financial reporting page (e.g., investor relations) for a list of companies from a CSV file.

    :param input_file: Path to the input CSV file containing company names.
    :param limit: Optional limit on the number of companies to process.
    """
    urls = await get_url(input_file, limit)
    for company_home_url in urls:
        financial_document_urls = _infer_financial_report_url([company_home_url])


async def _infer_financial_report_url(url_stack):
    if len(url_stack) >= 5:
        logger.error(f"Recursion limit reached. Trace: {url_stack}")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html_content = await response.text()

    soup = BeautifulSoup(html_content, 'html.parser')
    links = [(a.get('href'), a.text) for a in soup.find_all('a', href=True)]
    logger.info(f"Found links: {links}")

    # TODO: do an LLM call to find the link that would most likely point
    # ultimately towards a financial document
