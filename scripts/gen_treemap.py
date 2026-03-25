import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# 1. DB 데이터 로드 및 감사(Audit) 로직 실행
engine = create_engine('postgresql://postgres:pass@localhost:5432/postgres')
df = pd.read_sql("SELECT * FROM porsche_tax_records", engine)

df['expected_tax'] = df['net_amount'] * (df['expected_vat_rate'] / 100)
df['applied_tax'] = df['net_amount'] * (df['applied_vat_rate'] / 100)
df['tax_gap'] = df['expected_tax'] - df['applied_tax']

# 2. 트리맵용 데이터 집계 (카테고리별 합계)
treemap_data = df.groupby(['receiver_country', 'customer_type']).agg({
    'net_amount': 'sum',
    'tax_gap': 'sum'
}).reset_index()

# tax_gap의 절대값을 크기로 사용 (크기는 비중, 색상은 리스크 종류)
treemap_data['abs_tax_gap'] = treemap_data['tax_gap'].abs()

# 3. 트리맵 생성 (Plotly Express)
fig = px.treemap(treemap_data, 
                 path=['receiver_country', 'customer_type'], # 계층 구조
                 values='abs_tax_gap',                     # 사각형 크기 (리스크 규모)
                 color='tax_gap',                          # 색상 (세무 누수 방향)
                 color_continuous_scale='RdBu_r',          # 파란색(-, 과다납부) -> 빨간색(+, 미납)
                 color_continuous_midpoint=0,              # 0을 기준으로 색상 분리
                 hover_data=['net_amount'],              # 마우스 올렸을 때 보여줄 데이터
                 title='PFS Global Tax Risk Portfolio (Treemap)')

# 4. HTML 파일로 저장 (인터랙티브 기능 유지)
fig.write_html('tax_risk_treemap.html')
print("성공! 인터랙티브 트리맵 리포트가 'tax_risk_treemap.html'로 저장되었습니다.")
