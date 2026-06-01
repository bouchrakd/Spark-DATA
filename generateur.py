import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_DIR = Path("data/stream")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


USERS = [f"usr_{i:04d}" for i in range(1, 51)]
SELLERS = [f"sel_{i:04d}" for i in range(1, 11)]
PRODUCTS = [f"prod_{i:04d}" for i in range(1, 31)]

CITIES = ["Paris", "Lyon", "Marseille", "Lille", "Bordeaux", "Toulouse", "Cergy"]
CATEGORIES = ["Vehicules", "Telephones", "Meubles", "Vetements", "Livres", "Sport"]
ACTIONS = ["AIME", "VOUT", "ACHAT"]


def create_event():
    product_id = random.choice(PRODUCTS)
    seller_id = random.choice(SELLERS)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": random.choice(USERS),
        "user_city": random.choice(CITIES),
        "product_id": product_id,
        "product_cat": random.choice(CATEGORIES),
        "seller_id": seller_id,
        "action_type": random.choices(
            ACTIONS,
            weights=[70, 20, 10],
            k=1
        )[0],
        "price": round(random.uniform(5, 2000), 2)
    }


def main():
    print("Générateur lancé...")
    print("Écriture des événements dans data/stream/")
    print("Appuie sur CTRL + C pour arrêter.")

    batch_number = 0

    while True:
        events = []

        for _ in range(10):
            events.append(create_event())

        file_path = OUTPUT_DIR / f"events_{batch_number}.json"

        with open(file_path, "w", encoding="utf-8") as file:
            for event in events:
                file.write(json.dumps(event) + "\n")

        print(f"Fichier créé : {file_path}")

        batch_number += 1
        time.sleep(5)


if __name__ == "__main__":
    main()
