import asyncio
from make_inference import make_inference

async def is_fin_report(url):
    # Fetch the page content
    page_content_response = await make_inference('http_fetch', {'url': url})
    raw_html = page_content_response['content']

    # Determine if it's a financial report
    report_check_response = await make_inference('is_financial_report', {'page_content': raw_html})
    is_financial_report = report_check_response['is_financial_report']

    if is_financial_report:
        print(f"The URL {url} is a financial report.")
    else:
        print(f"The URL {url} is not a financial report.")
