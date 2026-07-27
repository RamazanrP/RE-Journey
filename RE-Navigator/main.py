from analyzer.language_detector import detect_language
from analyzer.core import analyze_function
from analyzer.classifier import classify
from utils.color import colorize
import json

def load_data():
    with open("data.json") as f:
        return json.load(f)

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

        print()

if __name__ == "__main__":
    main()
