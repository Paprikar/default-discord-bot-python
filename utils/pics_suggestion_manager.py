from aiohttp import web

from .manager import Manager


class PicsSuggestionManager(Manager):

    def __init__(self, category_name, bot):
        self.bot = bot

    def run(self):
        raise NotImplementedError

    async def start(self):
        msg = await request.text()
        print(msg)
        return web.Response(text='ANSWER')

    async def close(self):
        raise NotImplementedError
