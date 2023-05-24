import tomllib
from tomllib import TOMLDecodeError
from difflib import SequenceMatcher
import re

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

def remove_default_attributes(dict1, dict2, keys_to_keep=[]):
    """If an attribute is not specified, drop it from the query"""
    # Create a new dictionary based on dict2
    new_dict = dict2.copy()
    
    # Iterate over the keys in dict1
    for key in dict1:
        # If the key exists in dict2 and its value is the same as in dict1,
        # and the key is not in the list of keys to keep
        if key in dict2 and dict1[key] == dict2[key] and key not in keys_to_keep:
            # Remove this key-value pair from the new dictionary
            del new_dict[key]
            
    return new_dict

    
def partial_load_toml(broken_toml_text):
    """
    Assume we received a toml that contains some broken bit in it. 
    Keep cutting out lines until we trim the broken piece
    """
    lines = broken_toml_text.split('\n')
    for i in range(len(lines), 0, -1):
        try:
            doc = tomllib.loads('\n'.join(lines[:i]))
            # Validate that all sections are complete
            for key in doc.keys():
                if doc[key] == {} or (isinstance(doc[key], list) and len(doc[key]) > 0 and doc[key][-1] == {}):
                    raise TOMLDecodeError("Incomplete section")
            print("WE DROPPED THE FOLLOWING FROM THE TOML")
            print('\n'.join(lines[i:]))
            return doc
        except TOMLDecodeError:
            continue
    raise TOMLDecodeError("TOML completely unsalvageable")


def approximately_the_same_str(a, b, cutoff=0.6):
    def _remove_parentheticals(t):
        return re.sub("[\(\[].*?[\)\]]", "", t)
    a = _remove_parentheticals(a)
    b = _remove_parentheticals(b)
    return (SequenceMatcher(a=a, b=b).ratio() >= cutoff)
