import os
import json
import urllib.request
import urllib.error
import urllib.parse

print("CS2 Scanner - test skinow broni")

api_key = os.environ.get("CSFLOAT_API_KEY")

if not api_key:
    raise SystemExit("Brak klucza CSFLOAT_API_KEY")

params = urllib.parse.urlencode({
    "limit": 10,
    "sort_by": "lowest_price",
    "max_price": 20,
    "type": "buy_now",
    "market_hash_name": "P250 | Sand Dune (Field-Tested)"
})

url = "https://csfloat.com/api/v1/listings?" + params

request = urllib.request.Request(
    url,
    headers={
        "Authorization": api_key,
        "Accept": "application/json",
        "User-Agent": "CS2ProfitScanner/1.2"
    }
)

try:
    with urllib.request.urlopen(
        request, timeout=20
    ) as response:
        data = json.load(response)

    listings = data.get("data", [])

    print(f"Pobrano ofert: {len(listings)}")

    for listing in listings:
        item = listing.get("item", {})

        print("--------------------")
        print("Nazwa:", item.get("market_hash_name"))
        print("Weapon:", item.get("weapon"))
        print("Category:", item.get("category"))
        print("Type:", item.get("type"))
        print("Cena USD:", listing.get("price", 0) / 100)

except urllib.error.HTTPError as error:
    print("Blad HTTP:", error.code)
    raise

except Exception as error:
    print("Blad:", error)
    raise
