from aiogram.fsm.state import State, StatesGroup

# Holatlarni aniqlash
class UserStates(StatesGroup):
    MAIN_MENU = State()
    ADD_TO_CART = State()
    VIEW_CART = State()
    CHECKOUT = State()
    ADMIN_MENU = State()
    ADD_PRODUCT = State()
    ADD_PRODUCT_NAME = State()
    ADD_PRODUCT_PRICE = State()
    EDIT_PRODUCT = State()
    DELETE_PRODUCT = State()
    REMOVE_PRODUCT = State()  # Mahsulotni o'chirish uchun
    REMOVE_PRODUCT_QUANTITY = State()  # Nechtasini o'chirishni so'rash uchun