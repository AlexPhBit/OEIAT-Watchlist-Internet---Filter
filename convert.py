import csv
from datetime import datetime, timezone


def read_previous(path):
    """Liest die bisherige filter.txt: Regeln und Zeitpunkt der letzten Aenderung."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return None, None
    rules = [l for l in lines if l.startswith('||')]
    stamp = next((l.split(': ', 1)[1] for l in lines if l.startswith('! Generated:')), None)
    return rules, stamp


# Regeln aus der CSV einlesen
rules = []
with open('data.csv', 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile, delimiter=';')
    for row in reader:
        if len(row) >= 1:
            domain = row[0].strip().strip('"')
            if domain and '.' in domain:
                rules.append(f'||{domain}^|')

# Zeitstempel nur erneuern, wenn sich die Regeln geaendert haben
old_rules, old_stamp = read_previous('filter.txt')
now = datetime.now(timezone.utc).isoformat()
stamp = old_stamp if (old_rules == rules and old_stamp) else now

with open('filter.txt', 'w', encoding='utf-8') as outfile:
    outfile.write('! Title: Inoffizielle Kopie - ÖIAT Watchlist Internet Filterlist\n')
    outfile.write('! Source: https://www.watchlist-internet.at/liste-betruegerischer-shops/csv/\n')
    outfile.write('! Disclaimer: Inoffizielle, automatisch erzeugte Kopie. Keine Verbindung zu ÖIAT Watchlist Internet. Keine Gewaehr fuer Richtigkeit und Vollstaendigkeit.\n')
    outfile.write(f'! Generated: {stamp}\n')
    for rule in rules:
        outfile.write(rule + '\n')
