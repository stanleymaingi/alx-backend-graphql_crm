import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_report_log.txt"

@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report with total customers, orders, and revenue.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = gql("""
    query {
      totalCustomers: customersCount
      totalOrders: ordersCount
      totalRevenue: ordersAggregate {
        sum {
          totalamount
        }
      }
    }
    """)

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        result = client.execute(query)

        total_customers = result.get("totalCustomers", 0)
        total_orders = result.get("totalOrders", 0)
        total_revenue = result.get("totalRevenue", {}).get("sum", {}).get("totalamount", 0)

        log_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"

        with open(LOG_FILE, "a") as f:
            f.write(log_message)

        print("CRM weekly report generated!")

    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} - Error generating report: {e}\n")
