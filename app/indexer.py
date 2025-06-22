import os
import asyncio
import datetime
import logging

from web3 import Web3
from web3.middleware import geth_poa_middleware
from hexbytes import HexBytes

from sqlalchemy import select

from .db import async_session
from .models import Transfer


RPC_URL = os.getenv("RPC_URL")
TOKEN_ADDRESS = Web3.to_checksum_address(os.getenv("TOKEN_ADDRESS"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 10))

w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

TRANSFER_TOPIC = w3.keccak(text="Transfer(address,address,uint256)").hex()

logger = logging.getLogger("indexer")
logger.setLevel(logging.INFO)


async def store_transfer(ev):
    async with async_session() as session:
        # check for existing record
        stmt = select(Transfer).where(Transfer.tx_hash == ev["transactionHash"].hex())
        result = await session.execute(stmt)
        if result.scalars().first():
            return

        # parse the transfer value
        raw = ev["data"]
        if isinstance(raw, (bytes, bytearray)):
            amount = int.from_bytes(raw, "big")
        else:
            amount = int(raw, 16)

        tr = Transfer(
            tx_hash=ev["transactionHash"].hex(),
            frm="0x" + ev["topics"][1].hex()[-40:],
            to="0x" + ev["topics"][2].hex()[-40:],
            value=str(amount),
            block_number=ev["blockNumber"],
            timestamp=datetime.datetime.utcnow(),
        )
        session.add(tr)
        await session.commit()


async def run_indexer(stop_event: asyncio.Event):
    # 1) backfill the very last block so we don’t skip anything
    head = w3.eth.block_number
    latest = head - 1 if head > 0 else 0
    logger.info(f"Starting indexer from block {latest + 1}")

    while not stop_event.is_set():
        # 2) refresh head each loop
        head = w3.eth.block_number
        from_block = latest + 1
        to_block = head

        if from_block <= to_block:
            try:
                logs = w3.eth.get_logs(
                    {
                        "fromBlock": from_block,
                        "toBlock": to_block,
                        "address": TOKEN_ADDRESS,
                        "topics": [TRANSFER_TOPIC],
                    }
                )
                print(f"Fetched {len(logs)} logs from blocks {from_block}–{to_block}")

                # 3) store each event
                for ev in logs:
                    await store_transfer(ev)

                # 4) advance the pointer
                latest = to_block

            except Exception as e:
                logger.error(f"Error fetching logs: {e}")
