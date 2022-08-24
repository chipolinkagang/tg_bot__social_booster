
import datetime
from typing import List

from yoomoney import Client
from yoomoney import Quickpay
import random
import db_funcs

# receiver: 410014649906106

#Создание ссылки - формы на оплату:
async def create_payment(input_tg_id: str, input_sum: int):
    label_str = input_tg_id + "_" + str(random.randint(1000, 9999)) # задаем label для quickpay
    main_receiver = "410014649906106" # задаем получателя
    quickpay = Quickpay(
        receiver=main_receiver,
        quickpay_form="shop",
        targets="Sponsor this project",
        paymentType="SB",
        sum=input_sum,
        label=label_str
    )
    result = {"url": quickpay.base_url, "label": label_str}
    return result


def check_interval_of_pay(date, x=30) -> bool: # запись берется из бд, если прошло 30 мин, то запись надо будет удалить, последний чек платежа и отправить смс, что время на оплату вышло.
    create_payform_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    # create_payform_date = date
    thirty_minutes = datetime.timedelta(minutes=x)
    last_pay_time = create_payform_date + thirty_minutes

    now = datetime.datetime.today()

    if last_pay_time > now:
        return True
    else:
        return False

#Проверка платежа:
async def check_payment(input_label: str):
    token = "410014649906106.DFD98894DA0369D440FEBC499AD11E6CAC7BB3A8074CFC0C60AE67EE9E346A0A4DBC9C4E8D8EA8680FA1960CF6254316838F2F6120DB5A13E3020AD6DFC89A1D846041238D1207B2DB94A7DDB8F252EC6D6F0B9C36C98FAB09D878B1FAF88414526DE2354A9C94FB4FECEDF45A81014B16411FFA1B2F55CC01A1612AC52A82C6"
    client = Client(token)
    history = client.operation_history(label=input_label)
    print("List of operations:")
    print("Next page starts with: ", history.next_record)
    for operation in history.operations:
        print()
        print("Operation:",operation.operation_id)
        print("\tStatus     -->", operation.status)
        print("\tDatetime   -->", operation.datetime)
        print("\tTitle      -->", operation.title)
        print("\tPattern id -->", operation.pattern_id)
        print("\tDirection  -->", operation.direction)
        print("\tAmount     -->", operation.amount)
        print("\tLabel      -->", operation.label)
        print("\tType       -->", operation.type)
        if (operation.status == "success"): # 215 потому что 3 часа + 35 минут (юмани время по гринвичу, а now время по мск)
            return True
    return False





# print(check_payment("a1b2c3d4e5"))