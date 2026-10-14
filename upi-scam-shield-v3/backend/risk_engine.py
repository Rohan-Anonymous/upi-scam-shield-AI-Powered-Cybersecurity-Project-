"""Module 1: Risk Engine - 4 layers, explainable score (0-100)."""
import re

REPORTS = {"sbi-kyc-update@okaxis": 6, "refund.help123@ybl": 3}   # fallback demo data
SUSPICIOUS_WORDS = ["kyc", "refund", "lottery", "reward", "prize", "block", "support", "helpdesk", "cashback"]
URGENT_WORDS = ["abhi", "urgent", "turant", "warna", "block", "immediately", "jaldi"]
ADVICE = {
    "GREEN": "Koi bada khatra nahi mila. Phir bhi receiver ka naam bank app me ek baar check kar lein.",
    "YELLOW": "Thoda ruk jaaiye. Receiver ko call karke confirm karein, phir pay karein.",
    "RED": "Payment mat kijiye! Ye ID scam jaisi lag rahi hai.",
}

def check_upi(upi_id, amount=0, message="", reports=None, is_collect=False):
    score, reasons = 0, []
    upi_id = upi_id.lower().strip()

    # Layer 1: community reports
    if reports is None:
        reports = REPORTS.get(upi_id, 0)
    if reports >= 3:
        score += 50
        reasons.append(f"Is ID ko {reports} logon ne scam report kiya hai")
    elif reports > 0:
        score += 15
        reasons.append(f"Is ID par {reports} report aayi hai")

    # Layer 2: suspicious ID pattern
    name = upi_id.split("@")[0]
    if any(w in upi_id for w in SUSPICIOUS_WORDS):
        score += 25
        reasons.append("ID me suspicious shabd hain (kyc/refund/lottery jaise)")
    if len(re.findall(r"\d", name)) >= 5:
        score += 15
        reasons.append("ID me bahut zyada random numbers hain")
    if "@" not in upi_id:
        score += 20
        reasons.append("UPI ID ka format galat hai (@ missing)")

    # Layer 3: urgency in message
    if any(w in message.lower() for w in URGENT_WORDS):
        score += 25
        reasons.append("Message me urgency/dhamki wali language hai")

    # Layer 4: amount
    if amount >= 10000:
        score += 10
        reasons.append("Bada amount bheja ja raha hai")

    # Layer 5: UPI collect request (paisa katta hai, aata nahi)
    if is_collect:
        score += 30
        reasons.append("Ye 'collect request' hai: isme aapka paisa katega, aayega nahi")

    score = min(score, 100)
    level = "RED" if score >= 60 else "YELLOW" if score >= 30 else "GREEN"
    return {"score": score, "level": level, "reasons": reasons, "advice": ADVICE[level]}

if __name__ == "__main__":
    print(check_upi("sbi-kyc-update@okaxis", 5000, "Abhi pay karo warna account block"))
    print(check_upi("rohan@oksbi", 200))
