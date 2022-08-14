from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btnMain = KeyboardButton('⬅️ Главное меню')
# main menu
btnOrder = KeyboardButton('🆕 ЗАКАЗ')
btnProfile = KeyboardButton('ℹ️ Профиль')
btnStat = KeyboardButton('#️⃣ Статистика')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnOrder, btnProfile, btnStat)


#order menu
btnLike = KeyboardButton('🔝 Лайки')
btnViews = KeyboardButton('👁‍🗨 Просмотры')
orderMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnLike, btnViews, btnMain)

#like_menu
btn_Likest_Like = KeyboardButton('❤️Обычные лайки')
btn_Snebes_Like = KeyboardButton('👤Живые лайки')
likeMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_Likest_Like, btn_Snebes_Like, btnMain)


