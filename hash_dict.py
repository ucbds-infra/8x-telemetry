import copy

def hash_dict(d):
    """ Recursively hash a dictionary and its contents
    :d: Python dictionary or dict-like data structure
    :return:
    """
    if not isinstance(d, dict):
        raise TypeError('Non dictionary-like data structure not supported')
    new_d = copy.deepcopy(d)
    for k, v in new_d.items():
        new_d[k] = hash_dict(v)
    return hash(tuple(frozenset(sorted(new_d.items()))))
