import asyncio
import httpx

async def fetch_account_balance(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    base_url: str,
    account_id: int,
    attempts: int = 3,
) -> dict:
    url = f"{base_url}/accounts/{account_id}"
    async with semaphore:
        for attempt in range(1, attempts + 1):
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError):
                if attempt == attempts:
                    raise
                await asyncio.sleep(attempt)
    raise RuntimeError("Failed to fetch account balance")

async def fetch_many_accounts_parallel(
    base_url: str,
    account_ids: list[int],
) -> list[dict]:
    semaphore = asyncio.Semaphore(5)
    async with httpx.AsyncClient(timeout=5.0) as client:
        tasks = [
            asyncio.create_task(
                fetch_account_balance(client, semaphore, base_url, acc_id)
            )
            for acc_id in account_ids
        ]
        return list(await asyncio.gather(*tasks))