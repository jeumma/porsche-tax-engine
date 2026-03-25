# 🏎️ Porsche Tax Compliance & AI Audit Engine

> **An automated end-to-end solution for EU VAT compliance, tax leakage analysis, and AI-driven anomaly detection in multinational financial services.**

## 📌 Project Overview
This project simulates a **Tax Technology (TaxTech)** solution designed for global entities like **Porsche Financial Services (PFS)**. It addresses the complexity of EU cross-border transactions by automating VAT determination, validating compliance, and using Machine Learning to detect financial risks that traditional rule-based systems might miss.

### 🔑 Key Problems Solved
* **VAT Complexity**: Automates the "Destination Principle" and "Reverse Charge" logic for B2B/B2C transactions across the EU.
* **Financial Risk**: Identifies "Tax Leakage" (underpaid or overpaid tax) through a real-time audit engine.
* **Anomaly Detection**: Uses Unsupervised ML to flag suspicious patterns, such as incorrect zero-rating or high-value tax mismatches.

---

## 🛠️ Tech Stack
* **Language**: Python 3.12
* **Database**: PostgreSQL (Dockerized)
* **ML/AI**: Scikit-learn (Isolation Forest), StandardScaler
* **Dashboard**: Streamlit
* **Visualization**: Plotly Express (Interactive Treemaps & Scatter Plots)
* **DevOps**: Docker, Python-dotenv, .gitignore optimization

---

## 🚀 Core Features

### 1. AI-Powered Anomaly Detection
Instead of relying solely on hard-coded rules, the system employs the **Isolation Forest** algorithm to detect statistical outliers.
* **Explainable AI (XAI)**: Provides human-readable reasons for each flagged anomaly (e.g., "B2B Zero-rating Violation").
* **Dynamic Sensitivity**: Adjustable contamination rates to tune the audit's strictness.

### 2. Strategic Tax Risk Treemap
Visualizes the global tax portfolio using interactive treemaps. 
* **Size**: Represents the net transaction volume.
* **Color**: Indicates the "Tax Gap" (Red for underpaid risk, Blue for overpaid/refund scenarios).

### 3. "What-if" Tax Simulation
Allows tax managers to simulate global VAT rate changes. The engine recalculates the entire portfolio's risk exposure in real-time based on the adjusted rates.

---

## 🏗️ System Architecture
1. **Data Layer**: 1,000+ synthetic high-fidelity tax records stored in a Dockerized PostgreSQL instance.
2. **Audit Engine**: Logic-based VAT determination based on EU Council Directive 2006/112/EC.
3. **ML Pipeline**: Feature engineering followed by Isolation Forest scoring.
4. **UI Layer**: A Streamlit-based web interface for real-time monitoring.EOF
cat README.md
cat  README.md
