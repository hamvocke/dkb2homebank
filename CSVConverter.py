import argparse
import csv
from datetime import datetime

class dkb(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL

csv.register_dialect("dkb", dkb)


class Converter():
    reader = None
    writer = None
    dkbFieldNames = ["buchungstag",
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


    visaFieldNames =    ["abgerechnet",
                         "wertstellung",
                         "belegdatum",
                         "umsatzbeschreibung",
                         "betrag",
                         "urspruenglicherBetrag"]

    homebankFieldNames = ["date",
                          "paymode",
                          "info",
                          "payee",
                          "memo",
                          "amount",
                          "category",
                          "tags"]


    def convertDkbCash(self, filename):
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile, dialect='dkb', fieldnames=self.dkbFieldNames)

            with open("cashHomebank.csv", 'w') as csvfile:

                # skip header lines
                for i in range(1, 6):
                    next(reader)

                writer = csv.DictWriter(csvfile, dialect='dkb', fieldnames=self.homebankFieldNames)
                for row in reader:
                    writer.writerow(
                        {
                        'date': self.convertDate(row["buchungstag"]),
                        'paymode': 8,
                        'info': None,
                        'payee': row["beguenstigter"],
                        'memo': row["verwendungszweck"],
                        'amount': row["betrag"],
                        'category': None,
                        'tags': None
                        })

    def convertVisa(self, filename):
        with open(filename, 'r') as csvfile:
            self.reader = csv.DictReader(csvfile, dialect='dkb', fieldnames=self.visaFieldNames)

            with open("visaHomebank.csv", 'w') as csvfile:
                writer = csv.DictWriter(csvfile, dialect='dkb', fieldnames=self.homebankFieldNames)
                for row in self.reader:
                    writer.writerow(
                        {
                        'date': self.convertDate(row["wertstellung"]),
                        'paymode': 1,
                        'info': None,
                        'payee': None,
                        'memo': row["umsatzbeschreibung"],
                        'amount': row["betrag"],
                        'category': None,
                        'tags': None
                        })


    def convertDate(self, dateString):
        date = datetime.strptime(dateString, "%d.%m.%Y")
        return date.strftime('%d-%m-%Y')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert a CSV export file from DKB online banking to a Homebank compatible CSV format.")
    parser.add_argument("filename", help="The CSV file to convert.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--visa", action="store_true", help="convert a DKB Visa account CSV file")
    group.add_argument("-c", "--cash", action="store_true", help="convert a DKB Cash account CSV file")

    args = parser.parse_args()

    converter = Converter()
    if args.visa:
        converter.convertVisa(args.filename)
        print("DKB Visa file converted. Output file: 'visaHomebank.csv'")
    elif args.cash:
        converter.convertDkbCash(args.filename)
        print("DKB Cash file converted. Output file: 'cashHomebank.csv'")
    else:
        print("You must provide the type of the CSV file (--cash for DKB Cash, --visa for DKB Visa)")
