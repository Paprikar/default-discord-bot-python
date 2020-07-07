import asyncio
import os
from datetime import datetime
from os import path

import discord

from .module import Module
from ..utils.utils import get_pics_path_list


class PicsSendingModule(Module):

    def __init__(self, bot):
        self._log_prefix = f'{type(self).__name__}: '

        self.bot = bot
        self.to_close = asyncio.Lock()
        self.tasks = {}

    def run(self):
        for category_name in self.bot.pics_categories:
            modules = self.bot.pics_categories[category_name]['modules']
            if type(self).__name__ not in modules:
                continue
            event = asyncio.Event()
            event.set()
            task = self.bot.loop.create_task(self.start(category_name))
            self.tasks[task] = event

    async def start(self, category_name):
        try:
            current_task = asyncio.current_task()
            category = self.bot.pics_categories[category_name]
            send_directory = category['send_directory']
            send_channel_id = category['send_channel_id']
            send_time = category['send_time']
            send_archive_directory = category['send_archive_directory']

            while not (self.bot.client.is_closed() or self.to_close.locked()):
                await self.bot.client.wait_until_ready()
                (
                    permit,
                    send_cooldown,
                    resend_cooldown,
                ) = self._time_check(send_time)

                if permit:
                    self.tasks[current_task].clear()
                    is_sended = await self._send_pic(
                        send_channel_id,
                        send_directory,
                        send_archive_directory)
                    self.tasks[current_task].set()

                    sleep_time = (send_cooldown if is_sended
                                  else resend_cooldown)
                else:
                    sleep_time = resend_cooldown

                await asyncio.sleep(sleep_time)
        except asyncio.CancelledError:
            pass

    def stop(self, timeout=None):
        self.close_task = self.bot.loop.create_task(self.close(timeout))

    async def close(self, timeout=None):
        try:
            await self.to_close.acquire()
            await asyncio.wait_for(self._closer(), timeout)
        except asyncio.TimeoutError:
            self.bot.logger.error(
                self._log_prefix +
                'The execution was forcibly terminated by timeout.')

    async def _closer(self):
        try:
            for task in self.tasks:
                self.bot.loop.create_task(self._task_closer(task))
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:  # on timeout
            for event in self.tasks.values():
                event.set()

    async def _task_closer(self, task):
        await self.tasks[task].wait()
        task.cancel()

    @staticmethod
    def _time_check(send_time):
        #  Returns: permit, send_cooldown, resend_cooldown
        current_time = datetime.strftime(datetime.now(), '%H:%M')
        if current_time in send_time:
            return (True, 60, 1)
        else:
            return (False, 60, 1)

    async def _send_pic(self, channel_id, directory, archive_directory):
        channel = self.bot.client.get_channel(channel_id)
        pics_path_list = get_pics_path_list(directory)

        if not pics_path_list:
            return False

        pic_path = self._select_pic(pics_path_list)
        pass_flag = False
        try:
            file = discord.File(pic_path, filename=path.basename(pic_path))
            await channel.send(file=file)
            pass_flag = True
            self.bot.logger.info(
                self._log_prefix +
                f'Sent a picture on the path: "{pic_path}".')
            file.close()
            if archive_directory is None:
                try:
                    os.remove(pic_path)
                except OSError as e:
                    self.bot.logger.error(
                        self._log_prefix +
                        f'Can not remove "{pic_path}" file from disk: {e}')
            else:
                try:
                    dst = path.join(archive_directory, path.basename(pic_path))
                    os.rename(pic_path, dst)
                except OSError as e:
                    self.bot.logger.error(
                        self._log_prefix +
                        f'Can not move "{pic_path}" file '
                        f'to the archive directory: {e}')
        except Exception as e:
            self.bot.logger.error(
                self._log_prefix +
                f'Caught an exception of type `{type(e).__name__}` '
                f'while sending the picture: {e}')
        return pass_flag

    @staticmethod
    def _select_pic(pics):
        #  Sort by file name
        pics = sorted(
            pics,
            key=lambda x: path.splitext(path.basename(x))[0])
        return pics[0]
