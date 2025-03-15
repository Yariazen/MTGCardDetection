import argparse
import requests
import time
import unicodedata
import re
import json
from pathlib import Path

root = Path(".")
data_raw = root / "data" / "raw"

headers = {
    "User-Agent": "YariazenWebScaper/1.0.0"
}

def request(url, type="json", params=None):
    time.sleep(0.1)
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        raise

    match type:
        case "text":
            return response.text
        case "content":
            return response.content
        case "json":
            return response.json()
        case "image":
            return response


def slugify(text):
    value = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")

def fetch_cards(set_code):
    data_raw_set = data_raw / set_code
    data_raw_set.mkdir(parents=True, exist_ok=True)

    set_response = request(f"https://api.scryfall.com/sets/{set_code}")
    search_uri = set_response["search_uri"]

    search_response = request(search_uri)
    data = search_response["data"]
    for card in data:
        card_name = card["name"]
        card_slug = slugify(card_name)
        card_path = data_raw / set_code / f"{card_slug}.json"

        with open(card_path, "w") as f:
            json.dump(card, f, indent=4)

        card_image_url = card["image_uris"]["png"]
        card_image_path = data_raw / set_code / f"{card_slug}.png"
        with request(card_image_url, "image") as response:
            with open(card_image_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interface with the Scryfall API")
    parser.add_argument("--set", required=True, help="The set code to search for")
    args = parser.parse_args()

    fetch_cards(args.set)