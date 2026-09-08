import asyncio
from datetime import datetime, timezone

from aiocoap import Context, Message, resource
from aiocoap.numbers.codes import CONTENT


class TextResource(resource.Resource):
    def __init__(self, value):
        super().__init__()
        self.value = value

    async def render_get(self, request):
        return Message(code=CONTENT, payload=self.value().encode("utf-8"))


def current_time():
    return datetime.now(timezone.utc).isoformat()


def main():
    asyncio.run(run_server())


async def run_server():
    site = resource.Site()
    site.add_resource(["time"], TextResource(current_time))
    site.add_resource(["temp"], TextResource(lambda: "22.5 C"))
    site.add_resource(["light"], TextResource(lambda: "450 lux"))
    site.add_resource(["led"], TextResource(lambda: "off"))
    site.add_resource(["logs"], TextResource(lambda: "Aucun journal"))

    await Context.create_server_context(site, bind=("0.0.0.0", 5683))
    print("Serveur CoAP demarre sur le port 5683", flush=True)
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    main()
