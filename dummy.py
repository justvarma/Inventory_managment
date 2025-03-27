import pymysql
import random

# Database Connection
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="Adityavarma@123",
    database="inventory_systems"
)

cursor = connection.cursor()

# Fetch categories from category_data
cursor.execute("SELECT name FROM category_data;")
categories = [row[0] for row in cursor.fetchall()]

# Fetch suppliers from supplier_data
cursor.execute("SELECT name FROM supplier_data;")
suppliers = [row[0] for row in cursor.fetchall()]

# Sample product names
product_names = [
    "Basmati Rice", "Himalayan Honey", "Ayurvedic Hair Oil", "Neem Wood Comb", "Darjeeling Tea",
    "Chyawanprash", "Patanjali Aloe Vera Gel", "Santoor Soap", "Mysore Sandal Soap", "Jaipur Handicrafts",
    "Tanjore Painting", "Kashmiri Pashmina", "Handmade Jute Bags", "Khadi Cotton Fabric", "Banarasi Silk Saree",
    "Kota Doria Dupatta", "Indian Spices Kit", "Organic Herbal Green Tea", "Eco-friendly Bamboo Utensils",
    "Dhokra Metal Craft", "Godavari Mango", "Bengali Sweets Box", "Handmade Terracotta Jewelry", "Coconut Oil",
    "Organic Coffee Beans", "Handmade Clay Pottery", "Saffron Threads", "Ayurvedic Shampoo", "Himalayan Pink Salt",
    "Organic Cow Ghee", "Handwoven Woolen Shawl", "Indian Masala Chai", "Multigrain Flour", "Premium Kashmiri Almonds",
    "Handcrafted Wooden Chess Board", "Silk Stitched Kurta", "Ghee Roasted Cashews", "Turmeric Powder",
    "Handmade Beaded Necklaces", "Handloom Linen Saree", "Rosewood Carved Box", "Madhubani Art Painting",
    "Pashmina Wool Stole", "Traditional Copper Water Bottle", "Organic Amla Juice", "Dried Figs",
    "Kashmiri Walnut Kernels",
    "Handpainted Terracotta Tiles", "Himalayan Herbal Shampoo", "Rajasthani Blue Pottery", "Neem Tulsi Face Wash",
    "Kesar Badam Thandai", "Handmade Jute Rug", "Handwoven Cotton Bedsheets", "Handcrafted Silver Earrings",
    "Sandalwood Essential Oil", "Banana Fiber Handbags", "Handloom Ikat Fabric", "Handmade Brass Statues",
    "Hand-carved Wooden Keychains", "Mysore Rosewood Artifacts", "Himalayan Herbal Bath Salts", "Pure Honeycomb Honey",
    "Black Pepper from Kerala", "Kesar Elaichi Barfi", "Handmade Embroidered Cushion Covers", "Organic Tulsi Tea"
]

# Status options
status_options = ["Active", "Inactive"]

# Insert 69 unique products
insert_query = """
INSERT INTO product_data (category, supplier, name, price, discount, discounted_price, quantity, status) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

product_data = []
for _ in range(69):
    category = random.choice(categories)
    supplier = random.choice(suppliers)
    name = random.choice(product_names)
    price = round(random.uniform(50, 5000), 2)  # Price between ₹50 and ₹5000
    discount = random.randint(0, 20)  # Discount between 0% and 20%
    discounted_price = round(price * (1 - discount / 100), 2)
    quantity = random.randint(10, 500)  # Stock quantity
    status = random.choice(status_options)  # "Active" or "Inactive"

    product_data.append((category, supplier, name, price, discount, discounted_price, quantity, status))

# Execute batch insert
cursor.executemany(insert_query, product_data)
connection.commit()

print("✅ 69 unique product entries inserted successfully!")

# Close connection
cursor.close()
connection.close()
