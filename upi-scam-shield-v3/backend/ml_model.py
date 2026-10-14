"""AI #1: Random Forest fraud model. Trained on SYNTHETIC (dummy) data at startup."""
import math, random
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

SCAM_WORDS = ["kyc","refund","lottery","reward","prize","block","support","helpdesk","cashback","verify"]
BRANDS = ["sbi","pnb","hdfc","icici","npci","rbi","paytm","bank"]
URGENT = ["abhi","urgent","turant","warna","block","immediately","jaldi"]
FEATURES = ["reports","scam_words","brand_in_id","digits","phone_like","valid_format","log_amount","urgent_msg","is_collect"]
INFO = {  # feature: (naam, Hindi explanation)
 "reports": ("Community reports", "इस आईडी पर लोगों ने स्कैम रिपोर्ट किया है"),
 "scam_words": ("Suspicious shabd", "आईडी में KYC, रिफंड या लॉटरी जैसे शब्द हैं"),
 "brand_in_id": ("Bank ka naam copy", "आईडी में बैंक का नाम इस्तेमाल हुआ है, जो नकली हो सकता है"),
 "digits": ("Zyada digits", "आईडी में बहुत ज़्यादा नंबर हैं"),
 "valid_format": ("Galat format", "आईडी का फ़ॉर्मेट गलत है"),
 "log_amount": ("Bada amount", "रकम बड़ी है"),
 "urgent_msg": ("Urgency", "मैसेज में जल्दबाज़ी या धमकी है"),
 "is_collect": ("Collect request", "यह कलेक्ट रिक्वेस्ट है, इसमें आपका पैसा कटेगा"),
}

def features(upi_id, amount=0, message="", reports=0, is_collect=False):
    uid = upi_id.lower().strip(); name = uid.split("@")[0]
    return [min(reports, 15), sum(w in name for w in SCAM_WORDS), int(any(b in name for b in BRANDS)),
            sum(c.isdigit() for c in name), int(name.isdigit() and len(name) == 10), int("@" in uid),
            math.log1p(max(amount, 0)), int(any(w in message.lower() for w in URGENT)), int(is_collect)]

def _synthetic(n=1500):
    rng = random.Random(42); X, y = [], []
    for _ in range(n):   # scam
        r = rng.random(); rep = 0 if r < .15 else rng.randint(1, 2) if r < .4 else rng.randint(3, 12)
        r = rng.random(); w = 1 if r < .45 else 2 if r < .6 else 0
        ph = rng.random() < .05
        X.append([rep, w, int(rng.random() < .35), 10 if ph else rng.choice([0,3,5,6,7,8]), int(ph),
                  int(rng.random() < .95), math.log1p(rng.lognormvariate(8, 1.1)),
                  int(rng.random() < .45), int(rng.random() < .3)]); y.append(1)
    for _ in range(n):   # legit
        r = rng.random(); rep = 0 if r < .88 else 1 if r < .97 else 2
        ph = rng.random() < .4
        X.append([rep, int(rng.random() < .06), int(rng.random() < .03), 10 if ph else rng.randint(0, 4), int(ph),
                  int(rng.random() < .99), math.log1p(rng.lognormvariate(6.2, 1.2)),
                  int(rng.random() < .02), int(rng.random() < .01)]); y.append(0)
    return np.array(X), np.array(y)

_X, _y = _synthetic()
_Xtr, _Xte, _ytr, _yte = train_test_split(_X, _y, test_size=.25, random_state=1)
MODEL = RandomForestClassifier(n_estimators=120, max_depth=7, min_samples_leaf=5, random_state=42).fit(_Xtr, _ytr)
INFO_META = {"model": "Random Forest", "train_samples": len(_Xtr), "synthetic": True,
             "holdout_accuracy_synthetic": round(float(MODEL.score(_Xte, _yte)), 3),
             "note": "Dummy data par trained hai; ye accuracy real world ki nahi hai."}
IMP = dict(zip(FEATURES, MODEL.feature_importances_))

def predict(upi_id, amount=0, message="", reports=0, is_collect=False):
    f = features(upi_id, amount, message, reports, is_collect); d = dict(zip(FEATURES, f))
    p = float(MODEL.predict_proba(np.array(f).reshape(1, -1))[0][1])
    active = [k for k, on in [("reports", d["reports"] >= 1), ("scam_words", d["scam_words"] >= 1),
              ("brand_in_id", d["brand_in_id"] == 1), ("digits", d["digits"] >= 5 and not d["phone_like"]),
              ("valid_format", d["valid_format"] == 0), ("log_amount", d["log_amount"] >= math.log1p(10000)),
              ("urgent_msg", d["urgent_msg"] == 1), ("is_collect", d["is_collect"] == 1)] if on]
    active.sort(key=lambda k: -IMP[k])
    return {"ml_score": round(p * 100), "factors": [{"name": INFO[k][0], "hi": INFO[k][1]} for k in active[:3]]}

def explain_hi(level, factors):
    why = "; ".join(f["hi"] for f in factors)
    if level == "RED": return f"सावधान! {why}। पेमेंट मत कीजिए।" if why else "सावधान! यह आईडी जोखिम भरी लग रही है। पेमेंट मत कीजिए।"
    if level == "YELLOW": return f"थोड़ा रुकिए। {why}। पहले रिसीवर से कन्फर्म कर लीजिए।" if why else "थोड़ा रुकिए। पहले रिसीवर से कन्फर्म कर लीजिए।"
    return "कोई बड़ा खतरा नहीं मिला। फिर भी रिसीवर का नाम चेक कर लें।"
