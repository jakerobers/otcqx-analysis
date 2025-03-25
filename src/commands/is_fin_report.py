import asyncio
from make_inference import make_inference

async def is_fin_report(url):
    # Fetch the page content
    if url.lower().endswith('.pdf'):
        page_content_response = await make_inference('fetch_pdf', {'url': url})
        # TODO: page_content_response was base64 encoded with:
        # `base64.b64encode(pdf_content).decode('utf-8')`. We need to
        # decode this back to a binary and then parse out the textual
        # content of the PDF. Assign to `raw_content`
    else:
        page_content_response = await make_inference('http_fetch', {'url': url})
        raw_html = page_content_response['content']

        # TODO: Use beautiful soup to parse out the textual content. Assign
        # to `raw_content`

    # Determine if it's a financial report
    report_check_response = await make_inference('is_financial_report', {'page_content': raw_content})
    is_financial_report = report_check_response['is_financial_report']

    if is_financial_report:
        print(f"The URL {url} is a financial report.")
    else:
        print(f"The URL {url} is not a financial report.")
