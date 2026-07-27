def colorize(level, text):
    colors = {
        "HIGH": "\033[91m",
        "MEDIUM": "\033[93m",
        "LOW": "\033[92m"
    }
    reset = "\033[0m"
    return f"{colors[level]}{text}{reset}"
