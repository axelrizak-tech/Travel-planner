import httpx

BASE_URL = "https://api.artic.edu/api/v1"


async def validate_artwork_exists(external_id: int) -> bool:
    url = f"{BASE_URL}/artworks/{external_id}"
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.get(url)
    if resp.status_code != 200:
        return False
    data = resp.json().get("data")
    return bool(data)
