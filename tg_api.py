import asyncio
import logging

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
import math

import like_api
import view_api
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions

import db_funcs
from aiopg.sa import create_engine

import markups as nav

bot = Bot(token='5489920134:AAGkMf2P9b22kpAGkRWLV6QAd6b6jyIN85k')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    uid = message.from_user.id  # записал id
    uname = message.from_user.full_name  # имя
    person = {"name": uname, "tg_id": str(uid)}
    async with create_engine(user='postgres',
                             database='lab1',
                             host='127.0.0.1',
                             password='123456') as engine:
        if not await db_funcs.reg_check(engine, person["tg_id"]):
            await db_funcs.registration(engine, person)
            await message.reply("Регистрация успешно пройдена!", reply_markup=nav.mainMenu)
        else:
            await message.reply("Вы уже зарегистрированы. Переходим к меню", reply_markup=nav.mainMenu)


class Task_now:
    task_id = 0  # 1 - лайки, 2 - просмотры

    def choose_task(self, _task: int):
        self.task_id = _task

    def check_task(self):
        return self.task_id


task = Task_now()


@dp.message_handler()
async def echo_message(msg: types.Message):
    async with create_engine(user='postgres',
                             database='lab1',
                             host='127.0.0.1',
                             password='123456') as engine:
        if msg.text == "⬅️ Главное меню":
            task.choose_task(0)
            await bot.send_message(msg.from_user.id, "Вернулись в главное меню.", reply_markup=nav.mainMenu)

        # for main menu:
        elif msg.text == "🆕 ЗАКАЗ":
            task.choose_task(0)
            await bot.send_message(msg.from_user.id, "Выберите тип продвижения.", reply_markup=nav.orderMenu)
        elif msg.text == "ℹ️ Профиль":
            task.choose_task(0)
            uid = str(msg.from_user.id)
            balance = await db_funcs.get_balance(engine, str(msg.from_user.id))
            ans = "Информация:\nTelegram id: " + uid + "\nБаланс: " + str(
                balance) + "\nНа счет пополнения баланса писать: @chipolinka_gang"
            await bot.send_message(msg.from_user.id, ans)
        elif msg.text == "#️⃣ Статистика":
            uid = str(msg.from_user.id)
            get_like = await db_funcs.get_report(engine, uid, 1)
            get_view = await db_funcs.get_report(engine, uid, 2)
            task.choose_task(0)
            await bot.send_message(msg.from_user.id,
                                   "Статистика:\n\nЛайки:\nЗаказов: " + str(get_like['res_orders']) + " штук\nВсего: " +
                                   str(get_like['res_sum']) + " лайков\n\nПросмотры:\nЗаказов: " + str(
                                       get_view['res_orders']) + " штук\nВсего: " +
                                   str(get_view['res_sum']) + " просмотров")
        # for order menu:
        elif msg.text == "🔝 Лайки":
            task.choose_task(1)
            await bot.send_message(msg.from_user.id,
                                   "Введите ссылку и количество лайков через пробел.\nЦена 60 рублей за 1000 лайков\nПример:\nhttps://vk.com/wall-22822305_1307837 110",
                                   reply_markup=nav.orderMenu)
        elif msg.text == "👁‍🗨 Просмотры":
            task.choose_task(2)
            await bot.send_message(msg.from_user.id,
                                   "Введите ссылку и количество просмотров через пробел.\nЦена 10 рублей за 1000 просмотровl\nПример:\nhttps://vk.com/wall-22822305_1307837 3200",
                                   reply_markup=nav.orderMenu)
        elif msg.text[0:5] == "https":
            order_list = msg.text.split()
            if len(order_list) == 2 and int(order_list[1]) > 0:
                uid = str(msg.from_user.id)
                if task.check_task() == 1:
                    try:
                        sum = math.ceil(int(order_list[1]) / 1000 * 60)
                        if (await db_funcs.get_balance(engine, str(msg.from_user.id)) - sum) > 0:
                            like_api.make_like(str(uid), order_list[0], str(order_list[1]))
                            await bot.send_message(msg.from_user.id, "Задание успешно поставлено")
                            await db_funcs.new_order(engine, {"tg_id": uid, "type_id": task.check_task(), "url": order_list[0],
                                                      "value": order_list[1]})
                            await db_funcs.add_balance(engine, uid, -sum)
                        else:
                            await bot.send_message(msg.from_user.id, "Недостаточно средств.")

                    except Exception as ex:
                        await bot.send_message(msg.from_user.id, "Ошибка:" + str(ex))
                if task.check_task() == 2:
                    try:
                        sum = math.ceil(int(order_list[1]) / 1000 * 10)
                        if (await db_funcs.get_balance(engine, str(msg.from_user.id)) - sum) > 0:
                            view_api.make_view(order_list[0], str(order_list[1]))
                            await bot.send_message(msg.from_user.id, "Задание успешно поставлено")
                            await db_funcs.new_order(engine, {"tg_id": uid, "type_id": task.check_task(), "url": order_list[0],
                                                          "value": order_list[1]})
                            await db_funcs.add_balance(engine, uid, -sum)
                        else:
                            await bot.send_message(msg.from_user.id, "Недостаточно средств.")
                    except Exception as ex:
                        await bot.send_message(msg.from_user.id, "Ошибка:" + str(ex))
                if task.check_task() == 0:
                    await bot.send_message(msg.from_user.id, "Не выбран тип накрутки.")
            else:
                await bot.send_message(msg.from_user.id, "Неверный формат ввода.\nПример верного формата:\nhttps://vk.com/wall-22822305_1307837 3200\n(ссылка_на_пост, 1 пробел, количество)")

            # await bot.send_message(msg.from_user.id, "Тип задания: " + str(task.check_task()))
        else:
            await bot.send_message(msg.from_user.id, "Чтобы появилось меню, отправьте /start")


if __name__ == '__main__':
    executor.start_polling(dp)
