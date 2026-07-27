from analyzer.language_detector import detect_language
from analyzer.core import analyze_function
from analyzer.classifier import classify
from utils.color import colorize
from analyzer.detectors import detect_weak_signals
from analyzer.callgraph import build_call_map, find_entry, dfs_paths
import json
def load_data():
    with open("data/functions.json") as f:
        return json.load(f)

def main():
    functions = load_data()

    lang = detect_language(functions)
    print(f"\n[+] Detected Language: {lang}\n")

    important_funcs = set()

    for func in functions:
        score, reasons = analyze_function(func, lang)
        level = classify(score)

        print(colorize(level, f"[{level}] {func['name']} (score: {score})"))

        for r in reasons:
            print(f"   → {r}")

        if level in ["HIGH", "MEDIUM"]:
            important_funcs.add(func["name"])

            notes = detect_weak_signals(func)
            if notes:
                print("   [Notes]")
                for n in notes:
                    print(f"      - {n}")

        print()

    print("\n[+] Call Chains:\n")

    call_map = build_call_map(functions)
    entry = find_entry(functions)
    chains = dfs_paths(call_map, entry)

    def format_chain(chain): # Zincirde  HİGH seviyesindeki fonksiyonlar highlighted gözüksün diye [] koydum
        out = []
        for f in chain:
            if f in important_funcs:
                out.append(f"[{f}]")  # highlight
            else:
                out.append(f)
        return " → ".join(out)

    for chain in chains:
        print(format_chain(chain))


if __name__ == "__main__":
    main()
