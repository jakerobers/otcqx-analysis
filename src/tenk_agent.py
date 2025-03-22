import browser_use as browser

def download_10k_reports(company_name, num_reports=5):
    """
    Downloads the latest 10-K reports for a given company.

    :param company_name: Name of the company to search for.
    :param num_reports: Number of reports to download. Default is 5.
    """
    # Open a browser session
    with browser.Browser() as b:
        # Search for the company on Google
        b.go_to("https://www.google.com")
        b.type(company_name + " site:investor relations", into="q")
        b.submit()

        # Navigate to the company's investor relations page
        b.click_link(text="Investor Relations")

        # Find and download the 10-K reports
        reports_downloaded = 0
        for link in b.find_links(text="10-K"):
            if reports_downloaded >= num_reports:
                break
            b.download(link)
            reports_downloaded += 1

        print(f"Downloaded {reports_downloaded} reports for {company_name}.")
