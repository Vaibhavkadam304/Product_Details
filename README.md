# WooCommerce Product Data Integration with PostgreSQL

This Flask app fetches product data from the WooCommerce API and stores it in a PostgreSQL database. It also displays the data in a formatted table.

## Requirements

- Python 3.x
- PostgreSQL database
- WooCommerce API credentials (Consumer Key & Secret)

## Setup

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/Product_Details.git
    cd Product_Details
    ```

2. **Create and activate a virtual environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure the database and WooCommerce API credentials**:

    - Update database connection details in `app.py`.
    - Update WooCommerce API keys (`CONSUMER_KEY`, `CONSUMER_SECRET`).

5. **Create the PostgreSQL table**:

    ```sql
    CREATE TABLE productlist (
        product_id INT PRIMARY KEY,
        name VARCHAR(255),
        price DECIMAL(10, 2),
        regular_price DECIMAL(10, 2),
        sale_price DECIMAL(10, 2),
        status VARCHAR(50),
        on_sale BOOLEAN,
        description TEXT,
        sku VARCHAR(50),
        stock_status VARCHAR(50),
        category VARCHAR(255),
        total_sales INT,
        average_rating DECIMAL(3, 2),
        rating_count INT,
        store_name VARCHAR(255),
        store_url VARCHAR(255),
        store_location TEXT
    );
    ```

6. **Run the app**:

    ```bash
    python app.py
    ```

    The app will be available at `http://0.0.0.0:5000`.

## Endpoints

- **/fetch_products**: Fetches product data from WooCommerce and inserts it into the PostgreSQL database.
- **/display_table**: Displays the product data from the database in a formatted table.

## License

MIT License.
