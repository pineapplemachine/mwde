def normalize_path(path):
    if not path:
        return path
    path = path.replace("\\ ", " ")
    path = path.replace("\\'", "'")
    path = path.replace("\\\"", "\"")
    if path[0] == '"' and path[-1] == '"':
        path = path[1:-1]
    elif path[0] == "'" and path[-1] == "'":
        path = path[1:-1]
    return path
    