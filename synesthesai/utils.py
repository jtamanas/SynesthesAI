# base func definitions
def dict_to_string(d):
    """
    Converts a dictionary into a pretty string.

    Args:
        d (dict): A dictionary with string keys and values that are numbers or lists.

    Returns:
        str: A pretty string representation of the dictionary.
    """
    lines = []
    for key, value in d.items():
        if isinstance(value, list):
            value_str = "[" + ", ".join(str(v) for v in value) + "]"
        else:
            value_str = str(value)
        lines.append(f"{key}: {value_str}")
    return "\n".join(lines)


def deep_merge_dicts(dict1, dict2):
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge_dicts(dict1[key], value)
        else:
            merged[key] = value
    return merged


def pull_keys_to_top_level(data, keys):
    """Pull keys from nested dictionaries to the top level."""
    to_move = {}

    def traverse_dict(d):
        for key, value in list(d.items()):  # We use list to avoid RuntimeError due to size change during iteration
            if key in keys:
                to_move[key] = d.pop(key)
            elif isinstance(value, dict):
                traverse_dict(value)
                
    traverse_dict(data)
    data.update(to_move)
