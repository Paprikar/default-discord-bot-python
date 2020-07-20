import asyncio
import os
from datetime import datetime
from datetime import timezone

import aiofiles
import aiohttp
import discord
from aiohttp import web

from .module import Module


class PicsSuggestionModule(Module):

    def __init__(self, bot):
        self._log_prefix = f'{type(self).__name__}: '

        self.bot = bot
        self.to_close = asyncio.Lock()

        categories_data = self.bot.config.pics_categories
        self.categories = {
            k for k in categories_data
            if type(self).__name__ in categories_data[k]['modules']}
        self.suggestion_info = {
            categories_data[k]['suggestion_channel_id']:
                (categories_data[k]['suggestion_directory'],
                 categories_data[k]['suggestion_positive'],
                 categories_data[k]['suggestion_negative'])
            for k in self.categories}

        self.server = web.Server(self._request_handler, loop=self.bot.loop)
        self.server_runner = web.ServerRunner(self.server)
        self.site = None

    def run(self):
        self.bot.loop.create_task(self._start())

    async def _start(self):
        await self.server_runner.setup()
        self.site = web.TCPSite(self.server_runner, '0.0.0.0', 21520)
        await self.site.start()

    def stop(self, timeout=None):
        self.close_task = self.bot.loop.create_task(self._close(timeout))

    async def _close(self, timeout):
        try:
            await self.to_close.acquire()
            await asyncio.wait_for(self._closer(timeout), timeout)
        except asyncio.TimeoutError:
            self.bot.logger.warning(
                self._log_prefix +
                'The execution was forcibly terminated by timeout.')

    async def _closer(self, timeout):
        try:
            await self.server.shutdown(timeout)
            await self.site.stop()
        except asyncio.CancelledError:  # on timeout
            await self.site.stop()

    async def _request_handler(self, request):
        try:
            if self.to_close.locked():
                msg = 'Suggestion service unavailable.'
                self.bot.logger.warning(self._log_prefix + msg)
                return web.Response(status=500, text=msg)

            json = await request.json()  # type: dict

            category = json.get('category', None)
            link = json.get('link', None)

            if (category is None or
                link is None or
                category not in self.categories or
                not isinstance(link, str)):
                msg = 'POST request has invalid data.'
                self.bot.logger.warning(self._log_prefix + msg)
                return web.Response(status=400, text=msg)

            timeout = json.get('timeout', None)
            if not (timeout is None or isinstance(timeout, (float, int))):
                timeout = None
                self.bot.logger.warning(
                    self._log_prefix +
                    'The POST request was received '
                    'with invalid timeout parameter.')
            try:
                await asyncio.wait_for(
                    self.bot.client.wait_until_ready(), timeout)
            except asyncio.TimeoutError:
                msg = ('The bot is not ready to process '
                       'the request at this time.')
                self.bot.logger.warning(self._log_prefix + msg)
                return web.Response(status=500, text=msg)

            category_data = self.bot.config.pics_categories[category]
            channel = self.bot.client.get_channel(
                category_data['suggestion_channel_id'])
            positive = category_data['suggestion_positive']
            negative = category_data['suggestion_negative']

            try:
                message = await channel.send(link)
                await message.add_reaction(positive)
                await message.add_reaction(negative)
            except (discord.HTTPException, discord.InvalidArgument) as e:
                msg = ('Caught an exception of type '
                       f'`discord.{type(e).__name__}` '
                       f'while sending the suggestion: {e}')
                self.bot.logger.error(self._log_prefix + msg)
                return web.Response(status=500, text=msg)

            return web.Response(text='OK')

        except asyncio.CancelledError:
            msg = ('The bot is not ready to process '
                   'the request at this time.')
            return web.Response(status=500, text=msg)

    async def reaction_handler(self, payload):
        if self.to_close.locked():
            self.bot.logger.warning(
                self._log_prefix +
                'Ignoring the reaction event: '
                '`reaction_handler` is already closed.')
            return

        if payload.user_id == self.bot.client.user.id:
            return  # Do not respond to bot actions

        await self.bot.client.wait_until_ready()

        channel = self.bot.client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        try:
            (
                directory,
                positive,
                negative,
            ) = self.suggestion_info[message.channel.id]
        except KeyError:
            return  # Respond only to actions in suggestion channels

        positive_count = 0
        negative_count = 0
        for reaction in message.reactions:
            if reaction.emoji == positive:
                positive_count = reaction.count - int(reaction.me)
            elif reaction.emoji == negative:
                negative_count = reaction.count - int(reaction.me)

        if positive_count > negative_count:
            is_saved = await self._save_file(message.content, directory)
            to_delete = is_saved
        elif negative_count > positive_count:
            self.bot.logger.info(
                self._log_prefix +
                f'Rejected a picture by URL: "{message.content}".')
            to_delete = True

        if to_delete:
            try:
                await message.delete()
            except discord.HTTPException:
                self.bot.logger.error(
                    self._log_prefix +
                    'Can not delete the message after approval.')

    async def _save_file(self, url, directory):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        self.bot.logger.error(
                            self._log_prefix +
                            'An error occurred while saving the picture: '
                            'The client received a response with the status '
                            f'`{response.status}` and with the message: '
                            f'"{await response.text()}".')
                        return False
                    now = datetime.now(timezone.utc).timestamp() * 1000
                    ext = os.path.splitext(url)[1]
                    if ext.lower() not in ('.png', '.jpg', '.jpeg'):
                        self.bot.logger.error(
                            self._log_prefix +
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
                        self._log_prefix +
                        f'Saved a picture by URL: "{url}" '
                        f'on the path: "{path}".')
        except Exception as e:
            self.bot.logger.error(
                self._log_prefix +
                f'Caught an exception of type `{type(e).__name__}` '
                f'while saving the picture: {e}')
            return False

        return True
