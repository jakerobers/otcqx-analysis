import browser_use as browser

def download_10k_reports(company_name, num_reports=5):
    """
    Downloads the latest 10-K reports for a given company.

    :param company_name: Name of the company to search for.
    :param num_reports: Number of reports to download. Default is 5.
    """
    # Open a browser session
    with browser.Browser() as b:
        # Search for the company's main website on Google
        b.go_to("https://www.google.com")
        b.type(company_name, into="q")
        b.submit()

        # Click on the first link to go to the company's main website
        b.click_link(index=0)

        # Use inference to navigate to the financial reporting or investor relations page
        # This might involve searching for keywords like "investor", "financials", "reports", etc.
        potential_links = b.find_links()
        for link in potential_links:
            if any(keyword in link.text.lower() for keyword in ["investor", "financials", "reports", "10-K"]):
                b.click_link(link=link)
                break

        # Find and download the 10-K reports
        reports_downloaded = 0
        for link in b.find_links(text="10-K"):
            if reports_downloaded >= num_reports:
                break
            b.download(link)
            reports_downloaded += 1

        print(f"Downloaded {reports_downloaded} reports for {company_name}.")
