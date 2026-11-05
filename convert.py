import csv
import re
import sys
from datetime import datetime, timezone

INPUT_FILE = 'data.csv'
OUTPUT_FILE = 'filter.txt'
MIN_DOMAINS = 1000       # darunter gilt die Quelle als unvollstaendig
MAX_REJECTED = 0.01      # mehr als 1 % unbrauchbare Zeilen -> Abbruch

# plausibler Domainname: kein Leerraum, keine HTML-/Code-Zeichen, mindestens ein Punkt
DOMAIN_OK = re.compile(r'^[^\s<>/"\'=(){};,\\]+\.[^\s<>/"\'=(){};,\\]+$')


def fail(msg):
    print(f'FEHLER: {msg} - filter.txt bleibt unveraendert', file=sys.stderr)
    sys.exit(1)


def read_previous(path):
    """Liest die bisherige filter.txt: Regeln und Zeitstempel."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return None, None
    rules = [l for l in lines if l.startswith('||')]
    stamp = next((l.split(': ', 1)[1] for l in lines if l.startswith('! Generated:')), None)
    return rules, stamp


# 1) Ist data.csv ueberhaupt eine CSV? (HTML = Fehler-/Sperrseite)
with open(INPUT_FILE, 'r', encoding='utf-8-sig', errors='replace') as f:
    if f.read(512).lstrip().startswith('<'):
        fail('data.csv ist HTML (vermutlich Sperrseite von Cloudflare), keine CSV')

# 2) Domains einlesen und pruefen
rules = []
rejected = []
with open(INPUT_FILE, 'r', encoding='utf-8-sig', newline='') as infile:
    for row in csv.reader(infile, delimiter=';'):
        if not row:
            continue
        domain = row[0].strip().strip('"')
        if domain and DOMAIN_OK.match(domain):
            rules.append(f'||{domain}^|')
        else:
            rejected.append(domain)

# 3) Plausibilitaet: lieber nichts aendern als eine kaputte Liste veroeffentlichen
old_rules, old_stamp = read_previous(OUTPUT_FILE)
total = len(rules) + len(rejected)
if len(rules) < MIN_DOMAINS:
    fail(f'nur {len(rules)} gueltige Domains gefunden (Minimum {MIN_DOMAINS})')
if total and len(rejected) / total > MAX_REJECTED:
    fail(f'{len(rejected)} von {total} Zeilen sind keine Domains, z. B. {rejected[:3]}')

# 4) Zeitstempel nur erneuern, wenn sich die Regeln geaendert haben
now = datetime.now(timezone.utc).isoformat()
stamp = old_stamp if (old_rules == rules and old_stamp) else now

with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
    outfile.write('! Title: Inoffizielle Kopie - ÖIAT Watchlist Internet Filterlist\n')
    outfile.write('! Source: https://www.watchlist-internet.at/liste-betruegerischer-shops/csv/\n')
    outfile.write('! Disclaimer: Inoffizielle, automatisch erzeugte Kopie. Keine Verbindung zu ÖIAT Watchlist Internet. Keine Gewaehr fuer Richtigkeit und Vollstaendigkeit.\n')
    outfile.write(f'! Generated: {stamp}\n')
    for rule in rules:
        outfile.write(rule + '\n')

print(f'{len(rules)} Domains geschrieben')
