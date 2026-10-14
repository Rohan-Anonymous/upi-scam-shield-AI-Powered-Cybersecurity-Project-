# upi-scam-shield-AI-Powered-Cybersecurity-Project-
AI-powered UPI scam risk screening and multilingual SMS detection using machine learning, Python, and FastAPI.


# 🛡️ UPI Scam Shield

### AI-Assisted UPI Risk Screening & Multilingual SMS Scam Detection

**UPI Scam Shield** is an AI-powered cybersecurity prototype designed to help users identify suspicious UPI-related risk indicators and potentially fraudulent SMS messages. It combines rule-based risk analysis, machine learning, and Hindi explanations to make scam awareness more accessible.

**Developed by:** Cyber_Anonymous  
**Institution:** Shri Govindrao Wanjari College of Engineering and Technology (GWCET), Nagpur  
**Project Category:** AI in Cyber Security & Defence

---

## 🚀 Key Features

- **Hybrid UPI Risk Scoring:** Combines rule-based checks with a Random Forest machine learning model.
- **Multilingual SMS Detection:** Analyses Hindi, Hinglish, and English messages using TF-IDF and Logistic Regression.
- **Risk Classification:** Displays GREEN, YELLOW, or RED risk levels.
- **Explainable Results:** Provides risk indicators and recommended safety actions.
- **Hindi Explanations:** Helps users understand warnings through Hindi text and voice output.
- **Community Reporting:** Supports UPI-related reports and displays report information.
- **Dashboard & Alerts:** Provides statistics and recent report information for demonstration.

## 🧠 How It Works

### 1. UPI Risk Screening

The UPI risk engine examines selected indicators, including:

- Suspicious keywords in UPI IDs or messages
- Community report counts
- Unusual numeric patterns
- UPI ID format
- Urgent or threatening message language
- Transaction amount as a contextual signal
- UPI collect-request status

The current implementation combines the rule-based score and Random Forest score using the following formula:

`Final Score = 0.6 × Rule Score + 0.4 × ML Score`

The result is classified as:

- **GREEN:** Score below 30
- **YELLOW:** Score from 30 to below 60
- **RED:** Score of 60 or above

These labels represent prototype risk-screening results and are not confirmed fraud verdicts.

### 2. SMS Scam Detection

The SMS detection component uses:

- **TF-IDF:** Converts message text into numerical features.
- **Logistic Regression:** Classifies messages based on learned text patterns.

The detector is designed for Hindi, Hinglish, and English inputs and provides a classification with supporting information and a Hindi explanation.

### 3. Hindi Explanation & Voice

The prototype provides template-based Hindi explanations using the model's classification and relevant signals. Voice output is available where supported by the application.

## 🏗️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Machine Learning | scikit-learn |
| Numerical Computing | NumPy |
| Database | SQLite |
| Application Server | Uvicorn |
| Frontend | Existing web interface |

## 📂 Application Pages

The prototype documents the following pages:

- `/` — Main application
- `/sms.html` — SMS detection
- `/alerts.html` — Alerts and reports
- `/dashboard
