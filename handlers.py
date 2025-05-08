import logging
import uuid
from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from buttons import get_main_menu, get_products_menu, get_cart_menu, get_admin_menu, remove_quantity_keyboard
from database import init_db, get_products, add_to_cart_db, get_cart, clear_cart_db, remove_product_from_cart, add_product_db
from states import UserStates

# Router
router = Router()

# Ma'lumotlar bazasini sozlash
init_db()

# Admin ID (buttons.py dan olingan)
from buttons import ADMIN_ID

# Boshlang'ich menyuni ko'rsatish
async def show_main_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    keyboard = get_main_menu(user_id)
    await message.answer("🏪 KorzinkaBot'ga xush kelibsiz! Tanlang:", reply_markup=keyboard)
    await state.set_state(UserStates.MAIN_MENU)

# Mahsulotlar ro'yxatini ko'rsatish
async def show_products(message: types.Message, state: FSMContext):
    products = get_products()
    if not products:
        await message.answer("Mahsulotlar topilmadi.")
        return

    keyboard = get_products_menu(products)
    await message.answer("Mahsulotlarni tanlang:", reply_markup=keyboard)
    await state.set_state(UserStates.ADD_TO_CART)

# Mahsulotni savatga qo'shish
async def add_to_cart(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await show_main_menu(message, state)
        return

    product_name = message.text.split(" - ")[0]
    user_id = message.from_user.id
    success, response = add_to_cart_db(user_id, product_name)
    await message.answer(response)
    await show_products(message, state)

# Savatni ko'rish
async def view_cart(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    items = get_cart(user_id)
    if not items:
        await message.answer("Savat bo'sh.")
        await show_main_menu(message, state)
        return

    total = 0
    response = "🧺 Savatingiz:\n\n"
    for name, price, quantity in items:
        if price is not None and quantity is not None:
            item_total = price * quantity
            response += f"{name} x{quantity} = {item_total} so'm\n"
            total += item_total
        else:
            logging.error(f"Invalid data for product {name}: price={price}, quantity={quantity}")
            await message.answer(f"Mahsulot {name} bilan muammo yuz berdi.")
            return

    response += f"\nJami: {total} so'm"
    keyboard = get_cart_menu(items)
    await message.answer(response, reply_markup=keyboard)
    await state.set_state(UserStates.VIEW_CART)

# Savatni tozalash
async def clear_cart(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    success, response = clear_cart_db(user_id)
    await message.answer(response)
    await show_main_menu(message, state)

# Mahsulotni o'chirishni boshlash
async def remove_product_start(message: types.Message, state: FSMContext):
    # "Olma x1 o'chirish" dan faqat "Olma" ni olish
    text = message.text.replace(" o'chirish", "")
    product_name = text.split(" x")[0]
    await state.update_data(product_name=product_name)
    await message.answer("Necha dona o'chirilsin? (raqam kiriting):", reply_markup=remove_quantity_keyboard())
    await state.set_state(UserStates.REMOVE_PRODUCT_QUANTITY)

# Mahsulotni savatdan o'chirish
async def remove_product(message: types.Message, state: FSMContext):
    if message.text == "Hammasini":
        data = await state.get_data()
        product_name = data.get('product_name')
        user_id = message.from_user.id
        success, response = remove_product_from_cart(user_id, product_name, quantity=9999)  # Katta son bilan hammasini o'chirish
        await message.answer(response)
        await view_cart(message, state)
        return

    try:
        quantity = int(message.text)
        if quantity <= 0:
            await message.answer("Iltimos, musbat son kiriting!")
            return
    except ValueError:
        await message.answer("Iltimos, raqam kiriting!")
        return

    data = await state.get_data()
    product_name = data.get('product_name')
    user_id = message.from_user.id
    success, response = remove_product_from_cart(user_id, product_name, quantity)
    await message.answer(response)
    await view_cart(message, state)

# Hisob-kitob
async def checkout(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.CHECKOUT)
    user_id = message.from_user.id
    items = get_cart(user_id)
    if not items:
        await message.answer("Savat bo'sh.")
        await show_main_menu(message, state)
        return

    total = 0
    response = "📝 Chek:\n\n"
    for name, price, quantity in items:
        if price is not None and quantity is not None:
            item_total = price * quantity
            response += f"{name} x{quantity} = {item_total} so'm\n"
            total += item_total
        else:
            logging.error(f"Invalid data for product {name}: price={price}, quantity={quantity}")
            await message.answer(f"Mahsulot {name} bilan muammo yuz berdi. Iltimos, qayta urinib ko'ring.")
            await show_main_menu(message, state)
            return

    response += f"\nJami: {total} so'm"
    success, _ = clear_cart_db(user_id)
    if not success:
        await message.answer("Savatni tozalashda xatolik yuz berdi.")
        await show_main_menu(message, state)
        return

    await message.answer(response)
    await show_main_menu(message, state)

# Admin paneli
async def admin_panel(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        await message.answer("Sizda admin huquqi yo'q!")
        return

    keyboard = get_admin_menu()
    await message.answer("🔑 Admin paneli:", reply_markup=keyboard)
    await state.set_state(UserStates.ADMIN_MENU)

# Yangi mahsulot qo'shish
async def add_product_start(message: types.Message, state: FSMContext):
    await message.answer("Yangi mahsulot nomini kiriting:")
    await state.set_state(UserStates.ADD_PRODUCT_NAME)

async def add_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Mahsulot narxini kiriting (so'mda):")
    await state.set_state(UserStates.ADD_PRODUCT_PRICE)

async def add_product_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Iltimos, to'g'ri narx kiriting.")
        return

    data = await state.get_data()
    product_name = data.get('name')
    product_id = str(uuid.uuid4())
    success, response = add_product_db(product_id, product_name, price)
    await message.answer(response)
    await admin_panel(message, state)

# Handlerlar
@router.message(Command(commands=['start']))
async def start_command(message: types.Message, state: FSMContext):
    await show_main_menu(message, state)

@router.message(StateFilter(UserStates.MAIN_MENU))
async def main_menu_handler(message: types.Message, state: FSMContext):
    if message.text == "🛍 Mahsulotlar":
        await show_products(message, state)
    elif message.text == "🧺 Savatni ko'rish":
        await view_cart(message, state)
    elif message.text == "💳 Hisob-kitob":
        await checkout(message, state)
    elif message.text == "🔑 Admin paneli":
        await admin_panel(message, state)

@router.message(StateFilter(UserStates.ADD_TO_CART))
async def add_to_cart_handler(message: types.Message, state: FSMContext):
    await add_to_cart(message, state)

@router.message(StateFilter(UserStates.VIEW_CART))
async def view_cart_handler(message: types.Message, state: FSMContext):
    if message.text == "❌ Savatni tozalash":
        await clear_cart(message, state)
    elif message.text.endswith(" o'chirish"):
        await remove_product_start(message, state)
    elif message.text == "🔙 Orqaga":
        await show_main_menu(message, state)

@router.message(StateFilter(UserStates.ADMIN_MENU))
async def admin_menu_handler(message: types.Message, state: FSMContext):
    if message.text == "➕ Yangi mahsulot":
        await add_product_start(message, state)
    elif message.text == "🔙 Orqaga":
        await show_main_menu(message, state)

@router.message(StateFilter(UserStates.ADD_PRODUCT_NAME))
async def add_product_name_handler(message: types.Message, state: FSMContext):
    await add_product_name(message, state)

@router.message(StateFilter(UserStates.ADD_PRODUCT_PRICE))
async def add_product_price_handler(message: types.Message, state: FSMContext):
    await add_product_price(message, state)

@router.message(StateFilter(UserStates.REMOVE_PRODUCT_QUANTITY))
async def remove_product_quantity_handler(message: types.Message, state: FSMContext):
    await remove_product(message, state)