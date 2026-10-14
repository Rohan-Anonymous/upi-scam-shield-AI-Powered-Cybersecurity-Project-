"""FastAPI app v3: rules + ML hybrid, SMS detector, Hindi explanation."""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from risk_engine import check_upi, ADVICE
import database as db, ml_model, sms_detector

app = FastAPI(title="UPI Scam Shield v3")
db.init_db(); db.seed_demo()

class CheckReq(BaseModel):
    upi_id: str
    amount: float = 0
    message: str = ""
    is_collect: bool = False

class ReportReq(BaseModel):
    upi_id: str
    reason: str = ""
    reporter: str = "anon"

class SmsReq(BaseModel):
    text: str

@app.post("/check")
def check(req: CheckReq):
    n = db.count_reports(req.upi_id)
    rule = check_upi(req.upi_id, req.amount, req.message, n, req.is_collect)
    ai = ml_model.predict(req.upi_id, req.amount, req.message, n, req.is_collect)
    score = min(100, round(0.6 * rule["score"] + 0.4 * ai["ml_score"]))   # hybrid
    level = "RED" if score >= 60 else "YELLOW" if score >= 30 else "GREEN"
    db.log_check(level, req.amount)
    return {"score": score, "level": level, "reasons": rule["reasons"], "advice": ADVICE[level],
            "rule_score": rule["score"], "ml_score": ai["ml_score"], "ml_factors": ai["factors"],
            "explanation_hi": ml_model.explain_hi(level, ai["factors"])}

@app.post("/sms")
def sms(req: SmsReq):
    r = sms_detector.predict(req.text[:1000])
    db.log_check(r["level"], 0)
    return r

@app.post("/report")
def report(req: ReportReq):
    ok = db.add_report(req.upi_id, req.reason or "Scam report by user", req.reporter)
    return {"status": "ok" if ok else "duplicate", "total_reports": db.count_reports(req.upi_id)}

@app.get("/alerts")
def alerts(): return db.latest_reports(12)

@app.get("/stats")
def stats(): return db.stats()

@app.get("/ai/info")
def ai_info(): return {"fraud_model": ml_model.INFO_META, "sms_model": sms_detector.INFO_META}

app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend"), html=True), name="frontend")
