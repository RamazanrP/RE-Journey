def detect_language(functions):
    cpp_score = 0

    for func in functions:
        name = func["name"]
        strings = " ".join(func["strings"]).lower()
        calls = " ".join(func["calls"]).lower()

        if name.startswith("_Z"):
            cpp_score += 3

        if "::" in name:
            cpp_score += 2

        if "std::" in strings:
            cpp_score += 2

        if "vtable" in strings or "__cxa" in calls:
            cpp_score += 3

        if "new" in calls or "delete" in calls:
            cpp_score += 2

    if cpp_score >= 5: # Yukarda scoring için biraz uzun tuttum evet ama C++ olduğu takdirde kesinlikle >5 olacaktır. Kısacası sorun yok 
        return "C++"
    else:
        return "C"
