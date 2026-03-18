import httpx

from fastapi import HTTPException


async def check_artic_existence(external_id: int):
    url = f"https://api.artic.edu/api/v1/artworks/{external_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=404,
                    detail=f"Place with ID {external_id} not found in Art Institute",
                )
            return response.json()
        except httpx.RequestError:
            raise HTTPException(
                status_code=503, detail=f"Art Institute API is unavailable"
            )
