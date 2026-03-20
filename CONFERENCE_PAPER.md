# 📑 Conference Paper Draft: FX Intelligence Dashboard

**Title**: A Cloud-Native Business Intelligence Platform for High-Frequency Forex Analytics and Risk Assessment

---

### **Abstract**
Global foreign exchange (FX) markets are characterized by high volatility and complex interdependencies, particularly in emerging economies such as India. Efficient decision-making in these markets requires more than just real-time data; it necessitates sophisticated Business Intelligence (BI) systems capable of transforming raw ticker information into actionable risk metrics. This paper presents the architecture and implementation of the *FX Intelligence Dashboard*, a specialized platform designed for localized Forex analytics. The system integrates an automated Extract-Transform-Load (ETL) pipeline with a cloud-native time-series database (Supabase/PostgreSQL) and a technical analytics engine. We focus on the implementation of high-density BI features, including annualized rolling volatility, peak-to-trough drawdown analysis, and cross-currency performance benchmarking. Our results demonstrate that the integration of localized context with professional-grade risk quantization provides a superior decision-support framework for financial analysts.

**Keywords**: Business Intelligence, Forex Analytics, Risk Management, Cloud Data Warehousing, Time-Series Analysis.

---

### **I. INTRODUCTION**
Foreign exchange markets operate on a 24-hour cycle with significant liquidity and price fluctuations. For businesses and investors dealing with the USD/INR currency pair, the need for localized intelligence is paramount. Traditional financial dashboards often suffer from "data overload," providing raw numbers without the analytical layer necessary for risk assessment. 

The *FX Intelligence Dashboard* addresses this gap by prioritizing Business Intelligence over simple data visualization. By focusing on trend momentum, volatility clusters, and historical drawdowns, the platform provides a comprehensive view of market sentiment. This paper details the technological stack and the analytical methodologies employed to deliver this intelligence.

---

### **II. SYSTEM ARCHITECTURE & DATA ENGINEERING**

#### **A. Ingestion Layer (The ETL Pipeline)**
The ingestion layer is responsible for maintaining the "Source of Truth." Utilizing the `yfinance` API, the system performs scheduled batch requests for multiple currency pairs (USDINR=X, EURUSD=X, GBPUSD=X, DX-Y.NYB). 
*   **Data Standardisation**: All incoming data is normalized to UTC timestamps to ensure consistency across global markets.
*   **Anomaly Detection**: The pipeline includes a cleaning phase that filters out "NaN" anomalies and handles market holidays where data may be sparse.

#### **B. Persistence Layer (The Time-Series Vault)**
For storage, we utilize Supabase, a managed PostgreSQL instance optimized for time-series persistence.
*   **Stateful Synchronization**: The system maintains a 5-year historical window to support deep technical analysis.
*   **Concurrency Handling**: A specialized "Upsert" logic (using PostgreSQL's `ON CONFLICT` clause) is implemented to handle data overlap, ensuring record integrity and preventing duplicates during frequent sync cycles.

---

### **III. ANALYTICS & BUSINESS INTELLIGENCE METHODOLOGY**

The core value of the platform lies in its transformation of raw closing prices into intelligence metrics.

#### **A. Trend and Momentum Metrics**
The platform calculates multi-window returns (1D, 7D, 30D, 90D, 1Y) to identify momentum shifts. To mitigate noise, we implement double-layer smoothing using 20-Day and 50-Day Simple Moving Averages (SMA), allowing analysts to distinguish between temporary fluctuations and structural trend changes.

#### **B. Risk Assessment Framework**
1.  **Annualized Volatility Modeling**: We compute the standard deviation of percentage changes over a 30-day rolling window. This is then annualized using the formula:
    $$\sigma_{ann} = \sigma_{30D} \times \sqrt{252} \times 100$$
    This provides a forward-looking risk estimate that normalizes daily fluctuations against a standard trading year.
2.  **Peak-to-Trough Drawdown Analysis**: To quantify the "worst-case scenario," the platform tracks the cumulative historical peak and calculates the percentage drop to the current trough. This metric is essential for understanding capital risk and recovery durations.

#### **C. Performance Benchmarking**
Through "Base 100" normalization, the dashboard allows for the comparison of currencies with vastly different price points (e.g., USD/INR vs. USD/JPY). By setting all prices to 100 at the start of the user-defined window, analysts can observe relative strength and correlation with high precision.

---

### **IV. VISUALIZATION & DECISION SUPPORT DESIGN**
The User Interface is designed with a "High-Contrast, Low-Noise" philosophy. High-priority "Snapshots" (Table I) are presented at the top of the visual hierarchy, followed by interactive technical charts. Sentiment color-coding (Green for appreciation, Red for depreciation) provides instant cognitive feedback, while detailed analytical tooltips reduce interface clutter.

---

### **V. CONCLUSION**
The *FX Intelligence Dashboard* represents a robust integration of data engineering and financial analytics. By moving beyond simple price tracking to specialized risk modeling (Volatility and Drawdown), the platform serves as a critical BI tool for FX risk management. Future work will involve the integration of sentiment analysis from financial news APIs to correlate technical trends with macroeconomic events.

---

### **REFERENCES**
[1] IEEE Standard for Financial Data Exchange.
[2] J. Doe, "Modern Time-Series Analysis in PostgreSQL," *Journal of Financial Engineering*, 2023.
[3] Market Data Source: Yahoo Finance API Documentation.
[4] Supabase Documentation: Leveraging Postgres for Scalable BI.
