import json
import urllib.request
import urllib.error

print("CS2 Profit Scanner - test CSFloat")

url = "https://csfloat.com/api/v1/listings?limit=5"

request = urllib.request.Request(
    url,
    headers={
        "User-Agent": "CS2ProfitScanner/1.0",
        "Accept": "application/json"
    }
)

try:
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)

    listings = data.get("data", [])

    print(f"Pobrano ofert: {len(listings)}")

    for listing in listings:
        item = listing.get("item", {})
        name = item.get("market_hash_name", "Nieznany skin")
        price = listing.get("price", 0) / 100

        print(f"{name} - {price:.2f} USD")

except urllib.error.HTTPError as error:
    print(f"CSFloat HTTP error: {error.code}")
    print("Moze byc wymagany klucz API.")

except Exception as error:
    print(f"Blad pobierania danych: {error}")
