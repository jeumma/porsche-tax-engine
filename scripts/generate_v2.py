import pandas as pd
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from faker import Faker

fake = Faker()
engine = create_engine('postgresql://postgres:pass@localhost:5432/postgres')

# Configuration for EU transaction simulation
countries = ['DEU', 'AUT', 'FRA', 'ITA', 'ESP']
vat_rates = {'DEU': 19.0, 'AUT': 20.0, 'FRA': 20.0, 'ITA': 22.0, 'ESP': 21.0}
services = ['Leasing', 'Subscription', 'Insurance']

data = []
for _ in range(1000):
    sender = 'DEU' # Assuming PFS HQ in Germany
    receiver = random.choice(countries)
    cust_type = random.choice(['B2B', 'B2C'])
    service = random.choice(services)
    
    # --- CORE TAX LOGIC ENGINE ---
    is_reverse = False
    if sender == receiver:
        expected = 19.0 # Domestic German rate
    elif cust_type == 'B2B':
        expected = 0.0  # EU B2B Reverse Charge mechanism
        is_reverse = True
    else:
        expected = vat_rates[receiver] # B2C Destination principle
        
    # --- Injecting Intentional Errors (5% probability) ---
    if random.random() < 0.05:
        applied = expected + random.choice([5.0, -5.0, 10.0])
    else:
        applied = expected

    data.append({
        'transaction_date': datetime(2025, 1, 1) + timedelta(days=random.randint(0, 400)),
        'sender_country': sender,
        'receiver_country': receiver,
        'customer_type': cust_type,
        'service_type': service,
        'vat_id': f"{receiver}{fake.random_number(digits=8)}" if cust_type == 'B2B' else None,
        'net_amount': round(random.uniform(5000, 150000), 2),
        'applied_vat_rate': applied,
        'expected_vat_rate': expected,
        'is_reverse_charge': is_reverse
    })

# Append data to PostgreSQL
df = pd.DataFrame(data)
df.to_sql('porsche_tax_records', engine, if_exists='append', index=False)
print("Success! 1,000 advanced tax records have been generated and stored.")
