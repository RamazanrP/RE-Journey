from analyzer.language_detector import detect_language
from analyzer.c_analyzer import analyze_c
from analyzer.cpp_analyzer import analyze_cpp
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

    if lang == "C++":
        results = analyze_cpp(functions)
    else:
        results = analyze_c(functions)

    for func, score, reasons in results:
        level = classify(score)

        print(colorize(level, f"[{level}] {func['name']} (score: {score})"))

        for r in reasons:
            print(f"   → {r}")

        print()

if __name__ == "__main__":
    main()
