import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest

# 1. Load data from PostgreSQL
engine = create_engine('postgresql://postgres:pass@localhost:5432/postgres')
df = pd.read_sql("SELECT * FROM porsche_tax_records", engine)

# 2. Feature Engineering: Providing hints for the AI
df['rate_diff'] = (df['applied_vat_rate'] - df['expected_vat_rate']).abs()
df['amount_log'] = np.log1p(df['net_amount'])
# Flagging B2B transactions with incorrect zero-rating
df['b2b_issue'] = ((df['customer_type'] == 'B2B') & (df['applied_vat_rate'] > 0)).astype(int)

# Select features for training
features = ['amount_log', 'applied_vat_rate', 'rate_diff', 'b2b_issue']
X = df[features].values 

# 3. Model Training: Learning normal transaction patterns
model = IsolationForest(contamination=0.03, random_state=42)
model.fit(X) 

# 4. Anomaly Detection
df['anomaly_score'] = model.decision_function(X) # Anomaly score (-0.5 to 0.5)
df['is_anomaly'] = model.predict(X) # -1 indicates an anomaly

# 5. Explainable AI (XAI): Heuristic explanations for detected anomalies
def explain_anomaly(row):
    reasons = []
    if row['rate_diff'] > 0:
        reasons.append(f"Tax Rate Mismatch ({row['applied_vat_rate']}% vs {row['expected_vat_rate']}%)")
    if row['net_amount'] > df['net_amount'].quantile(0.95):
        reasons.append("High Value Transaction")
    if row['b2b_issue'] == 1:
        reasons.append("B2B Zero-rating Violation")
    return ", ".join(reasons) if reasons else "Statistical Outlier"

# Filter and report anomalies
anomalies = df[df['is_anomaly'] == -1].copy()
anomalies['reason'] = anomalies.apply(explain_anomaly, axis=1)

print("--- Porsche AI Audit: Explainable Anomaly Report ---")
if not anomalies.empty:
    print(anomalies[['id', 'receiver_country', 'net_amount', 'applied_vat_rate', 'reason']].head(15))
else:
    print("No anomalies detected.")
