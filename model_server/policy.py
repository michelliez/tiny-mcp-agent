def policy_gate(question: str) -> dict:
    """Check whether a prompt is allowed before routing to tools or the model"""
    blocked_terms = {
        "patient name": "Requests patient-identifying informaion", 
        "names": "Requests patient-identifying informaion", 
        "mrn": "Requests medical record numbers", 
        "dob": "Requests patient-identifying informaion", 
        "date of birth": "Requests patient-identifying informaion", 
        "address": "Requests patient-identifying informaion", 
        "phone number": "Requests patient-identifying informaion", 
        "family members": "Requests patient-identifying informaion", 
        "relatives": "Requests patient-identifying informaion", 
        "which patient": "Asks for individual patient information", 
        "who was": "Asks for individual patient information", 
        "delete": "Requests a destructive database action", 
        "drop": "Requests a destructive database action", 
        "update": "Requests a destructive database action", 
        "insert": "Requests a destructive database action", 
        "ignore policy": "Tries to change rules", 
        "ignore permissions": "Tries to change rules"
    }
    q = question.lower()
    for term, reason in blocked_terms.items():
        if term in q:
            return{
                "allowed": False,
                "reason": reason,
                "matched_term": term,
            }
    return {
        "allowed": True,
        "reason": None,
        "matched_term": None 
    }
