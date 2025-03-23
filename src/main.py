import argparse
import asyncio
from commands.get_url import get_url
from commands.dox import dox
from commands.infer_financial_page import infer_financial_page
from commands.infer_financial_report_url import infer_financial_report_url


async def main():
    parser = argparse.ArgumentParser(description="OTCQX Analysis Tool")
    subparsers = parser.add_subparsers(dest='command')


    # Dox command
    dox_parser = subparsers.add_parser('dox', help='Categorizes a list of companies by industry')
    dox_parser.add_argument('-i', '--input', required=True, help='Input file path')
    dox_parser.add_argument('-o', '--output', required=True, help='Output file path')

    # Infer financial page command
    infer_fin_page_parser = subparsers.add_parser('infer-fin-page', help='Infer the financial reporting page of the company')
    infer_fin_page_parser.add_argument('-i', '--input', required=True, help='Input file path')
    infer_fin_page_parser.add_argument('-l', '--limit', type=int, help='Limit the number of companies to process')

    # Infer financial report URL command
    infer_fin_report_url_parser = subparsers.add_parser('infer-fin-report-url', help='Infer the financial report URL of the company')
    infer_fin_report_url_parser.add_argument('-c', '--company', required=True, help='Company name')

    # Fetch domain for a company
    get_url_parser = subparsers.add_parser('get-url', help='Fetch the URL for a company\'s financial documents')
    get_url_parser.add_argument('-i', '--input', required=True, help='Input file path')
    get_url_parser.add_argument('-l', '--limit', type=int, help='Limit the number of companies to process')

    args = parser.parse_args()

    if args.command == 'dox':
        await dox(args.input, args.output)
    elif args.command == 'infer-fin-page':
        await infer_financial_page(args.input, args.limit)
    elif args.command == 'infer-fin-report-url':
        await infer_financial_report_url(args.company)
    elif args.command == 'get-url':
        await get_url(args.input, args.limit)

if __name__ == '__main__':
    asyncio.run(main())
