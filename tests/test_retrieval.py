from agents.researcher import lookup_company_contact, perform_research


def test_lookup_company_contact_curated():
    fk = lookup_company_contact("Flipkart")
    assert fk["email"] == "grievance.officer@flipkart.com"
    assert fk["verified"] is True

    indigo = lookup_company_contact("IndiGo Airlines")
    assert indigo["email"] == "nodal.officer@goindigo.in"
    assert indigo["verified"] is True

    hdfc = lookup_company_contact("HDFC Bank")
    assert hdfc["email"] == "pno@hdfcbank.com"
    assert hdfc["verified"] is True


def test_perform_research_ecommerce():
    res = perform_research("CASE-101", "ecommerce", "Flipkart")
    assert res.case_id == "CASE-101"
    assert res.company_deadline_days == 30
    assert "Consumer Protection" in res.rights_summary
    assert len(res.citations) >= 2


def test_perform_research_airline():
    res = perform_research("CASE-102", "airline", "IndiGo")
    assert res.case_id == "CASE-102"
    assert res.company_deadline_days == 7
    assert "DGCA CAR" in res.rights_summary
    assert any("DGCA" in c.title for c in res.citations)
