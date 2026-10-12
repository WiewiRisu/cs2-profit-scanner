
import os
import json
import time
import math
import urllib.error
import urllib.parse
import urllib.request

API_KEY = os.environ.get('CSFLOAT_API_KEY')
if not API_KEY:
    raise SystemExit('Brak klucza CSFLOAT_API_KEY')

BASE_URL = 'https://csfloat.com/api/v1/listings'
PAGE_SIZE = 40
USD_TO_PLN = 3.92

try:
    BUDGET_PLN = float(os.environ.get('BUDGET_PLN', '0.53').replace(',', '.'))
    RANGE_PLN = float(os.environ.get('RANGE_PLN', '0.30').replace(',', '.'))
except ValueError:
    raise SystemExit('Nieprawidlowe saldo lub zakres')

if not (
    math.isfinite(BUDGET_PLN)
    and math.isfinite(RANGE_PLN)
    and 0 <= BUDGET_PLN <= 1000
    and 0 <= RANGE_PLN <= 1000
):
    raise SystemExit('Nieprawidlowe wartosci PLN')

min_pln = max(0, BUDGET_PLN - RANGE_PLN)
max_pln = BUDGET_PLN + RANGE_PLN

min_cents = max(0, math.floor(min_pln / USD_TO_PLN * 100))
max_cents = math.ceil(max_pln / USD_TO_PLN * 100)

# Dzielimy caly przedzial na maksymalnie 5 grup cenowych.
# Na kazda grupe przypadaja maksymalnie 4 strony.
PRICE_GROUPS = 5
PAGES_PER_GROUP = 4

price_values = list(range(min_cents, max_cents + 1))
group_count = min(PRICE_GROUPS, len(price_values))
groups = []

for i in range(group_count):
    start = i * len(price_values) // group_count
    end = (i + 1) * len(price_values) // group_count
    chunk = price_values[start:end]
    groups.append((chunk[0], chunk[-1]))

cheapest_by_name = {}
seen_ids = set()

print('CS2 Profit Hunter - skanowanie skinow broni')
print(f'Saldo: {BUDGET_PLN:.2f} PLN')
print(f'Zakres: {min_pln:.2f} - {max_pln:.2f} PLN')
print(f'Grup cenowych: {len(groups)}')

for group_number, (group_min, group_max) in enumerate(groups, 1):
    print(
        f'Grupa {group_number}: '
        f'{group_min} - {group_max} centow USD'
    )

    cursor = None

    for page in range(1, PAGES_PER_GROUP + 1):
        params = {
            'limit': PAGE_SIZE,
            'sort_by': 'lowest_price',
            'min_price': group_min,
            'max_price': group_max,
            'type': 'buy_now',
            'category': 1,
        }

        if cursor:
            params['cursor'] = cursor

        url = BASE_URL + '?' + urllib.parse.urlencode(params)

        request = urllib.request.Request(
            url,
            headers={
                'Authorization': API_KEY,
                'Accept': 'application/json',
                'User-Agent': 'CS2ProfitHunter/3.0',
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as error:
            raise SystemExit(
                f'Blad CSFloat HTTP {error.code}, '
                f'grupa {group_number}, strona {page}'
            )
        except Exception as error:
            raise SystemExit(
                f'Blad pobierania: {error}'
            )

        listings = payload.get('data', [])
        print(
            f'Grupa {group_number}, '
            f'strona {page}: {len(listings)} ofert'
        )

        if not listings:
            break

        for listing in listings:
            item = listing.get('item') or {}
            name = item.get('market_hash_name')
            listing_id = listing.get('id')
            price = listing.get('price')

            if (
                item.get('type') != 'skin'
                or not name
                or not listing_id
                or not isinstance(price, int)
                or price <= 0
            ):
                continue

            # Zachowujemy tylko oferty w wybranym zakresie PLN.
            price_pln = price / 100 * USD_TO_PLN

            if not (min_pln <= price_pln <= max_pln):
                continue

            if listing_id in seen_ids:
                continue

            seen_ids.add(listing_id)

            previous = cheapest_by_name.get(name)

            if (
                previous is None
                or price < previous['price_cents']
            ):
                cheapest_by_name[name] = {
                    'name': name,
                    'price_cents': price,
                    'listing_id': listing_id,
                }

        next_cursor = payload.get('cursor')

        if not next_cursor or next_cursor == cursor:
            break

        cursor = next_cursor
        time.sleep(1)

results = [
    {
        'name': item['name'],
        'csfloat_price_usd': item['price_cents'] / 100,
        'listing_id': item['listing_id'],
    }
    for item in sorted(
        cheapest_by_name.values(),
        key=lambda item: (
            item['price_cents'],
            item['name'],
        ),
    )
]

with open('results.json.tmp', 'w', encoding='utf-8') as file:
    json.dump(
        results,
        file,
        ensure_ascii=False,
        indent=2,
    )

os.replace('results.json.tmp', 'results.json')

print(f'Roznych skinow: {len(results)}')
print(f'Unikalnych ofert: {len(seen_ids)}')
print('Zapisano results.json')
