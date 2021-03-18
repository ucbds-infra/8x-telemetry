import hashlib
import base64

def hash_sha256(d):
    """Deterministically hashes input using SHA-256
    :d: Python dictionary or dict-like data structure
    :return: hash value
    """
    hasher = hashlib.sha256()
    hasher.update(repr(make_hashable(d)).encode())
    return base64.b64encode(hasher.digest()).decode()

def make_hashable(d):
    """ Recursively hash an object (and its contents)
    :d: Python dictionary or dict-like data structure
    :return: hashable data structure (tuple)
    """
    if isinstance(d, (tuple, list)):
        return tuple((make_hashable(e) for e in d))
    if isinstance(d, dict):
        return tuple(sorted((k, make_hashable(v)) for k,v in d.items()))
    if isinstance(d, (set, frozenset)):
        return tuple(sorted(make_hashable(e) for e in d))
    return d
