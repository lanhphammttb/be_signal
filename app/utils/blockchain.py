import hashlib
import asyncio
import uuid
# giả
async def write_to_blockchain(metadata: dict) -> str:
    import json
    await asyncio.sleep(0.2)
    return hashlib.sha256(json.dumps(metadata).encode()).hexdigest()

async def record_on_blockchain_mock(data: dict) -> str:
    """
    Giả lập gửi dữ liệu lên blockchain.
    Trả về tx_hash dạng chuỗi uuid giả để test.
    """
    await asyncio.sleep(1)  # Giả lập độ trễ mạng
    # Tạo tx_hash giả (uuid4)
    tx_hash = f"0x{uuid.uuid4().hex}"
    return tx_hash

async def record_license_transaction_mock(data: dict) -> str:
    """
    Giả lập ghi giao dịch mua quyền sử dụng bản quyền lên blockchain.
    """
    await asyncio.sleep(1)
    tx_hash = f"0x{uuid.uuid4().hex}"
    return tx_hash

# thật
# async def write_to_blockchain(metadata: dict) -> str:
#     data = json.dumps(metadata).encode("utf-8").hex()
#     nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)

#     tx = {
#         "nonce": nonce,
#         "to": PUBLIC_ADDRESS,
#         "value": 0,
#         "gas": 300000,
#         "gasPrice": w3.to_wei("10", "gwei"),
#         "data": "0x" + data,
#         "chainId": 137,
#     }

#     signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
#     return tx_hash.hex()

# def record_on_blockchain(data: dict) -> str:
#     """
#     Gửi dữ liệu lên blockchain thật và trả về tx_hash.
#     Giả định đã có smart contract sẵn để ghi bản quyền.
#     """
#     # Ở đây bạn nên thay thế bằng code gọi contract, ví dụ gọi API Web3 Gateway hoặc smart contract của bạn
#     # Đây là đoạn mock - bạn cần thay thế bằng Web3.py hoặc Alchemy/Infura/Web3 Gateway thực sự
#     response = requests.post("https://polygon-smartcontract-api.com/mint", json=data)
#     if response.status_code != 200:
#         raise Exception("Ghi blockchain thất bại")

#     tx_hash = response.json().get("transactionHash")
#     return tx_hash