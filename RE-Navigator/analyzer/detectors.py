def detect_auth_logic(func):
    score = 0
    reasons = []

    keywords = ["password", "pass", "auth", "login", "key", "token", "flag"] # Crackmes tecrübem arttıkça buraya gelip bu listeyi büyüteceğim

    for s in func["strings"]:
        for k in keywords:
            if k in s.lower():
                score += 4
                reasons.append(f"String contains '{k}' → likely authentication logic")

    if func["conditions"] > 5:
        score += 2
        reasons.append("High number of conditional branches → decision-heavy logic")

    return score, reasons
