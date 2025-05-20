import aiofiles
import hashlib
import asyncio
# IPFS giả lập
async def upload_to_ipfs(filepath: str) -> str:
    async with aiofiles.open(filepath, "rb") as f:
        content = await f.read()
    cid = hashlib.sha256(content).hexdigest()
    await asyncio.sleep(0.1)
    return cid

# thật
# import httpx
# import os
# from dotenv import load_dotenv

# load_dotenv()
# TOKEN = os.getenv("WEB3_STORAGE_TOKEN")

# async def upload_to_ipfs(file_path: str) -> str:
#     async with httpx.AsyncClient() as client:
#         with open(file_path, "rb") as f:
#             files = {"file": f}
#             headers = {"Authorization": f"Bearer {TOKEN}"}
#             response = await client.post("https://api.web3.storage/upload", files=files, headers=headers)
#             response.raise_for_status()
#             cid = response.json()["cid"]
#             return cid