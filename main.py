import sys

from query_finders.query_finder import QcodeFinder

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please provide a Wikidata Qcode for a human being as an argument")
        print('Usage example: "python3 main.py Q615"')
        sys.exit(1)
    qcode = sys.argv[1]
    result = QcodeFinder(qcode)
    print(result)