import asyncio
import base64
import io
from make_inference import make_inference
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup

async def is_fin_report(url):
    # Fetch the page content
    if url.lower().endswith('.pdf'):
        page_content_response = await make_inference('fetch_pdf', {'url': url})

        pdf_binary = base64.b64decode(page_content_response['encoded_content'])
        pdf_reader = PdfReader(io.BytesIO(pdf_binary))
        raw_content = ""
        for page in pdf_reader.pages:
            raw_content += page.extract_text()
    else:
        page_content_response = await make_inference('http_fetch', {'url': url})
        raw_html = page_content_response['content']

        soup = BeautifulSoup(raw_html, 'html.parser')
        raw_content = soup.get_text(separator=' ', strip=True)

    # Determine if it's a financial report
    report_check_response = await make_inference('is_financial_report', {'page_content': raw_content}, use_cache=False)
    is_financial_report = report_check_response['is_financial_report']

    if is_financial_report:
        print(f"The URL {url} is a financial report.")
    else:
        print(f"The URL {url} is not a financial report.")
