import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# Bot tokeni (o'zingizning tokeningiz bilan almashtiring)
API_TOKEN = 'token'

# Bot va Dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())