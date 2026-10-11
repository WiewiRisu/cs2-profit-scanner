import os
import json
import urllib.request
import urllib.error
import urllib.parse

api_key = os.environ.get('CSFLOAT_API_KEY')
if not api_key:
    raise SystemExit('Brak CSFLOAT_API_KEY')

params = urllib.parse.urlencode({
    'limit': 40,
    'sort_by': 'lowest_price',
    'max_price': 30,
    'type': 'buy_now',
    'category': 1,
})

url = 'https://csfloat.com/api/v1/listings?' + params
request = urllib.request.Request(url, headers={
    'Authorization': api_key,
    'Accept': 'application/json',
    'User-Agent': 'CS2ProfitHunter/2.0',
})

try:
    with urllib.request.urlopen(request, timeout=25) as response:
        data = json.load(response)
except urllib.error.HTTPError as error:
    raise SystemExit(f'Blad API: HTTP {error.code}')

listings = data.get('data', [])
print('Liczba ofert:', len(listings))
print('Czy API zwrocilo cursor:', bool(data.get('cursor')))
print('Dlugosc cursora:', len(str(data.get('cursor') or '')))
print('Dostepne pola odpowiedzi:', list(data.keys()))
print('Przykladowe typy:', sorted({str(x.get('item', {}).get('type')) for x in listings}))

seen = set()
for listing in listings:
    item = listing.get('item') or {}
    name = item.get('market_hash_name')
    if item.get('type') != 'skin' or not name or name in seen:
        continue
    seen.add(name)
    print(f"{name} | {listing.get('price', 0) / 100:.2f} USD")

print('Roznych skinow broni:', len(seen))
print('To byl tylko test. results.json pozostaje bez zmian.')
