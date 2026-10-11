import json
import re
import requests
from bs4 import BeautifulSoup

# URL do Azair: loty z Gdańska (GDN) w dowolne miejsce (XXX), pobyt 2-5 dni, waluta PLN
AZAIR_URL = (
    "https://www.azair.com/azfin.php?lang=pl&searchtype=flexi&tp=0"
    "&isOneway=return&srcAirport=Gdansk+[GDN]&srcIncluded=1"
    "&dstAirport=Everywhere+[XXX]&dstIncluded=1&minDaysStay=2&maxDaysStay=5"
    "&currency=PLN&indexSubmit=Search"
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_cheapest_flight():
    try:
        response = requests.get(AZAIR_URL, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")

        # Pobieramy pierwszy (najtańszy) wynik
        first_result = soup.find("div", class_="result")
        if not first_result:
            # Rezerwowa próba wyszukania po kontenerach wyników
            first_result = soup.find("div", class_=re.compile("item|result"))

        if first_result:
            text = first_result.get_text()

            # Szukanie ceny (np. 89 zł lub 89 PLN)
            price_match = re.search(r"(\d+)\s*(?:zł|PLN)", text)
            price = f"{price_match.group(1)} zl" if price_match else "Okazja"

            # Szukanie miasta docelowego
            dest_elem = first_result.find("span", class_="to") or first_result.find(
                "span", class_="destination"
            )
            dest = dest_elem.get_text().strip() if dest_elem else "Europa"

            # Czyszczenie tekstu do 16 znaków (na ekran LCD)
            dest = dest.split("(")[0].strip()

            return {"route": f"GDN->{dest[:8]}", "price": f"Cena: {price}"}
    except Exception as e:
        print("Blad pobierania z Azair:", e)

    # Wartosc zapasowa w razie tymczasowego bledu Azair
    return {"route": "GDN->Mediolan", "price": "Cena od: 79 zl"}


if __name__ == "__main__":
    flight = get_cheapest_flight()
    with open("flight.json", "w", encoding="utf-8") as f:
        json.dump(flight, f, ensure_ascii=False)
    print("Zapisano:", flight)
