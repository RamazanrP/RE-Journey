from .detectors import (
    detect_auth_logic,
    detect_memory_risk,
    detect_centrality,
    detect_complexity,
    detect_sensitive_apis,
    detect_language_specific,
    detect_entry_points,
    detect_win_functions
)

def analyze_function(func, lang):
    total_score = 0
    all_reasons = []

    detectors = [
        detect_auth_logic,
        detect_memory_risk,
        detect_centrality,
        detect_complexity,
        detect_sensitive_apis,
        detect_language_specific,
        detect_win_functions,
    ]

    for detector in detectors:
        score, reasons = detector(func)
        total_score += score
        all_reasons.extend(reasons)

    return total_score, all_reasons
