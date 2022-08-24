from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

btnMain = KeyboardButton('⬅️ Главное меню')
# main menu
btnOrder = KeyboardButton('🆕 ЗАКАЗ')
btnProfile = KeyboardButton('ℹ️ Профиль')
btnStat = KeyboardButton('#️⃣ Статистика')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnOrder, btnProfile, btnStat)


#order menu
btnLike = KeyboardButton('🔝 Лайки')
btnViews = KeyboardButton('👁‍🗨 Просмотры')
btnRepost = KeyboardButton('📢Репосты')
orderMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnLike, btnViews, btnRepost, btnMain)

#like_menu
btn_Likest_Like = KeyboardButton('❤️Обычные лайки')
btn_Snebes_Like = KeyboardButton('👤Живые лайки')
likeMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_Likest_Like, btn_Snebes_Like, btnMain)

#make_payment_button
inline_btn_pay_card = InlineKeyboardButton('Пополнение с карты.', callback_data='make_pay_button')
inline_kb_make_payment = InlineKeyboardMarkup().add(inline_btn_pay_card)
#check_payment_button
inline_btn_1 = InlineKeyboardButton('Проверить платеж.', callback_data='check_pay_button')
inline_kb_check_payment = InlineKeyboardMarkup()