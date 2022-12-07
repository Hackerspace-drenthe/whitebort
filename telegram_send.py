

import logging
import platform
import threading

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

import secret_settings
import state
import asyncio

class TelegramBot(state.State):
    def __init__(self):
        super().__init__()

        # persistent state stuff
        state_file="bot.state"
        try:
            self.load(state_file)
        except Exception as e:
            logging.error(str(e))
            logging.info("Created new state file.")
            self.save(state_file)

        # update missing defaults
        self.defaults({
            'token': secret_settings.token,
            'joined_ids': []
        })



        # start background frame thread
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    async def on_startup(self,dispatcher, url=None, cert=None):
        # print(await self.bot.get_updates())
        # await self.send_message_joined("Started: {}".format(platform.node()))
        pass

    async def on_shutdown(self, dispatcher, url=None, cert=None):
        await self.send_message_joined("Stopped: {}".format(platform.node()))

    async def send_message_joined(self, text):
        """send message to all joined clients"""
        for chat_id in self.state.joined_ids:
            await self.bot.send_message(chat_id, text)

    async def _send_queued(self):
        while True:
            await asyncio.sleep(1)
            while len(self.task_queue)!=0:
                task=self.task_queue.pop()
                await task

    def send_message_joined_sync(self, text):
        self.task_queue.append(self.send_message_joined(text))

    def run(self):
        print("Telegram thread\n\n")

        # Initialize bot and dispatcher
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.bot = Bot(token=self.state.token, loop=self.loop)
        self.dp = Dispatcher(self.bot, loop=self.loop)
        self.task_queue=[]

        @self.dp.message_handler(commands=['join'])
        async def handle_join(message: types.Message):
            if message.chat.id in self.state.joined_ids:
                await message.reply("Already joined")
            else:
                self.state.joined_ids.append(message.chat.id)
                self.save()
                await message.reply("Joined {}".format(platform.node()))

        @self.dp.message_handler(commands=['join_channel'])
        async def handle_join_channel(message: types.Message):
            id=int(message.text.split(" ")[1])
            if id in self.state.joined_ids:
                await message.reply("Already joined")
            else:
                self.state.joined_ids.append(id)
                self.save()
                await message.reply("Joined {}".format(platform.node()))


        @self.dp.message_handler(commands=['leave'])
        async def handle_leave(message: types.Message):
            if message.chat.id in self.state.joined_ids:
                self.state.joined_ids.remove(message.chat.id)
                self.save()
                await message.reply("Left")

        @self.dp.message_handler(commands=['quit'])
        async def handle_quit(message: types.Message):
            await self.send_message_joined("quitting on request")
            await asyncio.sleep(1)
            self.loop.stop()


        self.loop.create_task(self._send_queued())
        executor.start_polling(self.dp, skip_updates=False, on_startup=self.on_startup, on_shutdown=self.on_shutdown,loop=self.loop)
