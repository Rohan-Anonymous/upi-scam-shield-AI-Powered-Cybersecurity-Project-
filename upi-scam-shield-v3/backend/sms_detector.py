"""AI #2: Scam SMS detector. TF-IDF + Logistic Regression on SYNTHETIC template data (Hindi/Hinglish/English)."""
import re, random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

SCAM = [
 "Dear customer, your {bank} account will be blocked today. Update KYC now: http://{bank}-kyc-{x}.xyz/login",
 "{bank} alert: aapka account block ho jayega. Abhi KYC update karein is link par: bit.ly/{x}",
 "Congratulations! You won Rs {amt} lottery. Claim your prize now, click the link and share your UPI PIN",
 "Aapko {amt} rupaye cashback mila hai. Paisa lene ke liye link kholein aur UPI PIN daalein",
 "Urgent: your PAN is not linked, account suspended. Verify immediately http://{bank}-verify.top",
 "Refund of Rs {amt} pending. Scan this QR code to receive the money, jaldi karein warna expire ho jayega",
 "आपका {bank} खाता बंद हो जाएगा। अभी KYC अपडेट करें: http://kyc-{x}.xyz",
 "बधाई हो! आपने ₹{amt} की लॉटरी जीती है। इनाम पाने के लिए अभी लिंक पर क्लिक करें और UPI PIN बताएं",
 "Electricity bill unpaid, connection will be cut tonight. Call this number and pay immediately",
 "Work from home job, earn Rs {amt} daily. Send registration fee to this UPI ID and WhatsApp us",
 "Aapka parcel customs me ruka hai, Rs {amt} fee turant pay karein is link par: www.{x}.top",
 "Your card is blocked. Share OTP with our executive to unblock it now",
 "Sir, aapka loan approve ho gaya hai. Processing fee Rs {amt} abhi bhejein warna offer khatam",
 "{bank} KYC expired. Account will be frozen in 24 hours. Click here to update: {x}.xyz/kyc",
]
LEGIT = [
 "{bank}: Rs {amt} debited from A/c XX{n} on {d}. If not you, call the number on the back of your card",
 "Your OTP is {otp}. Do not share it with anyone. Valid for 10 minutes.",
 "Rs {amt} credited to your account XX{n}. Available balance Rs {amt2}",
 "Your order #{n} has been delivered. Thank you for shopping with us.",
 "Aapka {bank} statement ready hai. Netbanking me login karke dekhein.",
 "Reminder: your electricity bill of Rs {amt} is due on {d}. Pay via the official app.",
 "Hi, meeting kal 5 baje hai. Please confirm.",
 "Your appointment is confirmed for tomorrow 10 AM. Reply STOP to cancel.",
 "Aapka recharge Rs {amt} safal raha. Validity 28 din.",
 "Happy birthday! Party kal shaam ko hai, aa jana.",
 "आपका ट्रांजैक्शन सफल रहा। राशि ₹{amt}।",
 "Thanks for paying Rs {amt}. Your receipt is available in the app.",
 "Kal ghar aa jana, dinner hai. Mummy ne bola hai.",
 "Your OTP for login is {otp}. Never share this code with anyone, including bank staff.",
]
URL = re.compile(r"(https?://\S+|www\.\S+|\b\S+\.(xyz|top|ly)\b\S*)", re.I)
_prep = lambda t: URL.sub(" urltoken ", t)

def _data():
    rng = random.Random(7); X, y = [], []
    def fill(t): return t.format(bank=rng.choice(["SBI","PNB","HDFC","ICICI","Axis"]), amt=rng.choice([499,1500,5000,25000,98000]),
        n=rng.randint(1000,9999), x="".join(rng.choice("abcdefgh") for _ in range(5)), otp=rng.randint(100000,999999),
        d=rng.choice(["12 Oct","15 Oct","20 Oct"]), amt2=rng.choice([12000,45000,80000]))
    for _ in range(12):
        for t in SCAM: X.append(_prep(fill(t))); y.append(1)
        for t in LEGIT: X.append(_prep(fill(t))); y.append(0)
    return X, y

_X, _y = _data()
VEC = TfidfVectorizer(ngram_range=(1, 2), token_pattern=r"[^\s.,!?:;()\"'₹/]+", lowercase=True)
LR = LogisticRegression(C=5, max_iter=500).fit(VEC.fit_transform(_X), _y)
INFO_META = {"model": "TF-IDF + Logistic Regression", "train_samples": len(_X), "synthetic": True,
             "note": "Template-based dummy data; accuracy ka koi number real world ke liye maanya nahi hai."}
HI = {"RED": "यह मैसेज स्कैम लगता है। लिंक पर क्लिक न करें और अपना PIN या OTP किसी को न बताएं।",
      "YELLOW": "इस मैसेज पर शक है। बैंक की आधिकारिक ऐप या नंबर से पुष्टि करें।",
      "GREEN": "इस मैसेज में कोई स्कैम संकेत नहीं मिला।"}

def predict(text):
    v = VEC.transform([_prep(text)]); p = float(LR.predict_proba(v)[0][1])
    names = VEC.get_feature_names_out(); row = v.tocoo()
    contrib = sorted(((LR.coef_[0][j] * val, names[j]) for j, val in zip(row.col, row.data)), reverse=True)
    words = ["link" if w == "urltoken" else w for c, w in contrib if c > 0.1 and " " not in w][:5]
    level = "RED" if p >= .7 else "YELLOW" if p >= .4 else "GREEN"
    return {"probability": round(p * 100), "level": level, "words": words,
            "has_link": bool(URL.search(text)), "explanation_hi": HI[level]}
