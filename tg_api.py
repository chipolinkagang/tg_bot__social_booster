import asyncio
import logging

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher, FSMContext
import math

import config
import like_api
import like_snebes_3
import pay_yoomoney
import repost_likest4
import view_api
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions, InlineKeyboardButton, \
    InlineKeyboardMarkup

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import time

import db_funcs
from aiopg.sa import create_engine

import markups as nav
from aiogram.dispatcher.filters.state import StatesGroup, State

class Mail(StatesGroup):
    mail = State()

bot = Bot(token='5530817308:AAGVgvbqKPK2mryMkoGOcWSWndr4oOXkdrA')
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    uid = message.from_user.id  # записал id
    uname = message.from_user.full_name  # имя
    person = {"name": uname, "tg_id": str(uid)}
    async with create_engine(user=config.datab["user"],
                             database=config.datab["database"],
                             host=config.datab["host"],
                             password=config.datab["password"]) as engine:
        if not await db_funcs.reg_check(engine, person["tg_id"]):
            await db_funcs.registration(engine, person)
            await message.reply("Регистрация успешно пройдена!", reply_markup=nav.mainMenu)
        else:
            await message.reply("Вы уже зарегистрированы. Переходим к меню", reply_markup=nav.mainMenu)


# class Task_now:
#     task_id = 0  # 1 - лайки, 2 - просмотры
#
#     def choose_task(self, _task: int):
#         self.task_id = _task
#
#     def check_task(self):
#         return self.task_id
#
#
# task = Task_now()

@dp.callback_query_handler(lambda c: c.data == 'make_pay_button')
async def process_callback_make_pay_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    async with create_engine(user=config.datab["user"],
                             database=config.datab["database"],
                             host=config.datab["host"],
                             password=config.datab["password"]) as engine:
        await db_funcs.set_now_task(engine, str(callback_query.from_user.id), "1000")
    await bot.send_message(callback_query.from_user.id, 'Введите сумму для пополнения с карты:')


@dp.callback_query_handler(lambda c: c.data == 'check_pay_button')
async def process_callback_check_pay_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    async with create_engine(user=config.datab["user"],
                             database=config.datab["database"],
                             host=config.datab["host"],
                             password=config.datab["password"]) as engine:
        labels = await db_funcs.check_payment_labels(engine, str(callback_query.from_user.id))
        for label in labels:
            if await pay_yoomoney.check_payment(label):
                payment_info = await db_funcs.get_payment(engine, label)
                await db_funcs.delete_payment_label(engine, label)
                await db_funcs.add_balance(engine, payment_info["tg_id"], payment_info["sum"])
                await bot.send_message(callback_query.from_user.id,
                                       "Успешное пополнение баланса # " + label + ".\nЗачислено: " + str(
                                           payment_info["sum"]))
            else:
                await bot.send_message(callback_query.from_user.id, "Пополнение #" + label + " не завершено.")


@dp.message_handler(commands=['mail'], user_id=config.ADMIN_ID, state='*')
async def mail(message: types.Message):
    await message.answer(
        'Отправьте сообщение для рассылки:'
    )
    await Mail.mail.set()

@dp.message_handler(state=Mail.mail, content_types=types.ContentType.ANY)
async def mail_on(message: types.Message, state: FSMContext):
    async with create_engine(user=config.datab["user"],
                             database=config.datab["database"],
                             host=config.datab["host"],
                             password=config.datab["password"]) as engine:
        select_users = await db_funcs.get_all(engine)
    await state.reset_state(with_data=False)
    if types.ContentType.TEXT == message.content_type: # Если админ отправил текст
        for user in select_users:
            try:
                await bot.send_message(
                    chat_id=int(user),
                    text=message.html_text
                )
                await asyncio.sleep(0.33)
            except Exception:
                pass
        else:
            await message.answer(
                '<b> Рассылка завершена!</b>'
            )

    elif types.ContentType.PHOTO == message.content_type: # Если админ отправил фото
        for user in select_users:
            try:
                await bot.send_photo(
                    chat_id=int(user),
                    photo=message.photo[-1].file_id,
                    caption=message.html_text if message.caption else None
                )
                await asyncio.sleep(0.33)
            except Exception:
                pass
        else:
            await message.answer(
                '<b> Рассылка завершена!</b>'
            )

    elif types.ContentType.VIDEO == message.content_type: # Если админ отправил видео
        for user in select_users:
            try:
                await bot.send_video(
                    chat_id=int(user),
                    video=message.video.file_id,
                    caption=message.html_text if message.caption else None
                )
                await asyncio.sleep(0.33)
            except Exception:
                pass
        else:
            await message.answer(
                '<b> Рассылка завершена!</b>'
            )

    elif types.ContentType.ANIMATION == message.content_type: # Если админ отправил gif
        for user in select_users:
            try:
                await bot.send_animation(
                    chat_id=int(user),
                    animation=message.animation.file_id,
                    caption=message.html_text if message.caption else None
                )
                await asyncio.sleep(0.33)
            except Exception:
                pass
        else:
            await message.answer(
                '<b> Рассылка завершена!</b>'
            )

    else:
        await message.answer(
            '<b> Данный формат контента не поддерживается для рассылки!</b>'
        )



@dp.message_handler()
async def echo_message(msg: types.Message):
    async with create_engine(user=config.datab["user"],
                             database=config.datab["database"],
                             host=config.datab["host"],
                             password=config.datab["password"]) as engine:
        if msg.text == "⬅️ Главное меню":
            # task.choose_task(0)
            await db_funcs.set_now_task(engine, str(msg.from_user.id), "0")
            await bot.send_message(msg.from_user.id, "Вернулись в главное меню.", reply_markup=nav.mainMenu)

        # for main menu:
        elif msg.text == "🆕 ЗАКАЗ":
            # task.choose_task(0)
            await db_funcs.set_now_task(engine, str(msg.from_user.id), "0")
            await bot.send_message(msg.from_user.id, "Выберите тип продвижения.", reply_markup=nav.orderMenu)
        elif msg.text == "ℹ️ Профиль":
            # task.choose_task(0)
            await db_funcs.set_now_task(engine, str(msg.from_user.id), "0")
            uid = str(msg.from_user.id)
            balance = await db_funcs.get_balance(engine, str(msg.from_user.id))
            ans = "Информация:\nTelegram id: " + uid + "\nБаланс: " + str(
                balance) + "\nНа счет пополнения баланса писать: @chipolinka_gang"
            await bot.send_message(msg.from_user.id, ans, reply_markup=nav.inline_kb_make_payment)
        elif msg.text == "#️⃣ Статистика":
            uid = str(msg.from_user.id)
            get_like = await db_funcs.get_report(engine, uid, 1)
            get_snebes_like = await db_funcs.get_report(engine, uid, 3)
            get_view = await db_funcs.get_report(engine, uid, 2)
            # task.choose_task(0)
            await db_funcs.set_now_task(engine, str(msg.from_user.id), "0")
            await bot.send_message(msg.from_user.id,
                                   "Статистика:\n\nЛайки обычные:\nЗаказов: " + str(
                                       get_like['res_orders']) + " штук\nВсего: " +
                                   str(get_like['res_sum']) + " лайков\n\nЛайки живые:\nЗаказов: " + str(
                                       get_snebes_like['res_orders']) + " штук\nВсего: " +
                                   str(get_snebes_like['res_sum']) + " лайков\n\nПросмотры:\nЗаказов: " + str(
                                       get_view['res_orders']) + " штук\nВсего: " +
                                   str(get_view['res_sum']) + " просмотров")
        # for order menu:
        elif msg.text == "🔝 Лайки":
            await bot.send_message(msg.from_user.id, "Выберите тип лайков.", reply_markup=nav.likeMenu)
        elif msg.text == "❤️Обычные лайки":
            # task.choose_task(1)
            await db_funcs.set_now_task(engine, str(msg.from_user.id), "1")
            default_price_like_1 = 60
            if await db_funcs.get_personal_price(engine, str(msg.from_user.id), "1") is not None:
                await bot.send_message(msg.from_user.id,
                                       "Введите ссылку и количество лайков через пробел.\nЦена " + await db_funcs.get_personal_price(
                                           engine, str(msg.from_user.id),
                                           "1") + " рублей за 1000 лайков\nПример:\nhttps://vk.com/wall-22822305_1307837 110",
                                       reply_markup=nav.likeMenu)
            else:
                await bot.send_message(msg.from_user.id,
                                       "Введите ссылку и количество лайков через пробел.\nЦена " + str(
                                           default_price_like_1) + " рублей за 1000 лайков\nПример:\nhttps://vk.com/wall-22822305_1307837 110",
                                       reply_markup=nav.likeMenu)
        elif msg.text == "👤Живые лайки":
            # task.choose_task(1)
            await db_funcs.set_now_task(engine, str(msg.from_user.id), "3")
            default_price_like_1 = 90
            if await db_funcs.get_personal_price(engine, str(msg.from_user.id), "3") is not None:
                await bot.send_message(msg.from_user.id,
                                       "Введите ссылку и количество лайков через пробел.\nЦена " + await db_funcs.get_personal_price(
                                           engine, str(msg.from_user.id),
                                           "3") + " рублей за 1000 лайков\nПример:\nhttps://vk.com/wall-22822305_1307837 110",
                                       reply_markup=nav.likeMenu)
            else:
                await bot.send_message(msg.from_user.id,
                                       "Введите ссылку и количество лайков через пробел.\nЦена " + str(
                                           default_price_like_1) + " рублей за 1000 лайков\nПример:\nhttps://vk.com/wall-22822305_1307837 110",
                                       reply_markup=nav.likeMenu)
        elif msg.text == "👁‍🗨 Просмотры":

            # task.choose_task(2)
            await db_funcs.set_now_task(engine, str(msg.from_user.id), "2")
            default_price_view_2 = 10
            if await db_funcs.get_personal_price(engine, str(msg.from_user.id), "2") is not None:
                await bot.send_message(msg.from_user.id,
                                       "Введите ссылку и количество просмотров через пробел.\nЦена " + await db_funcs.get_personal_price(
                                           engine, str(msg.from_user.id),
                                           "2") + " рублей за 1000 просмотров\nПример:\nhttps://vk.com/wall-22822305_1307837 3200",
                                       reply_markup=nav.orderMenu)
            else:
                await bot.send_message(msg.from_user.id,
                                       "Введите ссылку и количество просмотров через пробел.\nЦена " + str(
                                           default_price_view_2) + " рублей за 1000 просмотров\nПример:\nhttps://vk.com/wall-22822305_1307837 3200",
                                       reply_markup=nav.orderMenu)
        elif msg.text == "📢Репосты":

            # task.choose_task(2)
            await db_funcs.set_now_task(engine, str(msg.from_user.id), "4")
            default_price_repost = 120
            if await db_funcs.get_personal_price(engine, str(msg.from_user.id), "4") is not None:
                await bot.send_message(msg.from_user.id,
                                       "Введите ссылку и количество репостов через пробел.\nЦена " + str(
                                           int(await db_funcs.get_personal_price(engine, str(msg.from_user.id),
                                                                                 "4")) / 10) + " рублей за 100 репостов\nПример:\nhttps://vk.com/wall-22822305_1307837 32",
                                       reply_markup=nav.orderMenu)
            else:
                await bot.send_message(msg.from_user.id,
                                       "Введите ссылку и количество репостов через пробел.\nЦена " + str(
                                           default_price_repost / 10) + " рублей за 100 репостов\nПример:\nhttps://vk.com/wall-22822305_1307837 32",
                                       reply_markup=nav.orderMenu)
        elif msg.text[0:10] == "addbalance" and msg.from_user.id==config.ADMIN_ID:
            add_balance = msg.text.split()
            await db_funcs.add_balance(engine, add_balance[1], int(add_balance[2]))
            await bot.send_message(msg.from_user.id,
                                   "Баланс обновлен: " + add_balance[1] + " tg_id, на " + add_balance[2] + " рублей")
        elif msg.text[0:8] == "setprice" and msg.from_user.id==config.ADMIN_ID:
            set_price = msg.text.split()
            await db_funcs.set_personal_price(engine, set_price[1], set_price[2], set_price[3])
            await bot.send_message(msg.from_user.id,
                                   "Price обновлен:\n" + "tg_id: " + set_price[1] + ", type: " + set_price[
                                       2] + ", цена: " + set_price[3] + " рублей")
        elif msg.text[0:5] == "https":
            order_list = msg.text.split()
            if len(order_list) == 2 and int(order_list[1]) > 0:
                uid = str(msg.from_user.id)
                # if task.check_task() == 1:
                if await db_funcs.get_now_task(engine, str(msg.from_user.id)) == "1":
                    order_price = 60
                    t = await db_funcs.get_personal_price(engine, str(msg.from_user.id), "1")
                    if t is not None:
                        order_price = t
                    try:
                        sum = math.ceil(int(order_list[1]) / 1000 * int(order_price))
                        if (await db_funcs.get_balance(engine, str(msg.from_user.id)) - sum) > 0:
                            await like_api.make_like(str(uid), order_list[0], str(order_list[1]))
                            await bot.send_message(msg.from_user.id, "Задание успешно поставлено")
                            await db_funcs.new_order(engine, {"tg_id": uid, "type_id": "1", "url": order_list[0],
                                                              "value": order_list[1], "sum": sum})
                            await db_funcs.add_balance(engine, uid, -sum)
                        else:
                            await bot.send_message(msg.from_user.id, "Недостаточно средств.")
                    except Exception as ex:
                        await bot.send_message(msg.from_user.id, "Ошибка:" + str(ex))
                # if task.check_task() == 3:
                if await db_funcs.get_now_task(engine, str(msg.from_user.id)) == "3":
                    order_price = 90
                    t = await db_funcs.get_personal_price(engine, str(msg.from_user.id), "3")
                    if t is not None:
                        order_price = t
                    try:
                        sum = math.ceil(int(order_list[1]) / 1000 * int(order_price))
                        if (await db_funcs.get_balance(engine, str(msg.from_user.id)) - sum) > 0:
                            await like_snebes_3.make_like(order_list[0], str(order_list[1]))
                            await bot.send_message(msg.from_user.id, "Задание успешно поставлено")
                            await db_funcs.new_order(engine,
                                                     {"tg_id": uid, "type_id": "1", "url": order_list[0],
                                                      "value": order_list[1], "sum": sum})
                            await db_funcs.add_balance(engine, uid, -sum)
                        else:
                            await bot.send_message(msg.from_user.id, "Недостаточно средств.")
                    except Exception as ex:
                        await bot.send_message(msg.from_user.id, "Ошибка:" + str(ex))

                # if task.check_task() == 4:
                if await db_funcs.get_now_task(engine, str(msg.from_user.id)) == "4":
                    order_price = 120
                    t = await db_funcs.get_personal_price(engine, str(msg.from_user.id), "4")
                    if t is not None:
                        order_price = t
                    try:
                        sum = math.ceil(int(order_list[1]) / 1000 * int(order_price))
                        if (await db_funcs.get_balance(engine, str(msg.from_user.id)) - sum) > 0:
                            await repost_likest4.make_repost(order_list[0], str(order_list[1]))
                            await bot.send_message(msg.from_user.id, "Задание успешно поставлено")
                            await db_funcs.new_order(engine,
                                                     {"tg_id": uid, "type_id": "1", "url": order_list[0],
                                                      "value": order_list[1], "sum": sum})
                            await db_funcs.add_balance(engine, uid, -sum)
                        else:
                            await bot.send_message(msg.from_user.id, "Недостаточно средств.")
                    except Exception as ex:
                        await bot.send_message(msg.from_user.id, "Ошибка:" + str(ex))

                # if task.check_task() == 2:
                if await db_funcs.get_now_task(engine, str(msg.from_user.id)) == "2":
                    order_price = 10
                    t = await db_funcs.get_personal_price(engine, str(msg.from_user.id), "2")
                    if t is not None:
                        order_price = t
                    try:
                        sum = math.ceil(int(order_list[1]) / 1000 * int(order_price))
                        if (await db_funcs.get_balance(engine, str(msg.from_user.id)) - sum) > 0:
                            await view_api.make_view(order_list[0], str(order_list[1]))
                            await bot.send_message(msg.from_user.id, "Задание успешно поставлено")
                            await db_funcs.new_order(engine, {"tg_id": uid, "type_id": "2", "url": order_list[0],
                                                              "value": order_list[1], "sum": sum})
                            await db_funcs.add_balance(engine, uid, -sum)
                        else:
                            await bot.send_message(msg.from_user.id, "Недостаточно средств.")
                    except Exception as ex:
                        await bot.send_message(msg.from_user.id, "Ошибка:" + str(ex))
                # if task.check_task() == 0:
                if await db_funcs.get_now_task(engine, str(msg.from_user.id)) == "0":
                    await bot.send_message(msg.from_user.id, "Не выбран тип накрутки.")
            else:
                await bot.send_message(msg.from_user.id,
                                       "Неверный формат ввода.\nПример верного формата:\nhttps://vk.com/wall-22822305_1307837 3200\n(ссылка_на_пост, 1 пробел, количество)")
        elif (msg.text.isdigit()) and (await db_funcs.get_now_task(engine, str(msg.from_user.id)) == "1000"):
            if int(msg.text) > 1:
                payment_url_label = await pay_yoomoney.create_payment(str(msg.from_user.id), int(msg.text))
                inline_kb__check_payment = InlineKeyboardMarkup()
                inline_kb__check_payment.row(InlineKeyboardButton('Оплатить', url=payment_url_label["url"]))
                inline_kb__check_payment.row(InlineKeyboardButton('Проверить оплату', callback_data='check_pay_button'))
                await bot.send_message(msg.from_user.id,
                                       "Ссылка для оплаты создана. \nОплата доступна в течение 30 минут.",
                                       reply_markup=inline_kb__check_payment)
                await db_funcs.create_new_payment(engine, str(msg.from_user.id), int(msg.text),
                                                  payment_url_label["label"])
            else:
                await bot.send_message(msg.from_user.id, "Сумма не может быть меньше 2 рублей.")
        else:
            await bot.send_message(msg.from_user.id, "Чтобы появилось меню, отправьте /start")


if __name__ == '__main__':
    executor.start_polling(dp)
