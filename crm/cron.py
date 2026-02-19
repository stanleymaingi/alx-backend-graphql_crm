import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# ===========================
# Heartbeat Logger
# ===========================
HEARTBEAT_LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """Logs a heartbeat message every 5 minutes."""
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    # Append message to log file
    with open(HEARTBEAT_LOG_FILE, "a") as f:
        f.write(message)

    # Optional: verify GraphQL endpoint
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=1
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("query { hello }")
        client.execute(query)
    except Exception as e:
        with open(HEARTBEAT_LOG_FILE, "a") as f:
            f.write(f"{timestamp} GraphQL endpoint check failed: {e}\n")


# ===========================
# Order Reminder Script
# ===========================
ORDER_REMINDER_LOG_FILE = "/tmp/order_reminders_log.txt"

def send_order_reminders():
    """
    Queries orders from the last 7 days and logs reminders.
    """
    # Calculate date 7 days ago
    seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()

    # GraphQL query to fetch recent orders
    query = gql("""
    query GetRecentOrders($since: DateTime!) {
      orders(filter: {order_date_gte: $since}) {
        id
        customer {
          email
        }
        order_date
      }
    }
    """)
    params = {"since": seven_days_ago}

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        result = client.execute(query, variable_values=params)
        orders = result.get("orders", [])

        if orders:
            with open(ORDER_REMINDER_LOG_FILE, "a") as log_file:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for order in orders:
                    order_id = order["id"]
                    customer_email = order["customer"]["email"]
                    log_file.write(f"{timestamp} - Order ID: {order_id}, Customer Email: {customer_email}\n")

        print("Order reminders processed!")
    except Exception as e:
        with open(ORDER_REMINDER_LOG_FILE, "a") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{timestamp} - Error fetching orders: {e}\n")


            LOW_STOCK_LOG_FILE = "/tmp/low_stock_updates_log.txt"

def update_low_stock():
    """
    Executes the UpdateLowStockProducts mutation and logs updates.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    mutation = """
    mutation UpdateLowStockProducts($increment: Int!) {
      updateLowStockProducts(increment: $increment) {
        updatedProducts {
          name
          stock
        }
        message
      }
    }
    """
    variables = {"increment": 10}

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        result = client.execute(gql(mutation), variable_values=variables)

        updated_products = result["updateLowStockProducts"]["updatedProducts"]

        if updated_products:
            with open(LOW_STOCK_LOG_FILE, "a") as f:
                for product in updated_products:
                    f.write(f"{timestamp} - Product: {product['name']}, New Stock: {product['stock']}\n")

        print("Low-stock products updated!")
    except Exception as e:
        with open(LOW_STOCK_LOG_FILE, "a") as f:
            f.write(f"{timestamp} - Error updating low-stock products: {e}\n")
