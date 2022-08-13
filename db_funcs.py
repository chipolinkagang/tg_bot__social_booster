import asyncio
import datetime
import sys
from typing import List

import sqlalchemy as sa
from aiopg.sa import create_engine
from sqlalchemy import Table, MetaData

if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
metadata = sa.MetaData()

users = sa.Table('users', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('name', sa.String(255)),
                 sa.Column('tg_id', sa.String(255)),
                 sa.Column('balance', sa.Integer),
                 sa.Column('now_task', sa.String))

orders = sa.Table('orders', metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('tg_id', sa.String(255)),
                  sa.Column('url', sa.String(255)),
                  sa.Column('type_id', sa.Integer),
                  sa.Column('value', sa.Integer),
                  sa.Column('date', sa.String(255)))

personal_prices = sa.Table('personal_prices', metadata,
                           sa.Column('id', sa.Integer, primary_key=True),
                           sa.Column('tg_id', sa.String(255)),
                           sa.Column('type', sa.Integer),
                           sa.Column('price', sa.String))

list_o = sa.Table('list_o', metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('type', sa.String(255)),
                  sa.Column('price', sa.Integer))


async def create_table(engine):
    async with engine.acquire() as conn:
        await conn.execute('DROP TABLE IF EXISTS personal_prices')
        await conn.execute('''CREATE TABLE personal_prices (
                                                  id serial PRIMARY KEY,
                                                  tg_id varchar(255),
                                                  type integer,
                                                  price varchar(255))''')

        await conn.execute('DROP TABLE IF EXISTS users')
        await conn.execute('''CREATE TABLE users (
                                          id serial PRIMARY KEY,
                                          name varchar(255),
                                          tg_id varchar(255),
                                          balance integer,
                                          now_task varchar(255))''')

        # await conn.execute('DROP TABLE IF EXISTS orders')
        # await conn.execute('''CREATE TABLE orders (
        #                                   id serial PRIMARY KEY,
        #                                   tg_id varchar(255),
        #                                   url varchar(255),
        #                                   type_id integer,
        #                                   value integer,
        #                                   date varchar(255))''')
        #
        # await conn.execute('DROP TABLE IF EXISTS list_o')
        # await conn.execute('''CREATE TABLE list_o (
        #                                   id serial PRIMARY KEY,
        #                                   type varchar(255),
        #                                   price integer)''')


# проверка на регистрацию
async def reg_check(engine, inp_tg_id: str) -> bool:
    async with engine.acquire() as conn:
        async for row in conn.execute(users.select().where(users.c.tg_id == inp_tg_id)):
            return True


# Добавление нового пользователя в users
async def registration(engine, person: dict) -> str:
    async with engine.acquire() as conn:
        await conn.execute(users.insert().values(name=person['name'], tg_id=person['tg_id'], balance=0))
        x = 0
        async for row in conn.execute(users.select().where(users.c.tg_id == person['tg_id'])):
            if x < row.id:
                x = row.id
        return x


async def reg_type(engine, list_order: dict):
    async with engine.acquire() as conn:
        await conn.execute(users.insert().values(type=list_order['type'], price=list_order['price']))


# Добавление нового заказа в orders (orders.type_id = list.id) {"tg_id": , "type_id": , "url": , "value": }
async def new_order(engine, order: dict) -> str:
    async with engine.acquire() as conn:
        o_date = datetime.datetime.today().strftime("%Y%m%d/%H.%M.%S")
        await conn.execute(orders.insert().values(tg_id=order['tg_id'], url=order['url'],
                                                  type_id=order['type_id'], value=order['value'], date=o_date))
        x = 0
        async for row in conn.execute(orders.select().where(orders.c.tg_id == order['tg_id']
                                                            and orders.c.url == order['url']
                                                            and orders.c.type_id == order['type_id'])):
            if x < row.id:
                x = row.id
        return x


# Изменение баланса users
async def add_balance(engine, inp_tg_id: str, val: int) -> int:
    async with engine.acquire() as conn:
        async for row in conn.execute(users.select().where(users.c.tg_id == inp_tg_id)):
            now_balance = row.balance
            await conn.execute(
                sa.update(users).values({"balance": now_balance + val}).where(users.c.tg_id == inp_tg_id))
            return now_balance + val


# получить текущий баланс по uid
async def get_balance(engine, int_tg_id: str):
    async with engine.acquire() as conn:
        async for row in conn.execute(users.select().where(users.c.tg_id == int_tg_id)):
            return row.balance


# получить текущую цену для конкретного id товара
async def get_price(engine, type_id: int):
    async with engine.acquire() as conn:
        async for row in conn.execute(users.select().where(list_o.c.id == type_id)):
            print(row.type)


# Получение отчета о tg_id, 0 - вывод всех, inp_type_id ввод типа услуги
async def get_report(engine, inp_tg_id: str, inp_type_id: int) -> List[dict]:
    async with engine.acquire() as conn:
        if inp_tg_id == '0':
            return 0
        else:
            res_orders = 0
            res_sum = 0
            async for row in conn.execute(orders.select().where(orders.c.tg_id == inp_tg_id)):
                if row.type_id == inp_type_id:
                    print(row.tg_id, row.type_id, row.value)
                    res_orders += 1
                    res_sum += row.value
            res = {'res_orders': res_orders, 'res_sum': res_sum}
            print(res)
            return res


# Вывод всех значений таблицы
async def get_all(engine):
    async with engine.acquire() as conn:
        res = []
        async for row in conn.execute(users.select()):
            res.append({"id": row.id, "name": row.name, "tg_id": row.tg_id, "balance": row.balance})
        return res


async def set_now_task(engine, inp_tg_id: str, inp_type_id: str):
    async with engine.acquire() as conn:
        await conn.execute(sa.update(users).values({"now_task": inp_type_id}).where(users.c.tg_id == inp_tg_id))


async def get_now_task(engine, inp_tg_id: str):
    async with engine.acquire() as conn:
        async for row in conn.execute(users.select().where(users.c.tg_id == inp_tg_id)):
            return row.now_task


async def set_personal_price(engine, inp_tg_id: str, inp_type_id: str, inp_price: str):
    async with engine.acquire() as conn:
        x = 0
        async for row in conn.execute(personal_prices.select().where(personal_prices.c.tg_id == inp_tg_id and personal_prices.c.type == inp_type_id)):
            x = 1
            await conn.execute(sa.update(personal_prices).values({"price": inp_price}).where(personal_prices.c.tg_id == inp_tg_id and personal_prices.c.type == inp_type_id))

        if x == 0:
            await conn.execute(personal_prices.insert().values(tg_id=inp_tg_id, type=inp_type_id, price=inp_price))

async def get_personal_price(engine, inp_tg_id: str, inp_type_id):
    async with engine.acquire() as conn:
        x = 0
        async for row in conn.execute(personal_prices.select().where(personal_prices.c.tg_id == inp_tg_id and personal_prices.c.type == inp_type_id)):
            return row.price
        return None


async def go():
    async with create_engine(user='postgres',
                             database='lab1',
                             host='127.0.0.1',
                             password='123456') as engine:
        # await create_table(engine)

        # await get_price(engine, 2)

        # print(await get_personal_price(engine, "862989874", "1"))
        #
        # #
        # await registration(engine, {'name': 'Andrew', 'tg_id': '8432842'})
        # await registration(engine, {'name': 'Andr3ew', 'tg_id': '89573275'})
        #
        # await registration(engine, {'name': 'A', 'tg_id': '97372'})
        # await registration(engine, {'name': 'b3bb', 'tg_id': '8573275'})
        # await registration(engine, {'name': 'cecece', 'tg_id': '4324112'})
        #
        # await new_order(engine,
        #                 {'tg_id': '862989874', 'url': 'vk.com/chipoli/wall_', 'type_id': 1, 'value': 200})
        # await new_order(engine,
        #                 {'tg_id': '8629', 'url': 'vk.com/chipoli/wall_fd', 'type_id': 1, 'value': 25})
        # await new_order(engine,
        #                 {'tg_id': '862989874', 'url': 'vk.com/chipoli/dgwall_', 'type_id': 1, 'value': 25})
        # await new_order(engine,
        #                 {'tg_id': '862989874', 'url': 'vk.com/chipoli/wafdgfll_', 'type_id': 1, 'value': 300})
        # await new_order(engine,
        #                 {'tg_id': '862989874', 'url': 'vk.com/chipoli/dgwall_', 'type_id': 2, 'value': 2500})
        # await new_order(engine,
        #                 {'tg_id': '862989874', 'url': 'vk.com/chipoli/wafdgfll_', 'type_id': 2, 'value': 2000})

        # await add_balance(engine, '8573275', -15)
        # await get_report(engine, '8573275', 1)
        # await set(engine, {"id": "2", "first_name": "rer", "last_name": "fef"})
        # await get_list(engine, {"first_name": {"like": ""}, "last_name": {"ilike": "A"}}, [{"field": "id", "direction": "asc"}], 4, 0)
        # await get(engine, "2")
        # await get_count(engine, {"first_name": {"like": ""}, "last_name": {"ilike": "a"}})
        # await delete(engine, {"id": "1", "first_name": "rer", "last_name": "fef"})

        # async with engine.acquire() as conn:
        #     await conn.execute(peop.insert().values(first_name='Andrew', last_name='Star'))
        #     await conn.execute(peop.insert().values(first_name='Andrew', last_name='Star'))
        #
        #     async for row in conn.execute(peop.select()):
        #         print(row.id, row.first_name, row.last_name)
        print(await get_all(engine))
        # print(await set_now_task(engine, "862989874", "2"))


loop = asyncio.get_event_loop()
loop.run_until_complete(go())
