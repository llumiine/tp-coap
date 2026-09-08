import asyncio
from aiocoap import Context, Message, resource
from aiocoap.numbers.codes import CONTENT


class Temperature(resource.Resource):
    def __init__(self):
        super().__init__()
        self.temperature = 22.5

    async def render_get(self, request):
        return Message(
            code=CONTENT,
            payload=f"{self.temperature:.1f} C".encode()
        )


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

    await Context.create_server_context(
        site,
        bind=("0.0.0.0", 5683)
    )

    print("SERVEUR COAP DEMARRE", flush=True)

    await update_temperature(temp)


asyncio.run(main())
