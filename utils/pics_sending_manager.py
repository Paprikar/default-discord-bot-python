import asyncio
import os
from datetime import datetime
from os import path

import discord

from .manager import Manager
from .utils import get_pics_path_list


class PicsSendingManager(Manager):

    def __init__(self, category_name, bot):
        self.bot = bot
        self.closable = asyncio.Event()
        self.closable.set()
        self.to_close = asyncio.Lock()

        category = bot.pics_categories[category_name]
        self.channel_id = category['channel_id']
        self.pics_directory = category['pictures_directory']
        self.pics_send_time = category['pictures_send_time']

    def run(self):
        self.task = self.bot.loop.create_task(self.start())

    async def start(self):
        await self.bot.client.wait_until_ready()

        try:
            while not (self.bot.client.is_closed() or self.to_close.locked()):
                (
                    permit,
                    send_cooldown,
                    resend_cooldown,
                ) = self._send_pic_time_check()

                if permit:
                    self.closable.clear()
                    is_sended = await self._send_pic()
                    self.closable.set()
                    sleep_time = (send_cooldown if is_sended
                                  else resend_cooldown)
                else:
                    sleep_time = resend_cooldown

                await asyncio.sleep(sleep_time)
        except asyncio.CancelledError:
            pass

    async def close(self):
        await self.to_close.acquire()
        await self.closable.wait()
        self.task.cancel()

    def _send_pic_time_check(self):
        #  Returns: permit, send_cooldown, resend_cooldown
        current_time = datetime.strftime(datetime.now(), '%H:%M')
        if current_time in self.pics_send_time:
            return True, 60, 1
        else:
            return False, 60, 1

    async def _send_pic(self):
        channel = self.bot.client.get_channel(self.channel_id)
        pics_path_list = get_pics_path_list(self.pics_directory)

        if not pics_path_list:
            return False

        pic_path = self._select_pic(pics_path_list)
        pass_flag = False
        try:
            file = discord.File(pic_path, filename=path.basename(pic_path))
            await channel.send(file=file)
            pass_flag = True
            self.bot.logger.info(
                f'Sent a picture on the path: "{pic_path}".')
            file.close()
            try:
                os.remove(pic_path)
            except:
                self.bot.logger.error(
                    f'Can not remove "{pic_path}" file from disk.')
        except Exception as e:
            self.bot.logger.error(
                f'Caught an exception of type `{type(e).__name__}`: {e}')
        return pass_flag

    @staticmethod
    def _select_pic(pics):
        #  Sort by file name
        pics = sorted(
            pics,
            key=lambda x: path.splitext(path.basename(x))[0])
        return pics[0]
