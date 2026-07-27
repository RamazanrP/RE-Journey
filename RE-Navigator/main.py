from analyzer.language_detector import detect_language
from analyzer.core import analyze_function
from analyzer.classifier import classify
from utils.color import colorize
from analyzer.detectors import detect_weak_signals
from analyzer.callgraph import build_call_map, find_entry, dfs_paths
import json

def main():
    functions = load_data()

    lang = detect_language(functions)
    print(f"\n[+] Detected Language: {lang}\n")

    for func in functions:
        score, reasons = analyze_function(func, lang)
        level = classify(score)

        print(colorize(level, f"[{level}] {func['name']} (score: {score})"))

        for r in reasons:
            print(f"   → {r}")

        if level in ["HIGH", "MEDIUM"]: # Spam gibi gözükmemesi için sadeec HİGH ve Medium'da notlar gösterilsin istedim
            notes = detect_weak_signals(func)

            if notes:
                print("   [Notes]")
                for n in notes:
                    print(f"      - {n}")

            print("\n[+] Call Chains:\n")
            call_map = build_call_map(functions)
            entry = find_entry(functions)

            chains = dfs_paths(call_map, entry)

            for chain in chains:
                print(" → ".join(chain))

        print()

if __name__ == "__main__":
    main()
