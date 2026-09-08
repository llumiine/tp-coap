import asyncio
import sys

from aiocoap import Context, Message
from aiocoap.numbers.codes import GET, POST, PUT, DELETE

METHODS = {
    "get": GET,
    "put": PUT,
    "post": POST,
    "delete": DELETE,
}


async def request(method_name, path, payload=None):
    protocol = await Context.create_client_context()
    try:
        code = METHODS[method_name.lower()]
        kwargs = {"code": code, "uri": f"coap://coap-server:5683/{path}"}
        if payload is not None:
            kwargs["payload"] = payload.encode("utf-8")
        message = Message(**kwargs)
        response = await protocol.request(message).response
        body = response.payload.decode("utf-8") if response.payload else ""
        print(f"{response.code}: {body}")
    finally:
        await protocol.shutdown()


if __name__ == "__main__":
    args = sys.argv[1:]
    method = args[0] if len(args) > 0 else "get"
    path = args[1] if len(args) > 1 else "time"
    payload = args[2] if len(args) > 2 else None
    asyncio.run(request(method, path, payload))