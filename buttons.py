from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

# Admin ID (o'zingizning Telegram user ID ngiz bilan almashtiring)
ADMIN_ID = 6585387011  # Masalan, o'zingizning ID ngizni kiriting


# Admin panel menyusini ko'rsatish
def get_admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Yangi mahsulot"), KeyboardButton(text="✏️ Mahsulotni o'zgartirish")],
            [KeyboardButton(text="❌ Mahsulotni o'chirish"), KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )




# Boshlang'ich menyuni ko'rsatish
def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    if user_id == ADMIN_ID:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🛍 Mahsulotlar"), KeyboardButton(text="🧺 Savatni ko'rish")],
                [KeyboardButton(text="💳 Hisob-kitob"), KeyboardButton(text="🔑 Admin paneli")]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🛍 Mahsulotlar"), KeyboardButton(text="🧺 Savatni ko'rish")],
                [KeyboardButton(text="💳 Hisob-kitob")]
            ],
            resize_keyboard=True
        )

# Mahsulotlar menyusini ko'rsatish
def get_products_menu(products: list) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[])
    for product in products:
        keyboard.keyboard.append([KeyboardButton(text=f"{product[1]} - {product[2]} so'm")])
    keyboard.keyboard.append([KeyboardButton(text="🔙 Orqaga")])
    return keyboard

# Savat menyusini ko'rsatish (dinamik mahsulotlar bilan)
def get_cart_menu(items: list) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[])
    for name, price, quantity in items:
        if price is not None and quantity is not None:
            keyboard.keyboard.append([KeyboardButton(text=f"{name} x{quantity} o'chirish")])
    keyboard.keyboard.append([KeyboardButton(text="❌ Savatni tozalash"), KeyboardButton(text="Hammasini")])
    keyboard.keyboard.append([KeyboardButton(text="🔙 Orqaga")])
    return keyboard

# Mahsulotni o'chirish uchun so'rovni tozalash
def remove_quantity_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()