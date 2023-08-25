#! /usr/bin/env python3

import argparse
import csv
from datetime import datetime


class DKB(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL


class InvalidInputException(Exception):
    """Exception for input CSVs that seem not to be valid DKB input files."""
    def __init__(self, message):
        self.message = message


csv.register_dialect("dkb", DKB)

cash_field_names = ["buchungstag",
                   "wertstellung",
                   "buchungstext",
                   "beguenstigter",
                   "verwendungszweck",
                   "kontonummer",
                   "blz",
                   "betrag",
                   "glaeubigerID",
                   "mandatsreferenz",
                   "kundenreferenz"]

visa_field_names = ["abgerechnet",
                    "wertstellung",
                    "belegdatum",
                    "umsatzbeschreibung",
                    "betrag",
                    "urspruenglicherBetrag"]

giro_field_names = ["buchungsdatum",
                   "wertstellung",
                   "status",
                   "zahlungspflichtige*r",
                   "zahlungsempfänger*in",
                   "verwendungszweck",
                   "umsatztyp",
                   "betrag",
                   "gläubiger-id",
                   "mandatsreferenz",
                   "kundenreferenz"]

homebank_field_names = ["date",
                        "paymode",
                        "info",
                        "payee",
                        "memo",
                        "amount",
                        "category",
                        "tags"]


def _identify_csv_dialect(file_handle, field_names):
    """

    :param file_handle:
    :param field_names:
    :return:
    """
    dialect = csv.Sniffer().sniff(file_handle.read(1024))
    file_handle.seek(0)
    return csv.DictReader(find_transaction_lines(file_handle), dialect=dialect, fieldnames=field_names)


def identify_account_type(file_handle):
    """
    Automatically figure out whether a file is a cash, visa, or giro account CSV.

    This is easily recognisable by the first line of the file:
    A cash file has the string '"Kontonummer:"' (note the double quotes around the word as CSV field delimiters),
    then the account IBAN, a single forward slash (/) followed by the account name, surrounded by spaces:

    "Kontonummer:";"DE01234500001234567891 / Foobar";

    A visa CSV looks like this:

    "Kreditkarte:";"1234********6789";

    And a giro CSV file (introduced with the new banking portal in 2023) looks like this:

    "Konto:";"Girokonto DE33**************6789"

    :return: the string "cash", "visa", or "giro"
    """
    header_line = file_handle.readline()
    file_handle.seek(0)
    if header_line.startswith('"Kreditkarte:";"'):
        return "visa"
    elif header_line.startswith('"Kontonummer:";"'):
        return "cash"
    elif header_line.startswith('"Konto";"Girokonto'):
        return "giro"
    raise InvalidInputException("Can't recognise account type, is this a valid DKB export CSV?")


def convert_cash(file_handle, output_file="cashHomebank.csv"):
    """
    Convert a DKB cash file (i.e. normal bank account) to a homebank-readable import CSV.

    :param file_handle: file handle of the file to be converted
    :param output_file: the output file path as a string
    """
    reader = _identify_csv_dialect(file_handle, cash_field_names)
    with open(output_file, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect='dkb', fieldnames=homebank_field_names)
        for row in reader:
            writer.writerow(
                {
                    'date': convert_date(row["buchungstag"]),
                    'paymode': 8,
                    'info': None,
                    'payee': row["beguenstigter"],
                    'memo': row["verwendungszweck"],
                    'amount': row["betrag"],
                    'category': None,
                    'tags': None
                })


def convert_visa(file_handle, output_file="visaHomebank.csv"):
    """
    Convert a DKB visa file to a homebank-readable import CSV.

    :param file_handle: file handle of the file to be converted
    :param output_file: the output file path as a string
    """
    reader = _identify_csv_dialect(file_handle, visa_field_names)
    with open(output_file, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect='dkb', fieldnames=homebank_field_names)
        for row in reader:
            writer.writerow(
                {
                    'date': convert_date(row["wertstellung"]),
                    'paymode': 1,
                    'info': None,
                    'payee': None,
                    'memo': row["umsatzbeschreibung"],
                    'amount': row["betrag"],
                    'category': None,
                    'tags': None
                })

def convert_giro(file_handle, output_file="giroHomebank.csv"):
    """
    Convert a DKB giro file (i.e. the normal bank account file available in the
    new banking portal introduced in 2023) to a homebank-readable import CSV.

    :param file_handle: file handle of the file to be converted
    :param output_file: the output file path as a string
    """
    reader = _identify_csv_dialect(file_handle, giro_field_names)
    with open(output_file, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect='dkb', fieldnames=homebank_field_names)
        for row in reader:
            writer.writerow(
                {
                    'date': convert_short_date(row["buchungsdatum"]),
                    'paymode': 8,
                    'info': None,
                    'payee': row["zahlungsempfänger*in"],
                    'memo': row["verwendungszweck"],
                    'amount': row["betrag"],
                    'category': None,
                    'tags': None
                })

def find_transaction_lines(file):
    """
    Reduce the csv lines to the lines containing actual data relevant for the conversion.

    :param file: The export CSV from DKB to be converted
    :return: The lines containing the actual transaction data
    """
    lines = file.readlines()
    i = 1
    for line in lines:
        # simple heuristic to find the csv header line. Both these strings
        # appear in headers of the cash, visa, and giro CSVs.
        if "Betrag" in line and "Wertstellung" in line:
            return lines[i:]
        i = i + 1

    raise ValueError("Can't convert CSV file without header line")


def convert_date(date_string):
    """Convert the date_string to dd-mm-YYYY format."""
    date = datetime.strptime(date_string, "%d.%m.%Y")
    return date.strftime('%d-%m-%Y')

def convert_short_date(date_string):
    """Convert the date_string to dd-mm-YYYY format."""
    date = datetime.strptime(date_string, "%d.%m.%y")
    return date.strftime('%d-%m-%Y')

def setup_parser():
    parser = argparse.ArgumentParser(description=
                                     "Convert a CSV export file from DKB online banking "
                                     "to a Homebank compatible CSV format.")
    parser.add_argument("filename", help="The CSV file to convert.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--visa", action="store_true", help="convert a DKB Visa account CSV file")
    group.add_argument("-c", "--cash", action="store_true", help="convert a DKB Cash account CSV file")
    group.add_argument("-g", "--giro", action="store_true", help="convert a DKB Giro account CSV file (newly introduced in 2023)")

    parser.add_argument('-o', '--output-file', default='Homebank.csv',
                        help='choose where to store the output file (default: working directory')

    parser.add_argument('--debug', '-d', help='output some information to STDERR')

    return parser.parse_args()


def main():

    args = setup_parser()

    with open(args.filename, 'r', encoding='utf-8') as csv_file:
        account_type = identify_account_type(csv_file)
        if "visa" == account_type or args.visa:
            output = args.output_file or "visaHomebank.csv"
            convert_visa(csv_file, output)
            print(f"DKB Visa file converted. Output file: {output}") if args.debug else None
        elif "cash" == account_type or args.cash:
            output = args.output_file or "cashHomebank.csv"
            convert_cash(csv_file, output)
            print(f"DKB Cash file converted. Output file: {output}") if args.debug else None
        elif "giro" == account_type or args.giro:
            output = args.output_file or "cashHomebank.csv"
            convert_giro(csv_file, output)
            print(f"DKB Giro file converted. Output file: {output}") if args.debug else None


if __name__ == '__main__':
    main()
