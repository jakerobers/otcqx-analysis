import sys
import os
import argparse
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from otcqx_analysis import process_and_cluster_companies

def scrape(input_file):
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        company_names = [row['Security Name'] for row in reader]
    print("Company names extracted:", company_names)

def main():
    parser = argparse.ArgumentParser(description="OTCQX Analysis Tool")
    subparsers = parser.add_subparsers(dest='command')

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape company data')
    scrape_parser.add_argument('-i', '--input', required=True, help='Input file path')

    args = parser.parse_args()

    if args.command == 'scrape':
        scrape(args.input)
    else:
        return
        # TODO: Implement better clustering algorithm
        process_and_cluster_companies()

if __name__ == "__main__":
    main()
