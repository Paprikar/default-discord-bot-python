import asyncio
from datetime import datetime
from datetime import timedelta
from os import path
from os import remove
from os import rename

import discord
from watchdog.events import FileCreatedEvent
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from bot.utils.utils import get_pics_path_list
from bot.utils.utils import time_in_range
from .module import Module


class PicsSendingModule(Module):

    def __init__(self, bot):
        self._log_prefix = f'{type(self).__name__}: '

        self.bot = bot
        self.to_close = asyncio.Event()
        self.tasks = {}
        self.monitoring_events = {}
        self.last_send_datetime = {}

    def run(self):
        for category_name in self.bot.config.pics_categories:
            modules = self.bot.config.pics_categories[category_name]['modules']
            if type(self).__name__ not in modules:
                continue

            monitoring_task = self.bot.loop.create_task(
                self._start_monitoring(category_name))
            self.tasks[monitoring_task] = None
            self.monitoring_events[category_name] = asyncio.Event()

            self.last_send_datetime[category_name] = None

            idle_event = asyncio.Event()
            idle_event.set()
            task = self.bot.loop.create_task(self._start(category_name))
            self.tasks[task] = idle_event

    async def _start(self, category_name):
        try:
            idle_event = self.tasks[asyncio.current_task()]

            while not (self.bot.client.is_closed() or self.to_close.is_set()):
                await self.bot.client.wait_until_ready()
                permit, cooldown = await self._time_check(category_name)
                await asyncio.sleep(cooldown)
                if permit:
                    idle_event.clear()
                    await self._send_pic(category_name)
                    if self.bot.config.db is not None:
                        dt = self.last_send_datetime[category_name]
                        try:
                            self._set_last_send_datetime_db(category_name, dt)
                        except Exception as e:
                            self.bot.logger.error(
                                self._log_prefix +
                                'Caught an exception of type '
                                f'`{type(e).__name__}` '
                                f'while setting a value in the database: {e}')
                    idle_event.set()
        except asyncio.CancelledError:
            pass

    async def _start_monitoring(self, category_name):
        observer = None

        try:
            category = self.bot.config.pics_categories[category_name]
            directory = category['send_directory']

            event_handler = _FileSystemEventHandler(
                directory,
                self.monitoring_events[category_name],
                self.bot.loop)

            observer = Observer()
            observer.schedule(event_handler, directory)
            observer.start()

            await self.to_close.wait()
            observer.stop()
            observer.join()
        except asyncio.CancelledError:
            if observer is not None and observer.is_alive():
                observer.stop()
                observer.join()

    async def _time_check(self, category_name):
        #  Returns: permit, cooldown
        category = self.bot.config.pics_categories[category_name]
        directory = category['send_directory']
        start = category['send_start']
        end = category['send_end']
        reserve_days = category['send_reserve_days']

        qsize = len(get_pics_path_list(directory))
        # Waiting for new pictures to be added
        if qsize == 0:
            await self.monitoring_events[category_name].wait()
            qsize = len(get_pics_path_list(directory))

        current_datetime = datetime.now()
        start_datetime = datetime.combine(current_datetime.date(), start)
        end_datetime = datetime.combine(current_datetime.date(), end)

        in_time = time_in_range(start, end, current_datetime.time())

        # DEBUG
        debug_msg = (
            self._log_prefix +
            '_time_check:'
            f'\n  category_name: {category_name}'
            f'\n  current_datetime: {current_datetime}')

        if in_time:
            # When it starts yesterday
            if current_datetime < start_datetime:
                start_datetime -= timedelta(days=1)
            # When it ends tomorrow
            if start_datetime >= end_datetime:
                end_datetime += timedelta(days=1)
        else:  # Wait for the next day
            # When it starts tomorrow
            if current_datetime > start_datetime:
                start_datetime += timedelta(days=1)
            cooldown = (start_datetime - current_datetime).total_seconds()
            # DEBUG
            debug_msg += (
                f'\n  target: {start_datetime}'
                f'\n  cooldown: {cooldown}'
                '\n  Wait for the next day.')
            self.bot.logger.debug(debug_msg)
            return (False, cooldown)

        if (self.last_send_datetime[category_name] is None and
                self.bot.config.db is not None):
            idle_event = self.tasks[asyncio.current_task()]
            idle_event.clear()
            try:
                dt = self._get_last_send_datetime_db(category_name)
            except Exception as e:
                self.bot.logger.error(
                    self._log_prefix +
                    f'Caught an exception of type `{type(e).__name__}` '
                    f'while getting a value from the database: {e}')
                dt = None
            idle_event.set()
            self.last_send_datetime[category_name] = dt

        last_send_datetime = self.last_send_datetime[category_name]
        if last_send_datetime is None or last_send_datetime < start_datetime:
            last_send_datetime = start_datetime

        # DEBUG
        debug_msg += (
            f'\n  start_datetime: {start_datetime}'
            f'\n  end_datetime: {end_datetime}'
            f'\n  last_send_datetime: {last_send_datetime}')

        seconds_per_day = (end_datetime - start_datetime).total_seconds()
        seconds_total = seconds_per_day * reserve_days
        seconds_left = (end_datetime - last_send_datetime).total_seconds()
        period_global = seconds_total / (qsize + reserve_days)
        # At least 1 picture per day
        period_global = min(period_global, seconds_per_day / 2)
        periods = max(seconds_left // period_global, 1)
        period = seconds_left / periods

        # DEBUG
        debug_msg += (
            f'\n  qsize: {qsize}'
            f'\n  seconds_per_day: {seconds_per_day}'
            f'\n  seconds_total: {seconds_total}'
            f'\n  seconds_left: {seconds_left}'
            f'\n  period_global: {period_global}'
            f'\n  periods: {periods}'
            f'\n  period: {period}')

        # Send immediately if it is late
        if current_datetime > last_send_datetime + timedelta(seconds=period):
            self.last_send_datetime[category_name] = current_datetime
            # DEBUG
            debug_msg += '\n  Send immediately if it is late.'
            self.bot.logger.debug(debug_msg)
            return (True, 0)

        # Skipping the end point of the day
        if current_datetime > end_datetime - timedelta(seconds=period):
            # Wait for the next day
            target = start_datetime + timedelta(days=1)
            cooldown = (target - current_datetime).total_seconds()
            # DEBUG
            debug_msg += (
                f'\n  target: {target}'
                f'\n  cooldown: {cooldown}'
                '\n  Skipping the end point of the day.')
            self.bot.logger.debug(debug_msg)
            return (False, cooldown)

        # Skipping the start point of the day
        if last_send_datetime == start_datetime:
            target = start_datetime + timedelta(seconds=period)
            self.last_send_datetime[category_name] = target
            cooldown = (target - current_datetime).total_seconds()
            # DEBUG
            debug_msg += (
                f'\n  target: {target}'
                f'\n  cooldown: {cooldown}'
                '\n  Skipping the start point of the day.')
            self.bot.logger.debug(debug_msg)
            return (True, cooldown)

        # Send at the next point
        target = last_send_datetime + timedelta(seconds=period)
        self.last_send_datetime[category_name] = target
        cooldown = (target - current_datetime).total_seconds()
        # DEBUG
        debug_msg += (
            f'\n  target: {target}'
            f'\n  cooldown: {cooldown}'
            '\n  Send at the next point.')
        self.bot.logger.debug(debug_msg)
        return (True, cooldown)

    def _get_last_send_datetime_db(self, category_name):
        import psycopg2

        conn = psycopg2.connect(**self.bot.config.db)
        cur = conn.cursor()

        # If the table does not exist
        statement = '''
            SELECT * FROM information_schema.tables
            WHERE table_name = 'pics_sending_module';
            '''
        cur.execute(statement)
        if not cur.rowcount:
            cur.close()
            conn.close()
            return None

        statement = '''
            SELECT last_send_datetime FROM pics_sending_module
            WHERE category_name = %s;
            '''
        cur.execute(statement, (category_name,))
        data = cur.fetchone()
        microseconds = None if data is None else data[0]

        if microseconds is None:
            cur.close()
            conn.close()
            return None

        timestamp = microseconds / 1e6
        dt = datetime.fromtimestamp(timestamp)

        cur.close()
        conn.close()
        return dt

    def _set_last_send_datetime_db(self, category_name, datetime):
        import psycopg2

        conn = psycopg2.connect(**self.bot.config.db)
        cur = conn.cursor()

        # Create a table if it does not exist
        statement = '''
            CREATE TABLE IF NOT EXISTS pics_sending_module (
                category_name varchar(255) PRIMARY KEY,
                last_send_datetime bigint);
            '''
        cur.execute(statement)

        statement = '''
            INSERT INTO pics_sending_module (category_name, last_send_datetime)
            VALUES (%(name)s, %(ts)s)
            ON CONFLICT (category_name) DO
                UPDATE
                SET last_send_datetime = %(ts)s;
            '''
        timestamp = (None if datetime is None
                     else round(datetime.timestamp() * 1e6))
        cur.execute(statement, {'name': category_name, 'ts': timestamp})

        conn.commit()
        cur.close()
        conn.close()

    async def _send_pic(self, category_name):
        category = self.bot.config.pics_categories[category_name]
        directory = category['send_directory']
        channel_id = category['send_channel_id']
        archive_directory = category['send_archive_directory']

        channel = self.bot.client.get_channel(channel_id)
        pics_path_list = get_pics_path_list(directory)

        if not pics_path_list:
            return False

        pic_path = self._select_pic(pics_path_list)
        try:
            file = discord.File(pic_path, filename=path.basename(pic_path))
            await channel.send(file=file)
            file.close()
        except Exception as e:
            self.bot.logger.error(
                self._log_prefix +
                f'Caught an exception of type `{type(e).__name__}` '
                f'while sending the picture: {e}')
            return False
        self.bot.logger.info(
            self._log_prefix +
            f'Sent a picture on the path: "{pic_path}".')

        if archive_directory is None:
            try:
                remove(pic_path)
            except OSError as e:
                self.bot.logger.error(
                    self._log_prefix +
                    f'Caught an exception of type `{type(e).__name__}` '
                    f'while removing file from disk: {e}')
        else:
            try:
                dst = path.join(archive_directory, path.basename(pic_path))
                rename(pic_path, dst)
            except OSError as e:
                self.bot.logger.error(
                    self._log_prefix +
                    f'Caught an exception of type `{type(e).__name__}` '
                    f'while moving file "{pic_path}" '
                    f'to the archive directory: {e}')

        return True

    @staticmethod
    def _select_pic(pics):
        #  Sort by file name
        pics = sorted(
            pics,
            key=lambda x: path.splitext(path.basename(x))[0])
        return pics[0]

    def stop(self, timeout=None):
        self.close_task = self.bot.loop.create_task(self._close(timeout))

    async def _close(self, timeout=None):
        try:
            self.to_close.set()
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
            for idle_event in self.tasks.values():
                if idle_event is not None:
                    idle_event.set()

    async def _task_closer(self, task):
        idle_event = self.tasks[task]
        if idle_event is not None:
            await idle_event.wait()
        task.cancel()


class _FileSystemEventHandler(FileSystemEventHandler):

    def __init__(self, directory, monitoring_event, loop):
        self.directory = directory
        self.monitoring_event = monitoring_event
        self.loop = loop
        self.prev_set = set()

    def on_created(self, event):
        if not isinstance(event, FileCreatedEvent):
            return

        curr_set = set(get_pics_path_list(self.directory))
        if curr_set - self.prev_set:
            self.loop.call_soon_threadsafe(self._event)
        self.prev_set = curr_set

    def _event(self):
        self.monitoring_event.set()
        self.monitoring_event.clear()
