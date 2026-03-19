import sqlite3
import unittest
from datetime import datetime, timedelta
import os
from budget import connect_db, init_db, add_product, record_purchase, get_products

class TestBudget(unittest.TestCase):
    def setUp(self):
        self.db_name = "test_budget.db"
        self.conn = connect_db(self.db_name)
        init_db(self.conn)

    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    def test_add_product(self):
        pid = add_product(self.conn, "Leche", "Lácteos", "1L")
        products = get_products(self.conn)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0][1], "Leche")

    def test_record_purchase_updates(self):
        pid = add_product(self.conn, "Pan", "Panadería", "Pack 4")
        
        # Purchase 1
        record_purchase(self.conn, pid, 2.50, "Súper A", "2023-01-01")
        products = get_products(self.conn)
        # p: id, name, category, price, size, cheapest_place, avg_duration, last_purchase_duration
        self.assertEqual(products[0][3], 2.50) # price
        self.assertEqual(products[0][5], "Súper A") # cheapest_place
        
        # Purchase 2 (cheaper)
        record_purchase(self.conn, pid, 2.00, "Súper B", "2023-01-11")
        products = get_products(self.conn)
        self.assertEqual(products[0][3], 2.00) # new price
        self.assertEqual(products[0][5], "Súper B") # new cheapest_place
        self.assertEqual(products[0][6], 10.0) # avg_duration (11-1 = 10)
        self.assertEqual(products[0][7], 10.0) # last_duration (11-1 = 10)

        # Purchase 3 (more expensive)
        record_purchase(self.conn, pid, 3.00, "Tienda C", "2023-01-26")
        products = get_products(self.conn)
        self.assertEqual(products[0][3], 3.00) # new price
        self.assertEqual(products[0][5], "Súper B") # STILL Súper B is cheapest
        # durations: 10, 15. Avg = (10+15)/2 = 12.5
        self.assertEqual(products[0][6], 12.5) 
        self.assertEqual(products[0][7], 15.0)

if __name__ == "__main__":
    unittest.main()
