def build_call_map(functions):
    return {f["name"]: f.get("calls", []) for f in functions}


def find_entry(functions):
    # entry/main tespiti
    for f in functions:
        name = f["name"].lower()
        if "main" in name or "entry" in name or "start" in name:
            return f["name"]
    return functions[0]["name"]


def dfs_paths(call_map, start, path=None, visited=None):
    if path is None:
        path = [start]
    if visited is None:
        visited = set()

    visited.add(start)

    if not call_map.get(start):
        return [path]

    paths = []

    for callee in call_map[start]:
        if callee not in visited:
            new_paths = dfs_paths(call_map, callee, path + [callee], visited.copy())
            paths.extend(new_paths)

    return paths
