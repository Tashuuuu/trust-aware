from risk.rules import run_rules

def names(t, **kw): return {s["name"] for s in run_rules(t, "A long company profile " * 5, **kw)}

def test_fee_fires():            assert "asks_for_money" in names("You must pay a registration fee of 500")
def test_fee_not_fires():        assert "asks_for_money" not in names("Competitive salary and benefits")
def test_deposit_fires():        assert "asks_for_money" in names("A security deposit is required")
def test_bank_fires():           assert "sensitive_documents" in names("Send your bank details to us")
def test_bank_not_fires():       assert "sensitive_documents" not in names("Experience in banking sector")
def test_whatsapp_fires():       assert "chat_app_contact" in names("Contact us on WhatsApp")
def test_earn_fires():           assert "unrealistic_earnings" in names("Earn $500 per week from home")
def test_guaranteed_fires():     assert "unrealistic_earnings" in names("Guaranteed income for everyone")
def test_scam_type_fires():      assert "scam_job_type" in names("Mystery shopper wanted")
def test_pressure_fires():       assert "pressure" in names("Urgent hiring, apply immediately")
def test_clean_text_quiet():     assert names("Python developer with SQL and Git experience") == set()
def test_vague_company():
    assert "vague_company" in {s["name"] for s in run_rules("Python developer role", "")}
# add 8 more of your own to reach 20