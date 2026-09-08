import asyncio
import sys

from aiocoap import Context, Message
from aiocoap.numbers.codes import GET


async def request(path):
    protocol = await Context.create_client_context()
    try:
        message = Message(code=GET, uri=f"coap://coap-server:5683/{path}")
        response = await protocol.request(message).response
        print(f"{response.code}: {response.payload.decode('utf-8')}")
    finally:
        await protocol.shutdown()


if __name__ == "__main__":
    asyncio.run(request(sys.argv[1] if len(sys.argv) > 1 else "time"))
