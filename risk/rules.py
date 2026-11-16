"""Transparent risk rules. Output = warning signals with evidence, never proof."""
import re
from dataclasses import dataclass


@dataclass
class Rule:
    name: str
    pattern: str
    severity: str          # high | medium | low
    explanation: str

    def __post_init__(self):
        self.rx = re.compile(self.pattern, re.IGNORECASE)


TEXT_RULES = [
    Rule("asks_for_money",
         r"\b(registration|security|training|processing|application|joining|kit|refundable)\s+(fee|deposit|charges?)\b"
         r"|\bpay\s+(a|an|the|for)\b[^.]{0,30}\b(fee|kit|deposit)\b",
         "medium", "Posting mentions a payment or fee the applicant must make."),
    Rule("sensitive_documents",
         r"\b(your|their)\s+bank\s+(account|details)\b|\bssn\b|social\s+security\s+number|passport\s+copy|\baadhaar\b|credit\s+card\s+(number|details)",
         "medium", "Posting asks for sensitive documents or financial details."),
    Rule("chat_app_contact", r"\bwhatsapp\b|\btelegram\b",
         "low", "Contact through a chat app instead of a company channel."),
    Rule("unrealistic_earnings",
         r"\b(earn|make)\s+(up\s+to\s+)?[$₹£]?\s?\d[\d,]*\s*(per|a|/)\s*(day|week|hour)\b"
         r"|\bguaranteed\s+(income|salary|earnings|pay)\b|\bunlimited\s+(income|earning)",
         "medium", "Promises unusually high or guaranteed earnings."),
    Rule("scam_job_type",
         r"\bdata\s+entry\s+(from|at)\s+home\b|\bpayment\s+processing\b|\breship|\bmystery\s+shopper|\bpackage\s+forwarding",
         "low", "Job type often used in scams."),
    Rule("no_experience_big_pay",
         r"\bno\s+experience\s+(needed|required|necessary)\b",
         "low", "Says no experience is needed (common in both real and fake postings)."),
    Rule("pressure",
         r"\bapply\s+immediately\b|\blimited\s+(seats|positions|openings)\b|\burgent(ly)?\s+hiring\b|\bimmediate\s+joining\b",
         "low", "Uses pressure or urgency."),
]


def _snippet(text: str, m: re.Match, pad: int = 40) -> str:
    return "…" + text[max(0, m.start() - pad): m.end() + pad].strip() + "…"


def run_rules(search_text: str, company_profile: str = "", has_email_token: int = 0,
              has_url_token: int = 0) -> list:
    signals = []
    for r in TEXT_RULES:
        m = r.rx.search(search_text or "")
        if m:
            signals.append({"name": r.name, "severity": r.severity, "evidence": _snippet(search_text, m)})
    if len((company_profile or "").split()) < 10:
        signals.append({"name": "vague_company", "severity": "low",
                        "evidence": "company profile is empty or very short"})
    if has_email_token and not has_url_token:
        signals.append({"name": "email_but_no_website", "severity": "low",
                        "evidence": "contact given by email but no website link"})
    return signals