import os
import asyncio
from browser_use import Agent, Controller, ActionResult
from browser_use.browser.browser import Browser, BrowserConfig
from langchain_openai import ChatOpenAI
from cache_utils import make_llm_call_with_cache, cache_data
from llm_fetchers import LinkDecisionFetcher

# Configure the browser
browser = Browser(
    config=BrowserConfig(
        chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    ),
)

controller = Controller()

@controller.registry.action('Download 10-K reports')
async def download_10k_reports(browser_context, company_name, num_reports=5):
    """
    Downloads the latest 10-K reports for a given company.

    :param company_name: Name of the company to search for.
    :param num_reports: Number of reports to download. Default is 5.
    """
    page = await browser_context.get_current_page()
    await page.goto("https://www.google.com")
    await page.type(company_name, into="q")
    await page.submit()

    # Click on the first link to go to the company's main website
    await page.click_link(index=0)

    # Use inference to navigate to the financial reporting or investor relations page
    potential_links = await page.find_links()

    fetcher = LinkDecisionFetcher(model_name='gpt-4o')
    for link in potential_links:
        cached_response = await make_llm_call_with_cache('link_decision', link.text, lambda: fetcher.fetch_decision(link.text))
        response = cached_response['response']
        if response.lower() == "yes":
            await page.click_link(link=link)
            break

    # Find and download the 10-K reports
    reports_downloaded = 0
    for link in await page.find_links(text="10-K"):
        if reports_downloaded >= num_reports:
            break
        await page.download(link)
        reports_downloaded += 1

    return ActionResult(extracted_content=f"Downloaded {reports_downloaded} reports for {company_name}.")

async def main():
    async with await browser.new_context() as context:
        model = ChatOpenAI(model='gpt-4o')

        tenk_agent = Agent(
            task="""
                Download the latest 10-K reports for a given company.
            """,
            llm=model,
            browser_context=context,
            controller=controller,
        )
        await tenk_agent.run()

if __name__ == '__main__':
    asyncio.run(main())
