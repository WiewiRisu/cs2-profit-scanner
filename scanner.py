import os
import json
import urllib.request
import urllib.error
import urllib.parse
import time

print("CS2 Profit Scanner - skiny broni")
print("=" * 45)

api_key = os.environ.get("CSFLOAT_API_KEY")

if not api_key:
    raise SystemExit("Brak klucza CSFLOAT_API_KEY")

# Skórki, które chcemy sprawdzać
SKINS = [
    "P250 | Sand Dune (Field-Tested)",
    "Glock-18 | Death Rattle (Field-Tested)",
    "P250 | Sand Dune (Battle-Scarred)",
    "Glock-18 | Death Rattle (Battle-Scarred)",
]

# Maksymalna cena: 20 centów USD
MAX_PRICE_CENTS = 20

results = []

for skin_name in SKINS:
    print()
    print("Sprawdzam:", skin_name)

    params = urllib.parse.urlencode({
        "limit": 10,
        "sort_by": "lowest_price",
        "max_price": MAX_PRICE_CENTS,
        "type": "buy_now",
        "market_hash_name": skin_name
    })

    url = "https://csfloat.com/api/v1/listings?" + params

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": api_key,
            "Accept": "application/json",
            "User-Agent": "CS2ProfitScanner/1.3"
        }
    )

    try:
        with urllib.request.urlopen(
            request, timeout=20
        ) as response:
            data = json.load(response)

        listings = data.get("data", [])

        # Zostawiamy tylko właściwe skiny
        valid = [
            listing
            for listing in listings
            if listing.get("item", {}).get("type") == "skin"
            and listing.get("item", {}).get(
                "market_hash_name"
            ) == skin_name
        ]

        if not valid:
            print("Brak ofert w limicie.")
            continue

        cheapest = min(
            valid,
            key=lambda listing: listing["price"]
        )

        price_cents = cheapest["price"]
        price_usd = price_cents / 100

        print(f"Najtansza oferta: {price_usd:.2f} USD")
        print(f"Liczba ofert: {len(valid)}")

        result = {
            "name": skin_name,
            "csfloat_price_usd": price_usd,
            "listing_id": cheapest.get("id")
        }

        results.append(result)

    except urllib.error.HTTPError as error:
        print(f"Blad CSFloat HTTP: {error.code}")
        raise

    except Exception as error:
        print(f"Blad: {error}")
        raise

    # Krotka przerwa miedzy zapytaniami
    time.sleep(1)

print()
print("=" * 45)
print(f"Znaleziono skinow: {len(results)}")

for result in results:
    print(
        f"{result['name']} -> "
        f"{result['csfloat_price_usd']:.2f} USD"
    )

# Zapisujemy wyniki do pliku JSON
with open("results.json", "w", encoding="utf-8") as file:
    json.dump(
        results,
        file,
        ensure_ascii=False,
        indent=2
    )

print("Zapisano results.json")
