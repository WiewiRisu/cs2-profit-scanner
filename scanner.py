import os
import json
import time
import urllib.error
import urllib.parse
import urllib.request

API_KEY = os.environ.get('CSFLOAT_API_KEY')
if not API_KEY:
    raise SystemExit('Brak klucza CSFLOAT_API_KEY')

BASE_URL = 'https://csfloat.com/api/v1/listings'
PAGE_SIZE = 40
MAX_PAGES = 20

# Kurs orientacyjny USD -> PLN, taki sam jak na stronie
USD_TO_PLN = 3.92

try:
    BUDGET_PLN = float(os.environ.get('BUDGET_PLN', '0.53').replace(',', '.'))
    RANGE_PLN = float(os.environ.get('RANGE_PLN', '0.30').replace(',', '.'))
except ValueError:
    raise SystemExit('Nieprawidlowe saldo lub zakres')

if not (
    0 <= BUDGET_PLN <= 1000
    and 0 <= RANGE_PLN <= 1000
):
    raise SystemExit('Saldo i zakres musza byc poprawnymi kwotami PLN')

min_pln = max(0, BUDGET_PLN - RANGE_PLN)
max_pln = BUDGET_PLN + RANGE_PLN

# CSFloat przyjmuje ceny w centach USD
MIN_PRICE_CENTS = max(0, int(min_pln / USD_TO_PLN * 100))
MAX_PRICE_CENTS = max(
    MIN_PRICE_CENTS + 1,
    int(max_pln / USD_TO_PLN * 100 + 0.999999)
)

print(f'Saldo: {BUDGET_PLN:.2f} PLN')
print(f'Zakres: {min_pln:.2f} - {max_pln:.2f} PLN')
print(f'CSFloat: {MIN_PRICE_CENTS} - {MAX_PRICE_CENTS} centow USD')

cheapest_by_name = {}
seen_ids = set()
cursor = None

print('CS2 Profit Hunter - skanowanie skinow broni')

for page in range(1, MAX_PAGES + 1):
    params = {
        'limit': PAGE_SIZE,
        'sort_by': 'lowest_price',
        'min_price': MIN_PRICE_CENTS,
        'max_price': MAX_PRICE_CENTS,
        'type': 'buy_now',
        'category': 1,
    }
    if cursor:
        params['cursor'] = cursor

    url = BASE_URL + '?' + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={
        'Authorization': API_KEY,
        'Accept': 'application/json',
        'User-Agent': 'CS2ProfitHunter/2.1',
    })

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        raise SystemExit(f'Blad CSFloat HTTP {error.code} na stronie {page}')
    except Exception as error:
        raise SystemExit(f'Blad pobierania strony {page}: {error}')

    listings = payload.get('data', [])
    print(f'Strona {page}: {len(listings)} ofert')
    if not listings:
        break

    for listing in listings:
        item = listing.get('item') or {}
        name = item.get('market_hash_name')
        listing_id = listing.get('id')
        price = listing.get('price')
        if (item.get('type') != 'skin' or not name or not listing_id
                or not isinstance(price, int) or price <= 0):
            continue
        if listing_id in seen_ids:
            continue
        seen_ids.add(listing_id)
        previous = cheapest_by_name.get(name)
        if previous is None or price < previous['price_cents']:
            cheapest_by_name[name] = {
                'name': name,
                'price_cents': price,
                'listing_id': listing_id,
            }

    next_cursor = payload.get('cursor')
    if not next_cursor or next_cursor == cursor:
        break
    cursor = next_cursor
    if page < MAX_PAGES:
        time.sleep(1)

results = [
    {
        'name': item['name'],
        'csfloat_price_usd': item['price_cents'] / 100,
        'listing_id': item['listing_id'],
    }
    for item in sorted(
        cheapest_by_name.values(),
        key=lambda item: (item['price_cents'], item['name']),
    )
]

# Zapis atomowy: nie zostawiaj uszkodzonego JSON przy przerwaniu zapisu.
with open('results.json.tmp', 'w', encoding='utf-8') as file:
    json.dump(results, file, ensure_ascii=False, indent=2)
os.replace('results.json.tmp', 'results.json')

print(f'Roznych skinow: {len(results)}')
print(f'Unikalnych ofert: {len(seen_ids)}')
print('Zapisano results.json')
