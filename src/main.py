import argparse
import asyncio
import logging
import os
from commands.get_url import get_url

def setup_logging():
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        filename='logs/llm_calls.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
from commands.dox import dox
from commands.infer_financial_report_urls import infer_financial_report_urls


async def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="OTCQX Analysis Tool")
    subparsers = parser.add_subparsers(dest='command')


    # Dox command
    dox_parser = subparsers.add_parser('dox', help='Categorizes a list of companies by industry')
    dox_parser.add_argument('-i', '--input', required=True, help='Input file path')
    dox_parser.add_argument('-o', '--output', required=True, help='Output file path')

    # Infer financial report URLs command
    infer_fin_report_urls_parser = subparsers.add_parser('infer-fin-report-urls', help='Infer the financial reporting page of the company')
    infer_fin_report_urls_parser.add_argument('-i', '--input', required=True, help='Input file path')
    infer_fin_report_urls_parser.add_argument('-l', '--limit', type=int, help='Limit the number of companies to process')

    # Fetch domain for a company
    get_url_parser = subparsers.add_parser('get-url', help='Fetch the URL for a company\'s financial documents')
    get_url_parser.add_argument('-i', '--input', required=True, help='Input file path')
    get_url_parser.add_argument('-l', '--limit', type=int, help='Limit the number of companies to process')

    args = parser.parse_args()

    if args.command == 'dox':
        await dox(args.input, args.output)
    elif args.command == 'infer-fin-report-urls':
        await infer_financial_report_urls(args.input, args.limit)
    elif args.command == 'get-url':
        await get_url(args.input, args.limit)

if __name__ == '__main__':
    asyncio.run(main())
