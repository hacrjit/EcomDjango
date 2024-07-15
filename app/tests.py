# Import the Customer model
from .models import Customer

# Query for a specific customer by name (assuming names are unique for simplicity)
customer = Customer.objects.filter(name="John Doe").first()

# Check if the customer exists and then access the ID
if customer:
    customer_id = customer.id
    print(f"The customer ID is: {customer_id}")
else:
    print("Customer not found.")