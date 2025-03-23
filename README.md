# 10-K Report Downloader

This project is designed to automate the process of downloading the latest
10-K reports for a given company. It uses a combination of web scraping and
language model inference to navigate to the appropriate sections of a
company's website and retrieve the desired documents.

## Features

- **Automated Web Navigation**: Utilizes a browser automation framework to
  search for company websites and navigate to financial document sections.
- **Language Model Integration**: Employs OpenAI's language models to
  intelligently select links that are most likely to lead to 10-K reports
  or related financial documents.
- **Caching Mechanism**: Implements caching to store and reuse results of
  language model calls, improving efficiency and reducing API usage.

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:jakerobers/otcqx-analysis.git
   cd otcqx-analysis
   ```

2. Install the required dependencies using `uv`:
   ```bash
   uv sync
   ```

3. Set up environment variables for OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

To run the 10-K report downloader, execute the following command:

```bash
python src/main.py agent -i "data/index/Stock_Screener.csv"
```

This will initiate the process of downloading the latest 10-K reports for a specified company.

## Configuration

- **Browser Configuration**: The browser is configured to use Google
  Chrome. Ensure that the path to the Chrome executable is correctly set in
  `src/tenk_agent.py`.
- **Language Model**: The project uses the `gpt-4o` model from OpenAI. You
  can adjust the model settings in `src/llm_fetchers.py`.

## Runbook


```
python ./src/main.py dox -i ./data/index/20250322_stock_screener.csv -o ./data/index/20250322_clustered_companies.csv
```
