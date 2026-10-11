import os
import json
import urllib.request
import urllib.error
import urllib.parse

print("CS2 Profit Scanner - tanie oferty CSFloat")

api_key = os.environ.get("CSFLOAT_API_KEY")

if not api_key:
    raise SystemExit("Brak klucza API w GitHub Secrets.")

# Cena maksymalna w centach USD.
# 20 oznacza 0.20 USD, a NIE 0.20 PLN.
MAX_PRICE_CENTS = 20

params = urllib.parse.urlencode({
    "limit": 20,
    "sort_by": "lowest_price",
    "max_price": MAX_PRICE_CENTS,
    "type": "buy_now"
})

url = "https://csfloat.com/api/v1/listings?" + params

request = urllib.request.Request(
    url,
    headers={
        "Authorization": api_key,
        "User-Agent": "CS2ProfitScanner/1.1",
        "Accept": "application/json"
    }
)

try:
    with urllib.request.urlopen(
        request, timeout=20
    ) as response:
        data = json.load(response)

    listings = data.get("data", [])

    print(f"Znaleziono ofert: {len(listings)}")
    print("Ceny w USD. Limit: 0.20 USD.")
    print("-" * 40)

    for listing in listings:
        item = listing.get("item", {})
        name = item.get(
            "market_hash_name", "Nieznany przedmiot"
        )
        price_cents = listing.get("price", 0)
        price_usd = price_cents / 100
        listing_id = listing.get("id", "")

        print(f"{name} - {price_usd:.2f} USD")

        if listing_id:
            print(
                f"https://csfloat.com/item/{listing_id}"
            )

        print("-" * 40)

    if not listings:
        print("Brak ofert w wybranym przedziale.")

except urllib.error.HTTPError as error:
    print(f"CSFloat HTTP error: {error.code}")
    raise

except Exception as error:
    print(f"Blad pobierania: {error}")
    raise
