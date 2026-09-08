import asyncio
from datetime import datetime, timezone

from aiocoap import Context, Message, resource
from aiocoap.numbers.codes import CHANGED, CONTENT, CREATED


class TextResource(resource.Resource):
    """Ressource simple : GET seulement (ex: /time, /light)."""
    def __init__(self, value, rt=None):
        super().__init__()
        self.value = value
        self.rt = rt

    async def render_get(self, request):
        return Message(code=CONTENT, payload=self.value().encode("utf-8"))

    def get_link_description(self):
        desc = super().get_link_description()
        if self.rt:
            desc["rt"] = self.rt
        return desc


class MutableResource(resource.Resource):
    """Ressource modifiable : GET + PUT + DELETE (ex: /led, /sensors/...)."""
    def __init__(self, initial_value, rt=None):
        super().__init__()
        self._value = initial_value
        self.rt = rt

    async def render_get(self, request):
        return Message(code=CONTENT, payload=self._value.encode("utf-8"))

    async def render_put(self, request):
        self._value = request.payload.decode("utf-8")
        return Message(code=CHANGED)

    async def render_delete(self, request):
        self._value = ""
        return Message(code=CHANGED)

    def get_link_description(self):
        desc = super().get_link_description()
        if self.rt:
            desc["rt"] = self.rt
        return desc


class LogsResource(resource.Resource):
    """Ressource /logs : GET (liste) + POST (ajouter une entree)."""
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


class BigLogResource(resource.Resource):
    """Ressource /biglog : stocke un contenu volumineux (test blockwise)."""
    def __init__(self):
        super().__init__()
        self._content = ""

    async def render_get(self, request):
        return Message(code=CONTENT, payload=self._content.encode("utf-8"))

    async def render_put(self, request):
        self._content = request.payload.decode("utf-8")
        return Message(code=CHANGED)

    def get_link_description(self):
        desc = super().get_link_description()
        desc["rt"] = "biglog"
        return desc


class Temperature(resource.Resource):
    """Ressource /temp : GET/PUT/DELETE, plus mise a jour automatique
    (boucle) pour la demonstration d'observation du module 2."""
    def __init__(self):
        super().__init__()
        self.temperature = 22.5

    async def render_get(self, request):
        return Message(code=CONTENT, payload=f"{self.temperature:.1f} C".encode())

    async def render_put(self, request):
        self.temperature = float(request.payload.decode("utf-8"))
        return Message(code=CHANGED)

    async def render_delete(self, request):
        self.temperature = 0.0
        return Message(code=CHANGED)

    def get_link_description(self):
        desc = super().get_link_description()
        desc["rt"] = "temperature"
        return desc


def current_time():
    return datetime.now(timezone.utc).isoformat()


async def update_temperature(temp):
    print("BOUCLE TEMPERATURE DEMARREE", flush=True)

    while True:
        await asyncio.sleep(2)

        temp.temperature += 0.5

        if temp.temperature > 25:
            temp.temperature = 22.5

        print(
            f"Mise à jour température : {temp.temperature:.1f} C",
            flush=True
        )


async def main():
    site = resource.Site()

    temp = Temperature()
    site.add_resource(["temp"], temp)
    site.add_resource(["time"], TextResource(current_time, rt="time"))
    site.add_resource(["light"], TextResource(lambda: "450 lux", rt="light"))
    site.add_resource(["led"], MutableResource("off", rt="led"))
    site.add_resource(["logs"], LogsResource())
    site.add_resource(["biglog"], BigLogResource())

    # Arborescence de ressources imbriquees (module 3)
    site.add_resource(["sensors", "room1", "temperature"], MutableResource("23.5", rt="temperature"))
    site.add_resource(["sensors", "room1", "humidity"], MutableResource("55", rt="humidity"))
    site.add_resource(["sensors", "room1", "light"], MutableResource("150", rt="light"))

    # Decouverte standard CoAP (module 3)
    site.add_resource(
        [".well-known", "core"],
        resource.WKCResource(site.get_resources_as_linkheader),
    )

    await Context.create_server_context(
        site,
        bind=("0.0.0.0", 5683)
    )

    print("SERVEUR COAP DEMARRE", flush=True)

    await update_temperature(temp)


asyncio.run(main())
