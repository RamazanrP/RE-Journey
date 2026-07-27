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

def detect_memory_risk(func):
    score = 0
    reasons = []

    dangerous = ["strcpy", "gets", "scanf", "memcpy", "strcat"]

    for call in func["calls"]:
        if call in dangerous:
            score += 3
            reasons.append(f"Uses {call} → potential memory vulnerability")

    return score, reasons

def detect_centrality(func):
    score = 0
    reasons = []

    if func["xrefs"] > 5:
        score += 4
        reasons.append("High number of cross-references → central function") # Daha çok çağrılıyorsa daha kritik de olabilir Junk Code da olabilir. Umuyoruz ki core func. çıksın :)

    if len(func["callers"]) > 3:
        score += 2
        reasons.append("Called from multiple locations → shared logic")

    return score, reasons

def detect_complexity(func):
    score = 0
    reasons = []
    # Yine aynı şekilde umuyoruz ki Core Logic sebebiyle kompleks bir fonksiyon yazışmıştır
    if func["loops"]:
        score += 2
        reasons.append("Contains loops → possible data processing")

    if func["conditions"] > 8:
        score += 3
        reasons.append("High branching → complex logic")

    if func["size"] > 150:
        score += 2
        reasons.append("Large function → likely core logic")

    return score, reasons

def detect_sensitive_apis(func):
    score = 0
    reasons = []

    sensitive = ["CreateFile", "ReadFile", "WriteFile","send", "recv","Crypt", "AES", "SHA"]

    for imp in func["imports"]:
        for s in sensitive:
            if s.lower() in imp.lower():
                score += 3
                reasons.append(f"Uses sensitive API '{imp}'")

    return score, reasons
