def classify(score):
    if score >= 12:
        return "HIGH"
    elif score >= 6:
        return "MEDIUM"
    else:
        return "LOW"
