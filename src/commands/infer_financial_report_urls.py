import csv
import logging
from make_inference import make_inference
from bs4 import BeautifulSoup
from commands.get_url import get_url

logger = logging.getLogger(__name__)

async def infer_financial_report_urls(input_file, limit=None):
    """
    Infers the financial reporting page (e.g., investor relations) for a list of companies from a CSV file.

    :param input_file: Path to the input CSV file containing company names.
    :param limit: Optional limit on the number of companies to process.
    """
    # Note: We might want to get rid of the get-url command and just have
    # everything flow through this command
    urls = await get_url(input_file, limit)

    all_fin_doc_urls = []
    for company_home_url in urls:
        financial_document_urls = await _infer_financial_report_url([company_home_url])
        all_fin_doc_urls.append(financial_document_urls)

    # TODO: zip these up by company in input_file, using limit.


async def _infer_financial_report_url(url_stack):
    if len(url_stack) >= 2:
        logger.error(f"Recursion limit reached. Trace: {url_stack}")
        return

    current_url = url_stack[-1]

    if current_url.lower().endswith('.pdf'):
        response = await make_inference('fetch_pdf', {'url': current_url})
    else:
        # Note: we'll want to disable caching for this call in production. Hold
        # off on this for now.
        response = await make_inference('http_fetch', {'url': current_url})

    html_content = response['content']

    is_financial_report = await make_inference('is_financial_report', {'page_content': html_content})
    if is_financial_report:
        return current_url

    # Page not found yet, check which links are available to crawl.
    soup = BeautifulSoup(html_content, 'html.parser')
    links = [(a.get('href'), a.text) for a in soup.find_all('a', href=True)]
    logger.debug(f"Found links: {links}")

    # TODO: Recursively call this
    # await _infer_financial_report_url(url_stack + [next_url])



"""
1. fetch sitemap contents
2. embed all of the links
3. embed a reference: "Financial reports"
4. Find the closest matches (using z-score / mean & stddev ranking)
5. DFS against the hits
6. Bump recursion limit up to 10. Probably won't hit it ever.
7. For checking if we've reached our destination...
    a. Consider the page document d, containing a set of nodes N
    b. Embed the nodes
    c. Cluster the nodes
    d. Require that some number of clusters are close in distance to reference(s) R
    e. Could later FT a model where cluster embeddings are X.
"""
