import pandas as pd
from sqlalchemy import create_engine

# 1. DB 연결
engine = create_engine('postgresql://postgres:pass@localhost:5432/postgres')
df = pd.read_sql("SELECT * FROM porsche_tax_records", engine)

# 2. 세무 누수(Leakage) 계산 로직
# Leakage = (기대 세액) - (실제 적용 세액)
df['expected_tax'] = df['net_amount'] * (df['expected_vat_rate'] / 100)
df['applied_tax'] = df['net_amount'] * (df['applied_vat_rate'] / 100)
df['tax_gap'] = df['expected_tax'] - df['applied_tax']

# 3. 국가별/고객유형별 리스크 요약
audit_summary = df.groupby(['receiver_country', 'customer_type']).agg({
    'id': 'count',
    'net_amount': 'sum',
    'tax_gap': 'sum'
}).rename(columns={'id': 'transaction_count'}).reset_index()

# 4. 세무 리스크가 큰 순서대로 정렬
# tax_gap이 +이면 세금을 덜 낸 것(추징 위험), -이면 더 낸 것(환급 필요)
audit_summary = audit_summary.sort_values(by='tax_gap', ascending=False)

print("--- Porsche Tax Compliance: Financial Risk Report ---")
print(audit_summary.to_string(index=False, float_format="{:,.2f}".format))

# 전체 리스크 합계 계산
total_risk = audit_summary['tax_gap'].abs().sum()
print(f"\n[SUMMARY] Total Financial Exposure (Risk Amount): EUR {total_risk:,.2f}")
