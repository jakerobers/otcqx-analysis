import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from otcqx_analysis import process_and_cluster_companies

def main():
    process_and_cluster_companies()

if __name__ == "__main__":
    main()
