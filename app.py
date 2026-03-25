import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np

# ============================================================
# 1. Initial Setup
# ============================================================
st.set_page_config(page_title="PFS Tax Compliance Suite", layout="wide")

# ── DB Connection (using st.secrets - loaded from secrets.toml) ──────
# secrets.toml example:
# [database]
# url = "postgresql://user:password@host:5432/dbname"
@st.cache_resource
def get_engine():
    try:
        db_url = st.secrets["database"]["url"]
        engine = create_engine(db_url, pool_pre_ping=True)
        # Verify connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except KeyError:
        st.error("DB config missing: add [database] url to .streamlit/secrets.toml")
        st.stop()
    except OperationalError as e:
        st.error(f"DB connection failed: {e}")
        st.stop()

@st.cache_data
def load_data(_engine):
    try:
        return pd.read_sql("SELECT * FROM porsche_tax_records", _engine)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

engine = get_engine()
df = load_data(engine)

# ============================================================
# 2. Sidebar - Filters & Simulation
# ============================================================
st.sidebar.header("Simulation & Filters")
selected_country = st.sidebar.multiselect(
    "Select Countries",
    options=df['receiver_country'].unique(),
    default=df['receiver_country'].unique()
)

st.sidebar.subheader("Tax Rate Simulator")
sim_rate_change = st.sidebar.slider(
    "Global VAT Rate Change (%)", -5.0, 5.0, 0.0, step=0.5
)

st.sidebar.subheader("Anomaly Detection")
contamination = st.sidebar.slider(
    "Anomaly Sensitivity (contamination)", 0.01, 0.20, 0.05, step=0.01,
    help="Proportion of transactions to classify as anomalies. Higher values flag more transactions."
)

# ============================================================
# 3. Data Processing
# ============================================================
filtered_df = df[df['receiver_country'].isin(selected_country)].copy()

# Safely cast to float before applying simulation
filtered_df['expected_vat_rate'] = filtered_df['expected_vat_rate'].astype(float)
filtered_df['applied_vat_rate']  = filtered_df['applied_vat_rate'].astype(float)
filtered_df['net_amount']        = filtered_df['net_amount'].astype(float)

filtered_df['expected_vat_rate'] += sim_rate_change

filtered_df['tax_gap'] = (
    filtered_df['net_amount'] * (filtered_df['expected_vat_rate'] / 100)
  - filtered_df['net_amount'] * (filtered_df['applied_vat_rate']  / 100)
)

# ============================================================
# 4. VAT ID Validation (per country)
# ============================================================
VAT_PATTERNS: dict[str, str] = {
    "DE": r'^DE[0-9]{9}$',                    # Germany
    "FR": r'^FR[0-9A-Z]{2}[0-9]{9}$',         # France
    "GB": r'^GB([0-9]{9}|[0-9]{12}|GD[0-4][0-9]{2}|HA[5-9][0-9]{2})$',  # United Kingdom
    "NL": r'^NL[0-9]{9}B[0-9]{2}$',           # Netherlands
    "IT": r'^IT[0-9]{11}$',                    # Italy
    "ES": r'^ES[A-Z0-9][0-9]{7}[A-Z0-9]$',    # Spain
    "AT": r'^ATU[0-9]{8}$',                    # Austria
    "BE": r'^BE[0-9]{10}$',                    # Belgium
    "PL": r'^PL[0-9]{10}$',                    # Poland
    "SE": r'^SE[0-9]{12}$',                    # Sweden
}
FALLBACK_PATTERN = r'^[A-Z]{2}[0-9A-Z]{8,12}$'

def check_vat_format(row) -> str:
    vat = row.get('vat_id', '')
    if not vat or pd.isna(vat):
        return "N/A (B2C)"
    country = str(row.get('receiver_country', '')).upper()
    pattern = VAT_PATTERNS.get(country, FALLBACK_PATTERN)
    return "Valid" if re.match(pattern, str(vat).upper()) else "Invalid"

filtered_df['vat_status'] = filtered_df.apply(check_vat_format, axis=1)

# ============================================================
# 5. Anomaly Detection (IsolationForest)
# ============================================================
FEATURE_COLS = ['net_amount', 'tax_gap', 'expected_vat_rate', 'applied_vat_rate']

@st.cache_data
def detect_anomalies(data: pd.DataFrame, contamination_rate: float) -> pd.Series:
    """
    Detect anomalous transactions using IsolationForest.
    Returns: Series of -1 (anomaly) / 1 (normal)
    """
    features = data[FEATURE_COLS].copy().fillna(0)
    scaler   = StandardScaler()
    scaled   = scaler.fit_transform(features)

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination_rate,
        random_state=42,
        n_jobs=-1
    )
    return pd.Series(model.fit_predict(scaled), index=data.index)

if len(filtered_df) >= 10:
    filtered_df['anomaly'] = detect_anomalies(filtered_df, contamination)
    filtered_df['anomaly_label'] = filtered_df['anomaly'].map({1: "Normal", -1: "Anomaly"})
else:
    st.warning("Insufficient data for anomaly detection (minimum 10 records required).")
    filtered_df['anomaly']       = 1
    filtered_df['anomaly_label'] = "Normal"

anomalies = filtered_df[filtered_df['anomaly'] == -1]

# ============================================================
# 6. Main Dashboard
# ============================================================
st.title("Porsche Financial Services: Tax Engine v3.0")

if sim_rate_change != 0.0:
    st.info(f"Simulation Mode: expected VAT rate adjusted by {sim_rate_change:+.1f}%")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Selected Records",  len(filtered_df))
col2.metric("Total Tax Gap",     f"€{filtered_df['tax_gap'].sum():,.2f}")
col3.metric("Avg. Net Amount",   f"€{filtered_df['net_amount'].mean():,.0f}")
col4.metric("Anomalies Detected", len(anomalies),
            delta=f"{len(anomalies)/max(len(filtered_df),1)*100:.1f}%",
            delta_color="inverse")

st.divider()

# ── Section 1: VAT ID Validation ──────────────────────────────
st.subheader("1. VAT ID Format Compliance Check")

invalid_vats = filtered_df[filtered_df['vat_status'] == "Invalid"]
valid_count  = (filtered_df['vat_status'] == "Valid").sum()
b2c_count    = (filtered_df['vat_status'] == "N/A (B2C)").sum()

v1, v2, v3 = st.columns(3)
v1.metric("Valid",   valid_count)
v2.metric("Invalid", len(invalid_vats), delta_color="inverse")
v3.metric("B2C",     b2c_count)

if not invalid_vats.empty:
    st.error(f"{len(invalid_vats)} transaction(s) with invalid VAT ID format detected.")
    st.dataframe(
        invalid_vats[['id', 'receiver_country', 'vat_id', 'vat_status']],
        use_container_width=True
    )
else:
    st.success("All VAT ID formats are valid.")

st.divider()

# ── Section 2: Anomaly Detection Results ─────────────────────────────
st.subheader("2. Anomaly Detection (IsolationForest)")

if not anomalies.empty:
    st.warning(f"{len(anomalies)} anomalous transaction(s) detected.")

    # Scatter plot: normal vs anomaly
    fig_scatter = px.scatter(
        filtered_df,
        x='net_amount',
        y='tax_gap',
        color='anomaly_label',
        color_discrete_map={"Normal": "#4A90D9", "Anomaly": "#E74C3C"},
        hover_data=['id', 'receiver_country', 'vat_id', 'customer_type'],
        opacity=0.7,
        title="Net Amount vs Tax Gap — Anomaly Distribution"
    )
    fig_scatter.update_traces(marker=dict(size=8))
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Bar chart: anomaly count by country
    anomaly_by_country = (
        anomalies.groupby('receiver_country')
                 .size()
                 .reset_index(name='count')
                 .sort_values('count', ascending=False)
    )
    fig_bar = px.bar(
        anomaly_by_country,
        x='receiver_country', y='count',
        color='count',
        color_continuous_scale='Reds',
        title="Anomalous Transactions by Country"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("**Anomaly Transaction Detail**")
    st.dataframe(
        anomalies[['id', 'receiver_country', 'customer_type',
                   'net_amount', 'tax_gap', 'applied_vat_rate',
                   'expected_vat_rate', 'vat_id', 'vat_status']].sort_values('tax_gap'),
        use_container_width=True
    )
else:
    st.success("No anomalous transactions detected.")

st.divider()

# ── Section 3: Risk Treemap ───────────────────────────────────
st.subheader("3. Strategic Tax Risk Treemap")

fig_tree = px.treemap(
    filtered_df,
    path=['receiver_country', 'customer_type'],
    values='net_amount',
    color='tax_gap',
    color_continuous_scale='RdBu_r',
    color_continuous_midpoint=0,
    title="Tax Gap by Country / Customer Type"
)
st.plotly_chart(fig_tree, use_container_width=True)

st.divider()

# ── Section 4: Export ────────────────────────────────────────
st.subheader("4. Export & Reporting")

export_df = filtered_df.drop(columns=['anomaly'], errors='ignore')

c1, c2 = st.columns(2)

with c1:
    csv_all = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Audit Results (CSV)",
        data=csv_all,
        file_name='porsche_tax_audit_report.csv',
        mime='text/csv',
    )

with c2:
    if not anomalies.empty:
        csv_anomaly = anomalies.drop(columns=['anomaly'], errors='ignore') \
                               .to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Anomalies Only (CSV)",
            data=csv_anomaly,
            file_name='porsche_anomaly_transactions.csv',
            mime='text/csv',
        )
