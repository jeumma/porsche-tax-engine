Porsche Tax Compliance & AI Audit Engine

    An automated end-to-end solution for EU VAT compliance, tax leakage analysis, and AI-driven anomaly detection in multinational financial services.

Project Overview

This project simulates a Tax Technology (TaxTech) solution designed for global entities like Porsche Financial Services (PFS). It addresses the complexity of EU cross-border transactions by automating VAT determination, validating compliance, and using Machine Learning to detect financial risks that traditional rule-based systems might miss.
Key Problems Solved

    VAT Complexity: Automates the "Destination Principle" and "Reverse Charge" logic for B2B/B2C transactions across the EU.

    Financial Risk: Identifies "Tax Leakage" (underpaid or overpaid tax) through a real-time audit engine.

    Anomaly Detection: Uses Unsupervised ML to flag suspicious patterns, such as incorrect zero-rating or high-value tax mismatches.

Tech Stack

    Language: Python 3.12

    Database: PostgreSQL (Dockerized)

    ML/AI: Scikit-learn (Isolation Forest), StandardScaler

    Dashboard: Streamlit

    Visualization: Plotly Express (Interactive Treemaps & Scatter Plots)

    DevOps: Docker, Python-dotenv, .gitignore optimization

Core Features
1. AI-Powered Anomaly Detection

Instead of relying solely on hard-coded rules, the system employs the Isolation Forest algorithm to detect statistical outliers.

    Explainable AI (XAI): Provides human-readable reasons for each flagged anomaly (e.g., "B2B Zero-rating Violation").

    Mathematical Foundation: The anomaly score s(x,n) is calculated based on the path length h(x) to isolate a point:
    s(x,n)=2−c(n)E(h(x))​

    Points with a score near 1 are flagged as high-risk tax anomalies.

2. Strategic Tax Risk Treemap

Visualizes the global tax portfolio using interactive treemaps.

    Size: Represents the net transaction volume.

    Color: Indicates the "Tax Gap" (Red for underpaid risk, Blue for overpaid/refund scenarios).

3. "What-if" Tax Simulation

Allows tax managers to simulate global VAT rate changes. The engine recalculates the entire portfolio's risk exposure in real-time based on the adjusted rates.
4. Automated VAT ID Validator

Implements country-specific Regex patterns for 10+ EU nations (DE, FR, IT, etc.) to ensure B2B compliance and prevent reporting errors.
Project Structure
Plaintext

porsche-tax-engine/
├── app.py                # Main Streamlit Dashboard
├── scripts/              # Supplementary tools
│   ├── generate_v2.py    # Synthetic Tax Data Generator
│   └── advanced_ai_audit.py # Standalone AI Audit Script
├── .streamlit/
│   └── secrets.toml      # DB Credentials (Excluded from Git)
├── .gitignore            # Git exclusion rules
└── requirements.txt      # Python dependencies

Getting Started
1. Clone & Environment
Bash

# Clone the repository
git clone https://github.com/jeumma/porsche-tax-engine.git
cd porsche-tax-engine

# Create and activate virtual environment
python3 -m venv porsche_env
source porsche_env/bin/activate

# Install dependencies
pip install -r requirements.txt

2. Database Setup

Ensure Docker is running and your PostgreSQL container is active. Configure your credentials in .streamlit/secrets.toml:
Ini, TOML

[database]
url = "postgresql://username:password@localhost:5432/dbname"

3. Run the App
Bash

streamlit run app.py

Academic & Professional Context

This project bridges the gap between Computer Science and Accounting & Finance. It demonstrates the technical capability to build scalable data architectures while applying deep domain knowledge of international tax law and EU compliance trends such as ViDA (VAT in the Digital Age).
