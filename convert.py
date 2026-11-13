import csv
import re
import sys
import unicodedata
from datetime import datetime, timezone

INPUT_FILE = 'data.csv'
OUTPUT_FILE = 'filter.txt'
MIN_DOMAINS = 300        # darunter gilt die Quelle als unvollstaendig

# plausibler Domainname: kein Leerraum, keine HTML-/Code-Zeichen, kein Doppelpunkt, mindestens ein Punkt
DOMAIN_OK = re.compile(r'^[^\s<>/"\'=(){};:,\\]+\.[^\s<>/"\'=(){};:,\\]+$')
# unsichtbare Zeichen, die sich in Domains einschleichen koennen (Soft Hyphen, Zero-Width, BOM)
INVISIBLE = re.compile('[\u00ad\u200b\u200c\u200d\u2060\ufeff]')


def fail(msg):
    print(f'FEHLER: {msg} - filter.txt bleibt unveraendert', file=sys.stderr)
    sys.exit(1)


def normalize(raw):
    """Bereinigt einen Eintrag: unsichtbare Zeichen raus, Port und Punkt am Ende
    abschneiden, Umlaute je Label als Punycode (xn--...). Die Schreibweise bleibt
    wie in der CSV; nur Labels mit Umlauten werden klein geschrieben, sonst waere
    der Punycode falsch. Gibt None zurueck, wenn der Eintrag keine plausible
    Domain ist."""
    d = INVISIBLE.sub('', raw.strip().strip('"'))
    d = unicodedata.normalize('NFKC', d)
    d = re.sub(r':\d{1,5}$', '', d).rstrip('.')   # DNS kennt keine Ports
    if not DOMAIN_OK.match(d):
        return None
    labels = []
    for label in d.split('.'):
        if not label:
            return None
        if not label.isascii():
            label = 'xn--' + label.lower().encode('punycode').decode('ascii')
        labels.append(label)
    return '.'.join(labels)


def read_previous(path):
    """Liest die bisherige filter.txt: Regeln, Zeitstempel und kompletten Text."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        return None, None, None
    lines = text.splitlines()
    rules = [l for l in lines if l.startswith('||')]
    stamp = next((l.split(': ', 1)[1] for l in lines if l.startswith('! Generated:')), None)
    return rules, stamp, text


# 1) Ist data.csv ueberhaupt eine CSV? (HTML = Fehler-/Sperrseite)
with open(INPUT_FILE, 'r', encoding='utf-8-sig', errors='replace') as f:
    if f.read(512).lstrip().startswith('<'):
        fail('data.csv ist HTML (vermutlich Sperrseite von Cloudflare), keine CSV')

# 2) Domains einlesen und bereinigen: pro CSV-Zeile genau eine Regel. Auch Duplikate bleiben
#    erhalten, damit sich die Zeilenzahl mit der CSV vergleichen laesst. Nur Zeilen, die
#    keine Domain sind, werden uebersprungen.
rules = []
total = 0
with open(INPUT_FILE, 'r', encoding='utf-8-sig', newline='') as infile:
    for row in csv.reader(infile, delimiter=';'):
        if not row:
            continue
        total += 1
        domain = normalize(row[0])
        if domain:
            rules.append(f'||{domain}^|')

# 3) Plausibilitaet: lieber nichts aendern als eine kaputte Liste veroeffentlichen
if len(rules) < MIN_DOMAINS:
    fail(f'nur {len(rules)} gueltige Domains gefunden (Minimum {MIN_DOMAINS})')

# 4) Neuen Inhalt aufbauen; der Zeitstempel bleibt, wenn sich die Regeln nicht geaendert haben
old_rules, old_stamp, old_text = read_previous(OUTPUT_FILE)
now = datetime.now(timezone.utc).isoformat()
stamp = old_stamp if (old_rules == rules and old_stamp) else now

header = [
    '! Title: Inoffizielle Kopie - ÖIAT Watchlist Internet Filterlist',
    '! Source: https://www.watchlist-internet.at/liste-betruegerischer-shops/csv/',
    '! Disclaimer: Inoffizielle, automatisch erzeugte Kopie. Keine Verbindung zu ÖIAT Watchlist Internet. Keine Gewaehr fuer Richtigkeit und Vollstaendigkeit.',
    f'! Generated: {stamp}',
]
content = ''.join(line + '\n' for line in header + rules)

# 5) Nur schreiben, wenn sich wirklich etwas geaendert hat
if content == old_text:
    print(f'Keine Aenderungen ({len(rules)} Domains aus {total} Zeilen) - filter.txt wird nicht neu geschrieben')
    sys.exit(0)

with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
    outfile.write(content)

print(f'{len(rules)} Domains geschrieben (aus {total} Zeilen)')
