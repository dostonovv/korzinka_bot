import logging
import psycopg2

# PostgreSQL sozlamalari (o'zingizning ma'lumotlaringiz bilan almashtiring)
DB_CONFIG = {
    'dbname': 'korzinka_db',
    'user': 'postgres',
    'password': '25091986Nm_',
    'host': 'localhost',
    'port': '5432'
}

# Ma'lumotlar bazasini sozlash
def init_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id TEXT PRIMARY KEY, name TEXT, price REAL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS cart 
                     (user_id BIGINT, product_id TEXT, quantity INTEGER,
                      CONSTRAINT unique_user_product UNIQUE (user_id, product_id))''')
        conn.commit()
    except Exception as e:
        logging.error(f"DB initialization error: {e}")
    finally:
        if conn:
            c.close()
            conn.close()

# Mahsulotlar ro'yxatini olish
def get_products():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        c = conn.cursor()
        c.execute("SELECT id, name, price FROM products")
        products = c.fetchall()
        return products
    except Exception as e:
        logging.error(f"Error fetching products: {e}")
        return []
    finally:
        c.close()
        conn.close()

# Mahsulotni savatga qo'shish
def add_to_cart_db(user_id: int, product_name: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        c = conn.cursor()
        c.execute("SELECT id, price FROM products WHERE name = %s", (product_name,))
        product = c.fetchone()

        if product:
            product_id, price = product
            c.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s) ON CONFLICT (user_id, product_id) DO UPDATE SET quantity = cart.quantity + 1",
                     (user_id, product_id, 1))
            conn.commit()
            return True, f"{product_name} savatga qo'shildi."
        else:
            return False, "Mahsulot topilmadi."
    except Exception as e:
        logging.error(f"Error adding to cart: {e}")
        return False, "Xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
    finally:
        c.close()
        conn.close()

# Savatni olish
def get_cart(user_id: int):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        c = conn.cursor()
        c.execute('''SELECT p.name, p.price, c.quantity 
                     FROM cart c 
                     JOIN products p ON c.product_id = p.id 
                     WHERE c.user_id = %s''', (user_id,))
        items = c.fetchall()
        return items
    except Exception as e:
        logging.error(f"Error viewing cart: {e}")
        return []
    finally:
        c.close()
        conn.close()

# Savatni tozalash
def clear_cart_db(user_id: int):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        c = conn.cursor()
        c.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        conn.commit()
        return True, "Savat tozalandi."
    except Exception as e:
        logging.error(f"Error clearing cart: {e}")
        return False, "Xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
    finally:
        c.close()
        conn.close()

# Mahsulotni savatdan o'chirish (miqdor bilan)
def remove_product_from_cart(user_id: int, product_name: str, quantity: int = 1):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        c = conn.cursor()
        c.execute("SELECT id FROM products WHERE name = %s", (product_name,))
        product = c.fetchone()

        if product:
            product_id = product[0]
            c.execute("SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
            current_quantity = c.fetchone()
            if current_quantity:
                current_quantity = current_quantity[0]
                if current_quantity <= quantity:
                    c.execute("DELETE FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
                else:
                    c.execute("UPDATE cart SET quantity = quantity - %s WHERE user_id = %s AND product_id = %s",
                             (quantity, user_id, product_id))
                conn.commit()
                return True, f"{product_name} savatdan o'chirildi."
            else:
                return False, "Mahsulot savatda topilmadi."
        else:
            return False, "Mahsulot topilmadi."
    except Exception as e:
        logging.error(f"Error removing product from cart: {e}")
        return False, "Xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
    finally:
        c.close()
        conn.close()

# Yangi mahsulot qo'shish
def add_product_db(product_id: str, name: str, price: float):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        c = conn.cursor()
        c.execute("INSERT INTO products (id, name, price) VALUES (%s, %s, %s)",
                 (product_id, name, price))
        conn.commit()
        return True, f"{name} mahsuloti qo'shildi."
    except Exception as e:
        logging.error(f"Error adding product: {e}")
        return False, "Xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
    finally:
        c.close()
        conn.close()