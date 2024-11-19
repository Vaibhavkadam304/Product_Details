# import psycopg2
# import logging
# import requests
# from flask import Flask, jsonify

# # Flask app initialization
# app = Flask(__name__)

# # WooCommerce API credentials
# BASE_URL = "https://woocommerce-1355247-4989037.cloudwaysapps.com/wp-json/wc/v3/products"
# CONSUMER_KEY = "ck_5a5e3dfae960c8a4951168b46708c37d50bee800"
# CONSUMER_SECRET = "cs_8d6853d98d8b75ddaae2da242987122f38504e7f"

# # Database connection details
# DB_HOST = "ep-hidden-grass-a5jvxjss.us-east-2.aws.neon.tech"
# DB_PORT = "5432"
# DB_NAME = "neondb"
# DB_USER = "neondb_owner"
# DB_PASSWORD = "9cbzQplqW2mC"

# # Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# # Function to fetch product data from WooCommerce API
# def fetch_product_data():
#     try:
#         response = requests.get(
#             BASE_URL,
#             auth=(CONSUMER_KEY, CONSUMER_SECRET)
#         )
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Error fetching data from API: {e}")
#         return []


# # Function to handle NULL values
# def handle_null(value):
#     return value if value and value.strip() != "" else None


# # Function to insert product data into the database
# def insert_product_data(product, conn):
#     query = """
#     INSERT INTO productdetails (
#         product_id, name, price, regular_price, sale_price, status, on_sale, description, 
#         sku, stock_status, category, total_sales, average_rating, rating_count, 
#         store_name, store_url, store_location
#     )
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     ON CONFLICT (product_id) DO UPDATE 
#     SET name = EXCLUDED.name,
#         price = EXCLUDED.price,
#         regular_price = EXCLUDED.regular_price,
#         sale_price = EXCLUDED.sale_price,
#         status = EXCLUDED.status,
#         on_sale = EXCLUDED.on_sale,
#         description = EXCLUDED.description,
#         sku = EXCLUDED.sku,
#         stock_status = EXCLUDED.stock_status,
#         category = EXCLUDED.category,
#         total_sales = EXCLUDED.total_sales,
#         average_rating = EXCLUDED.average_rating,
#         rating_count = EXCLUDED.rating_count,
#         store_name = EXCLUDED.store_name,
#         store_url = EXCLUDED.store_url,
#         store_location = EXCLUDED.store_location;
#     """
#     try:
#         cursor = conn.cursor()

#         # Extract category
#         category = product.get("categories", [])
#         category_name = category[0]["name"] if category else "Unknown"

#         # Extract store information
#         store = product.get("store", {})
#         store_name = store.get("name", "Unknown Store")
#         store_url = store.get("url", "Unknown URL")
#         address = store.get("address", {})
#         store_location = f"{address.get('street_1', '')}, {address.get('city', '')}, {address.get('zip', '')}"

#         # Execute the query with appropriate data
#         cursor.execute(query, (
#             product["id"],
#             handle_null(product["name"]),
#             handle_null(product.get("price")),
#             handle_null(product.get("regular_price")),
#             handle_null(product.get("sale_price")),
#             product["status"],
#             product["on_sale"],
#             handle_null(product.get("description", "")),
#             handle_null(product.get("sku", "")),
#             handle_null(product["stock_status"]),
#             category_name,
#             product.get("total_sales", 0),
#             product.get("average_rating", 0),
#             product.get("rating_count", 0),
#             store_name,
#             store_url,
#             store_location
#         ))
#         conn.commit()
#         logging.info(f"Inserted/Updated product: {product['name']}")
#     except Exception as e:
#         logging.error(f"Error inserting product: {e}")
#         conn.rollback()


# # Route to trigger data fetching and insertion
# @app.route('/run', methods=['POST'])
# def run_task():
#     conn = None
#     try:
#         conn = psycopg2.connect(
#             host=DB_HOST,
#             port=DB_PORT,
#             database=DB_NAME,
#             user=DB_USER,
#             password=DB_PASSWORD
#         )
#         logging.info("Connected to the database")

#         # Fetch and insert product data
#         products = fetch_product_data()
#         if not products:
#             logging.error("No products fetched from API.")
#             return jsonify({"message": "No products fetched"}), 500

#         for product in products:
#             insert_product_data(product, conn)

#         return jsonify({"message": "Products processed successfully"}), 200
#     except Exception as e:
#         logging.error(f"Error in database operations: {e}")
#         return jsonify({"error": str(e)}), 500
#     finally:
#         if conn:
#             conn.close()
#             logging.info("Database connection closed.")


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
import psycopg2
import logging
import requests
import re
from flask import Flask, jsonify
from prettytable import PrettyTable

# WooCommerce API credentials
BASE_URL = "https://woocommerce-1355247-4989037.cloudwaysapps.com/wp-json/wc/v3/products"
CONSUMER_KEY = "ck_5a5e3dfae960c8a4951168b46708c37d50bee800"
CONSUMER_SECRET = "cs_8d6853d98d8b75ddaae2da242987122f38504e7f"

# Database connection details
DB_HOST = "ep-hidden-grass-a5jvxjss.us-east-2.aws.neon.tech"
DB_PORT = "5432"
DB_NAME = "neondb"
DB_USER = "neondb_owner"
DB_PASSWORD = "9cbzQplqW2mC"

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to fetch product data from WooCommerce API
def fetch_product_data():
    try:
        response = requests.get(
            BASE_URL,
            auth=(CONSUMER_KEY, CONSUMER_SECRET)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from API: {e}")
        return []

# Function to remove all HTML tags from text
def remove_html_tags(text):
    clean_text = re.sub(r'<.*?>', '', text) if text else text
    return clean_text

# Function to handle NULL values
def handle_null(value):
    return value if value and value.strip() != "" else None

# Function to insert product data into the database
def insert_product_data(product, conn):
    query = """
    INSERT INTO productlist (
        product_id, name, price, regular_price, sale_price, status, on_sale, description, 
        sku, stock_status, category, total_sales, average_rating, rating_count, 
        store_name, store_url, store_location
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (product_id) DO UPDATE 
    SET name = EXCLUDED.name,
        price = EXCLUDED.price,
        regular_price = EXCLUDED.regular_price,
        sale_price = EXCLUDED.sale_price,
        status = EXCLUDED.status,
        on_sale = EXCLUDED.on_sale,
        description = EXCLUDED.description,
        sku = EXCLUDED.sku,
        stock_status = EXCLUDED.stock_status,
        category = EXCLUDED.category,
        total_sales = EXCLUDED.total_sales,
        average_rating = EXCLUDED.average_rating,
        rating_count = EXCLUDED.rating_count,
        store_name = EXCLUDED.store_name,
        store_url = EXCLUDED.store_url,
        store_location = EXCLUDED.store_location;
    """
    try:
        cursor = conn.cursor()
        category = product.get("categories", [])
        category_name = category[0]["name"] if category else "Unknown"
        store = product.get("store", {})
        store_name = store.get("name", "Unknown Store")
        store_url = store.get("url", "Unknown URL")
        address = store.get("address", {})
        store_location = f"{address.get('street_1', '')}, {address.get('city', '')}, {address.get('zip', '')}"
        description = remove_html_tags(product.get("description", ""))
        cursor.execute(query, (
            product["id"],
            handle_null(product["name"]),
            handle_null(product.get("price")),
            handle_null(product.get("regular_price")),
            handle_null(product.get("sale_price")),
            product["status"],
            product["on_sale"],
            description,
            handle_null(product.get("sku", "")),
            handle_null(product["stock_status"]),
            category_name,
            product.get("total_sales", 0),
            product.get("average_rating", 0),
            product.get("rating_count", 0),
            store_name,
            store_url,
            store_location
        ))
        conn.commit()
        logging.info(f"Inserted/Updated product in table 'productlist': {product['name']}")
    except Exception as e:
        logging.error(f"Error inserting product into table 'productlist': {e}")
        conn.rollback()

# Flask route to fetch products and insert into DB
@app.route('/fetch_products', methods=['GET'])
def fetch_and_insert():
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logging.info("Connected to the database")

        products = fetch_product_data()
        if not products:
            return jsonify({"message": "No products fetched from API."}), 500

        for product in products:
            insert_product_data(product, conn)

        return jsonify({"message": "Products processed successfully"}), 200
    except Exception as e:
        logging.error(f"Error in database operations: {e}")
        return jsonify({"error": "Error processing products"}), 500
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

@app.route('/display_table', methods=['GET'])
def display_table():
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logging.info("Connected to the database")

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productlist")
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"message": "No products found in database."}), 404

        # Create a PrettyTable to display the data
        table = PrettyTable()
        table.field_names = ["Product ID", "Name", "Price", "Regular Price", "Sale Price", "Status", "Stock Status", "Category"]
        
        # Setting alignment for each column for better formatting
        for col in table.field_names:
            table.align[col] = "l"  # Align text to the left for all columns (you can change to "r" for right)

        # Adding rows to the table (only first 8 columns as per your design)
        for row in rows:
            table.add_row(row[:8])

        # Convert table to HTML preformatted text for better rendering in browser
        table_html = f"<pre>{table}</pre>"

        return table_html

    except Exception as e:
        logging.error(f"Error fetching data from the database: {e}")
        return jsonify({"error": "Error displaying product table"}), 500
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
