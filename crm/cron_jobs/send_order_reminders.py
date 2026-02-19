import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL client setup
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date 7 days ago
seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()

# GraphQL query to fetch orders from the last 7 days
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
    result = client.execute(query, variable_values=params)
    orders = result.get("orders", [])

    if orders:
        with open("/tmp/order_reminders_log.txt", "a") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for order in orders:
                order_id = order["id"]
                customer_email = order["customer"]["email"]
                log_file.write(f"{timestamp} - Order ID: {order_id}, Customer Email: {customer_email}\n")
    print("Order reminders processed!")
except Exception as e:
    print(f"Error fetching orders: {e}")
