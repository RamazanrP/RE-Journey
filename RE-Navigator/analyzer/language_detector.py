def detect_language_specific(func, lang):
    score = 0
    reasons = [] # Hangi dil olduğunu nedeniyle beraber yazıyorum ki ilerde refleks olsun

    name = func["name"]

    if lang == "C++":

        if "::" in name:
            score += 2
            reasons.append("C++ class/namespace function")

        if name.startswith("_Z"):
            score += 3
            reasons.append("Mangled symbol → compiled C++")

        if "ctor" in name.lower() or "dtor" in name.lower():
            score += 2
            reasons.append("Constructor/Destructor detected")

        if any("vtable" in s.lower() for s in func["strings"]):
            score += 3
            reasons.append("Virtual table usage → polymorphism")

    elif lang == "C":

        if "main" in name.lower():
            score += 2
            reasons.append("Main function → entry candidate")

        if func["conditions"] > 5 and func["loops"]:
            score += 2
            reasons.append("Procedural control-heavy logic")

    return score, reasons
