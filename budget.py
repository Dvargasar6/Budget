import sqlite3
from datetime import datetime

def connect_db(db_name="budget.db"):
    return sqlite3.connect(db_name)

def init_db(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            size TEXT,
            cheapest_place TEXT,
            avg_duration REAL,
            last_purchase_duration REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price REAL,
            place TEXT,
            purchase_date TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    conn.commit()

def add_product(conn, name, category, size):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, category, size)
        VALUES (?, ?, ?)
    ''', (name, category, size))
    conn.commit()
    return cursor.lastrowid

def record_purchase(conn, product_id, price, place, purchase_date_str):
    cursor = conn.cursor()
    
    # Insert purchase
    cursor.execute('''
        INSERT INTO purchases (product_id, price, place, purchase_date)
        VALUES (?, ?, ?, ?)
    ''', (product_id, price, place, purchase_date_str))
    
    # Update products table
    
    # 1. Update latest price (from the chronologically last purchase)
    cursor.execute('''
        SELECT price FROM purchases 
        WHERE product_id = ? 
        ORDER BY purchase_date DESC LIMIT 1
    ''', (product_id,))
    latest_price = cursor.fetchone()[0]
    cursor.execute('''
        UPDATE products SET price = ? WHERE id = ?
    ''', (latest_price, product_id))
    
    # 2. Update cheapest place
    cursor.execute('''
        SELECT place FROM purchases 
        WHERE product_id = ? 
        ORDER BY price ASC, purchase_date DESC LIMIT 1
    ''', (product_id,))
    cheapest_place = cursor.fetchone()[0]
    cursor.execute('''
        UPDATE products SET cheapest_place = ? WHERE id = ?
    ''', (cheapest_place, product_id))
    
    # 3. Calculate durations
    cursor.execute('''
        SELECT purchase_date FROM purchases 
        WHERE product_id = ? 
        ORDER BY purchase_date ASC
    ''', (product_id,))
    dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in cursor.fetchall()]
    
    if len(dates) >= 2:
        durations = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        last_duration = durations[-1]
        avg_duration = sum(durations) / len(durations)
        
        cursor.execute('''
            UPDATE products 
            SET avg_duration = ?, last_purchase_duration = ?
            WHERE id = ?
        ''', (avg_duration, last_duration, product_id))
    
    conn.commit()

def get_products(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    return cursor.fetchall()

def main():
    import sys
    conn = connect_db()
    init_db(conn)
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python budget.py add <nombre> <categoria> <tamaño>")
        print("  python budget.py buy <id_producto> <precio> <lugar> <fecha_aaaa-mm-dd>")
        print("  python budget.py list")
        return

    cmd = sys.argv[1]
    try:
        if cmd == "add":
            if len(sys.argv) < 5:
                print("Error: Faltan argumentos para 'add'.")
                return
            name, cat, size = sys.argv[2], sys.argv[3], sys.argv[4]
            pid = add_product(conn, name, cat, size)
            print(f"Producto añadido con ID: {pid}")
        elif cmd == "buy":
            if len(sys.argv) < 6:
                print("Error: Faltan argumentos para 'buy'.")
                return
            pid, price, place, date = int(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
            record_purchase(conn, pid, price, place, date)
            print("Compra registrada.")
        elif cmd == "list":
            products = get_products(conn)
            print(f"{'ID':<3} | {'Nombre':<15} | {'Cat':<10} | {'Precio':<7} | {'Tamaño':<10} | {'Barato':<10} | {'Dur Media':<10} | {'Ult Dur':<10}")
            print("-" * 90)
            for p in products:
                # p: id, name, category, price, size, cheapest_place, avg_duration, last_purchase_duration
                print(f"{p[0]:<3} | {p[1]:<15} | {p[2]:<10} | {p[3] if p[3] else 0.0:<7.2f} | {p[4] if p[4] else '':<10} | {p[5] if p[5] else '':<10} | {p[6] if p[6] else 0.0:<10.1f} | {p[7] if p[7] else 0.0:<10.1f}")
        else:
            print(f"Error: Comando desconocido '{cmd}'")
    except (ValueError, IndexError) as e:
        print(f"Error en los argumentos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
