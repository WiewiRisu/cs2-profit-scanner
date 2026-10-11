import os
import json
import urllib.request
import urllib.error

print("CS2 Profit Scanner - test CSFloat")

api_key = os.environ.get("CSFLOAT_API_KEY")

if not api_key:
    raise SystemExit(
        "Brak CSFLOAT_API_KEY w GitHub Actions."
    )

url = "https://csfloat.com/api/v1/listings?limit=5"

request = urllib.request.Request(
    url,
    headers={
        "Authorization": api_key,
        "User-Agent": "CS2ProfitScanner/1.0",
        "Accept": "application/json"
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
        name = item.get(
            "market_hash_name", "Nieznany skin"
        )

        price = listing.get("price", 0) / 100

        print(f"{name} - {price:.2f} USD")

except urllib.error.HTTPError as error:
    print(f"CSFloat HTTP error: {error.code}")

    if error.code == 401:
        print("Klucz API nie zostal zaakceptowany.")
    elif error.code == 403:
        print("CSFloat odmowil dostepu do API.")
    elif error.code == 429:
        print("Przekroczono limit zapytan.")
    else:
        print("Nie udalo sie pobrac ofert.")

except Exception as error:
    print(f"Blad pobierania danych: {error}")
