from aiogram import Bot,Dispatcher,executor,types
import aller_cfg as ac
import os
import logging
import sqlite3
import time

import config as cfg

logging.basicConfig(level=logging.INFO)


BASE_DIR = os.path.dirname(os.path.abspath("database.db"))
db_path = os.path.join(BASE_DIR)


class Database:
    def __init__(self,path,db_file):
        path = os.chdir(path)
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def user_exists(self,user_id):
        with self.connection:
           result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?",(user_id,)).fetchall()
           return bool(len(result))

    def add_user(self,user_id):
        with self.connection:
            return self.connection.execute("INSERT INTO `users` (`user_id`) VALUES (?)",(user_id,))

    def mute(self, user_id):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?",(user_id,)).fetchone()
            return int(user[2]) >= int(time.time())

    def add_mute(self,user_id,mute_time):
        with self.connection:
            return self.connection.execute("UPDATE `users` SET `mute_time` = ? WHERE `user_id` = ?",(int(time.time()) + mute_time, user_id,))



bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)
db = Database(db_path,"database.db")

@dp.message_handler(commands=["start"], commands_prefix ="!")
async def start(message: types.Message):
    await message.answer("idi nahuy ya rabotat ne budu")

@dp.message_handler(commands=["all"], commands_prefix ="!")
async def all(message: types.Message):
    await message.answer(",".join(ac.cheliks))


@dp.message_handler(commands=["mute"], commands_prefix = "!")
async def add_mut(message: types.Message):
    if str(message.from_user.id) == cfg.ADMIN_ID:
        if not message.reply_to_message:
            await message.reply("эта команда должна быть в ответе на сообнение")
            return
    mute_sec = int(message.text[6:])
    db.add_mute(message.reply_to_message.from_user.id, mute_sec)
    while(db.mute(message.from_user.id)):
        result: bool = await bot.delete_message(...)
    await message.reply_to_message.reply(f"Довыебывался")

@dp.message_handler()
async def get_warn(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)

    if db.mute(message.from_user.id):
        await message.delete()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)