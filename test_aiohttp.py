import asyncio
import aiohttp
import socket
import ssl
import certifi

async def main():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(
        family=socket.AF_INET,
        ssl=ssl_context,
        ttl_dns_cache=300
    )

    async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
        async with session.get("https://api.telegram.org/bot<ТВОЙ_ТОКЕН>/getMe", timeout=20) as resp:
            print(resp.status)
            print(await resp.text())

asyncio.run(main())