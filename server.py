from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI(title="【entity-Walmart¦canonical_name=Walmart】 EDI Fixer for Muse")

PAYPAL_LINK = "https://paypal.me/spatnam91/49USD"
UPI_ID = "8096712129-2@ybl"
UPI_LINK = f"upi://pay?pa={UPI_ID}&pn=【entity-Walmart¦canonical_name=Walmart】%20EDI%20Fixer&am=4099&cu=INR"

class EDIRequest(BaseModel):
    error_message: str = ""
    edi_snippet: str = ""
    cogs: float = 0
    ordered_qty: int = 0
    shipped_qty: int = 0

@app.get("/")
def home():
    return {
        "status": "【entity-Walmart¦canonical_name=Walmart】 EDI Fixer for Muse is LIVE ✅",
        "paypal": PAYPAL_LINK,
        "upi": UPI_ID,
        "tools": ["/mcp/diagnose_edi_error", "/mcp/calculate_otif", "/mcp/generate_warp_dispute", "/pay"],
        "how_to_use": "POST your 824 error to /mcp/diagnose_edi_error"
    }

@app.get("/pay")
def pay():
    return {
        "pro": "$49/month unlimited",
        "usa": PAYPAL_LINK,
        "india_upi_id": UPI_ID,
        "india_upi_link": UPI_LINK
    }

@app.post("/mcp/diagnose_edi_error")
def diagnose(req: EDIRequest):
    msg = req.error_message.upper()
    if "N1" in msg and "STORE" in msg:
        field = "N1 Store Number"
        fix = "Pad to 4 digits: Change 1234 -> 01234 in N104 segment"
    elif "REF" in msg or "UPC" in msg or "GTIN" in msg:
        field = "REF UPC/GTIN Mismatch"
        fix = "GTIN mismatch vs Retail Link. Update ERP mapping to Walmart expected GTIN"
    elif "SSCC" in msg:
        field = "SSCC-18 Check Digit"
        fix = "SSCC check digit failed. Recalculate Modulo 10 using GS1 calculator"
    elif "824" in msg or "864" in msg:
        field = "EDI 824/864 Alert"
        fix = "Walmart error alert - patch mapping within 1 hour, enable SMS alert"
    else:
        field = "General 5010 Mapping"
        fix = "Check Walmart 5010 spec, ISA version, missing segment"
    
    return {"field": field, "fine_risk": "$200 SQEP + 3% OTIF", "fix": fix, "pay_to_unlock": PAYPAL_LINK}

@app.post("/mcp/calculate_otif")
def calc(req: EDIRequest):
    fine = req.cogs * 0.03
    if req.shipped_qty < req.ordered_qty:
        return {"status": "FAIL Shorted", "fine": fine, "fix": f"DO NOT SHIP. Ordered {req.ordered_qty}, have {req.shipped_qty}. Fine ${fine}"}
    return {"status": "PASS if on time", "fine_risk": fine, "fix": "Use Walmart Collect carrier or buffer 48h"}

@app.post("/mcp/generate_warp_dispute")
def warp(req: EDIRequest):
    return {"type": "Code 22", "fix": "Save POD+BOL signed by DC, file WARP dispute NOW", "template": f"PO {req.error_message} - POD shows {req.shipped_qty} shipped"}

# THIS IS CRITICAL FOR RENDER - DO NOT CHANGE
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
