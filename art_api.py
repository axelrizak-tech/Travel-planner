import requests

ART_API_URL = "https://api.artic.edu/api/v1/artworks/"

def validate_place(external_id: str) -> dict:
    response = requests.get(f"{ART_API_URL}{external_id}")
    if response.status_code != 200:
        return None
    data = response.json()["data"]
    return {
        "external_id": external_id,
        "title": data.get("title", "Unknown")
    }
