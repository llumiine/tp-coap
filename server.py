import asyncio
from datetime import datetime, timezone

from aiocoap import Context, Message, resource
from aiocoap.numbers.codes import CHANGED, CONTENT, CREATED


class TextResource(resource.Resource):
    """Ressource simple : GET seulement (ex: /time, /light)."""
    def __init__(self, value):
        super().__init__()
        self.value = value

    async def render_get(self, request):
        return Message(code=CONTENT, payload=self.value().encode("utf-8"))


class MutableResource(resource.Resource):
    """Ressource modifiable : GET + PUT + DELETE (ex: /temp, /led)."""
    def __init__(self, initial_value):
        super().__init__()
        self._value = initial_value

    async def render_get(self, request):
        return Message(code=CONTENT, payload=self._value.encode("utf-8"))

    async def render_put(self, request):
        self._value = request.payload.decode("utf-8")
        return Message(code=CHANGED)

    async def render_delete(self, request):
        self._value = ""
        return Message(code=CHANGED)


class LogsResource(resource.Resource):
    """Ressource /logs : GET (liste) + POST (ajouter une entrée)."""
    def __init__(self):
        super().__init__()
        self._entries = []

    async def render_get(self, request):
        text = "\n".join(self._entries) if self._entries else "Aucun journal"
        return Message(code=CONTENT, payload=text.encode("utf-8"))

    async def render_post(self, request):
        entry = request.payload.decode("utf-8")
        self._entries.append(entry)
        return Message(code=CREATED, payload=f"/logs/{len(self._entries)}".encode("utf-8"))


def current_time():
    return datetime.now(timezone.utc).isoformat()


def main():
    asyncio.run(run_server())


async def run_server():
    site = resource.Site()
    site.add_resource(["time"], TextResource(current_time))
    site.add_resource(["temp"], MutableResource("22.5 C"))
    site.add_resource(["light"], TextResource(lambda: "450 lux"))
    site.add_resource(["led"], MutableResource("off"))
    site.add_resource(["logs"], LogsResource())

    await Context.create_server_context(site, bind=("0.0.0.0", 5683))
    print("Serveur CoAP demarre sur le port 5683", flush=True)
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    main()