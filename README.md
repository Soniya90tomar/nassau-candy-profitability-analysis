# 🍬 Nassau Candy Distributor - Margin Performance & Profitability Analysis

This repository contains an exploratory data analysis framework and an interactive Streamlit dashboard designed to evaluate structural margin variances, optimize product lines, and highlight profit concentration risks for Nassau Candy Distributor.

---

## 💻 Project Status & Environment
This application is designed to run in a local development environment. Follow the steps under **Local Installation & Setup** below to spin up and view the interactive Streamlit dashboard on your machine.

---

## 📊 Project Executive Summary & Key Insights
Instead of keeping insights locked in a static text document, the core findings of this analytical study are summarized directly below:

* **Data Diagnostics & Engineering:** Cleaned and processed raw distribution sales data using Pandas. Handled missing values, treated anomalous records, and engineered key base metrics such as *Gross Margin Percentage* and *Profit per Unit*.
* **Pareto (80/20 Rule) Analysis:** Evaluated cumulative profit contributions against total sales volumes to identify high-revenue product lines operating on critically thin margins that expose the distributor to structural revenue concentration risks.
* **Division Performance Isolation:** Segmented performance metrics across distinct business divisions to isolate operational inefficiencies and provide actionable indicators for pricing restructuring, cost renegotiations, and portfolio rationalization.

---

## 📁 Repository Structure
* **`dashboard.py`** - Core Streamlit web application script managing interactive UI filters, sidebar selectors, and responsive visualization plots.
* **`Nassau_Candy_Profitability_Analysis (1).ipynb`** - Jupyter Notebook containing the backend pipeline: data cleansing, statistical summaries, and rigorous exploratory data analysis (EDA).
* **`Nassau_Candy_Distributor.csv`** - Underlying transactional source dataset utilized by both the notebook and the active web application.
* **`requirements.txt`** - Text configuration listing specific Python library dependencies and system benchmarks required to deploy the environment.

---

## 🛠️ Local Installation & Setup

Follow these steps to download the repository and spin up the dashboard locally:

1. **Clone the repository:**
```bash
   git clone [https://github.com/Soniya90tomar/nassau-candy-profitability-analysis.git](https://github.com/Soniya90tomar/nassau-candy-profitability-analysis.git)
2. **Navigate into the project directory:**
```bash
   cd nassau-candy-profitability-analysis
