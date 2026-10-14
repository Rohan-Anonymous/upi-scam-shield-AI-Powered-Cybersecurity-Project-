# UPI Scam Shield v3 (AI)
Run: run.bat (Windows) ya ./run.sh  ->  http://127.0.0.1:8000
Pages: / | /sms.html | /alerts.html | /dashboard.html | /docs | /ai/info

## AI kya hai
1. Fraud model: Random Forest (scikit-learn), 9 features. Final score = 60% rules + 40% ML (hybrid).
2. SMS detector: TF-IDF + Logistic Regression (Hindi/Hinglish/English).
3. Hindi explanation: model ke signals se template-based Devanagari text (offline), voice me bhi bolta hai.
Dono models SYNTHETIC data par startup pe train hote hain. Accuracy ka bada daava mat karo.
