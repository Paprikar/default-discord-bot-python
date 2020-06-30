import asyncio
import os
from datetime import datetime
from datetime import timezone

import aiofiles
import aiohttp
from aiohttp import web

from .module import Module


class PicsSuggestionModule(Module):

    def __init__(self, bot):
        self.bot = bot
        self.closable = asyncio.Event()
        self.closable.set()
        self.to_close = asyncio.Lock()

        categories = self.bot.pics_categories
        self.suggestion_info = {
            categories[k]['suggestion_channel_id']:
                (categories[k]['directory'],
                 categories[k]['suggestion_positive'],
                 categories[k]['suggestion_negative'])
            for k in self.bot.pics_categories}

        self.server = web.Server(self._request_handler)
        self.server_runner = web.ServerRunner(self.server)
        self.site = None


    def run(self):
        self.task = self.bot.loop.create_task(self.start())


    async def start(self):
        await self.server_runner.setup()
        self.site = web.TCPSite(self.server_runner, 'localhost', 21520)
        await self.site.start()


    async def close(self):
        await self.to_close.acquire()
        await self.closable.wait()
        await self.site.stop()
        await self.server.shutdown()
        self.task.cancel()


    async def _request_handler(self, request: web.Request):
        self.closable.clear()

        json = await request.json()

        if ('category' not in json
            or 'link' not in json
            or json['category'] not in self.bot.pics_categories
            or not isinstance(json['link'], str)):
            msg = 'POST request has incorrect data.'
            self.bot.logger.warning(msg)
            self.closable.set()
            return web.Response(status=501, text=msg)

        category = json['category']
        link = json['link']

        channel = self.bot.client.get_channel(
            self.bot.pics_categories[category]['suggestion_channel_id'])

        positive = self.bot.pics_categories[category]['suggestion_positive']
        negative = self.bot.pics_categories[category]['suggestion_negative']

        try:
            message = await channel.send(link)
            await message.add_reaction(positive)
            await message.add_reaction(negative)
        except Exception as e:
            self.bot.logger.error(
                f'Caught an exception of type `{type(e).__name__}` '
                f'in `PicsSuggestionModule._request_handler`: {e}')
            self.closable.set()
            return web.Response(status=500)

        self.closable.set()
        return web.Response(text='OK')


    async def reaction_handler(self, payload):
        self.closable.clear()

        channel = self.bot.client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if payload.user_id == self.bot.client.user.id:
            self.closable.set()
            return  # Do not respond to bot actions

        try:
            (
                directory,
                positive,
                negative,
            ) = self.suggestion_info[message.channel.id]
        except KeyError:
            self.closable.set()
            return  # Respond only to actions in suggestion channels

        positive_count = 0
        negative_count = 0
        for reaction in message.reactions:
            if reaction.emoji == positive:
                positive_count = reaction.count
            elif reaction.emoji == negative:
                negative_count = reaction.count

        if positive_count > negative_count:
            saved = await self._save_file(message.content, directory)
            to_delete = saved
        elif negative_count > positive_count:
            self.bot.logger.info(
                f'Rejected a picture by URL: "{message.content}".')
            to_delete = True

        if to_delete:
            try:
                await message.delete()
            except:
                self.bot.logger.error(
                    'Can not delete the message after approval.')

        self.closable.set()


    async def _save_file(self, url, directory):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        self.bot.logger.error(
                            'An error occurred while saving the picture: '
                            'The client received a response with the status '
                            f'{response.status}.')
                        return False
                    now = datetime.now(timezone.utc).timestamp() * 1000
                    ext = os.path.splitext(url)[1]
                    if ext.lower() not in ('.png', '.jpg', '.jpeg'):
                        self.bot.logger.error(
                            'An error occurred while saving the picture: '
                            'The URL should point to a file with one of the '
                            'following extensions: (".png", ".jpg", ".jpeg"), '
                            f'but got "{ext}".')
                        return False
                    file_name = str(round(now)) + ext
                    path = os.path.join(directory, file_name)
                    f = await aiofiles.open(path, mode='wb')
                    await f.write(await response.read())
                    await f.close()
                    self.bot.logger.info(
                        f'Saved a picture by URL: "{url}" '
                        f'on the path: "{path}".')
        except Exception as e:
            self.bot.logger.error(
                f'Caught an exception of type `{type(e).__name__}` '
                f'in `PicsSuggestionModule._save_file`: {e}')
            return False

        return True
