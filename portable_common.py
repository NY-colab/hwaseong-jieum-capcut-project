"""Shared, dependency-free CapCut transfer functions (Windows, Python 3.10+)."""
import hashlib
import json
import re
from pathlib import Path

PLACEHOLDER = '##_draftpath_placeholder_PORTABLE_##'

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def write(p, value):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

def digest(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def norm(s):
    return re.sub('/+', '/', str(s).replace('\\', '/')).rstrip('/').casefold()

def path_string(s):
    return bool(re.match(r'^(?:[A-Za-z]:[/\\]|\\\\|##_draftpath_placeholder_)', s))

def transform(value, fn):
    if isinstance(value, dict):
        return {k: transform(v, fn) for k, v in value.items()}
    if isinstance(value, list):
        return [transform(v, fn) for v in value]
    if isinstance(value, str):
        if path_string(value):
            return fn(value)
        if value.lstrip().startswith(('{', '[')):
            try:
                nested = json.loads(value)
            except ValueError:
                return value
            changed = transform(nested, fn)
            if changed != nested:
                return json.dumps(changed, ensure_ascii=False, separators=(',', ':'))
    return value

def paths(value):
    result = []
    transform(value, lambda s: result.append(s) or s)
    return result

def relative_placeholder(s):
    match = re.match(r'^##_draftpath_placeholder_[^#]+_##[/\\](.*)$', s)
    if not match:
        return None
    rel = Path(match[1].replace('\\', '/'))
    if rel.is_absolute() or '..' in rel.parts or ':' in str(rel):
        raise ValueError('Unsafe placeholder path')
    return rel

def clean_identity(value):
    """Remove cloud/account linkage while keeping local editing settings."""
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            if 'cloud' in k.casefold() or k.casefold().startswith('pippit_'):
                result[k] = {} if isinstance(v,dict) else [] if isinstance(v,list) else False if isinstance(v, bool) else 0 if isinstance(v, (int, float)) else ''
            else:
                result[k] = clean_identity(v)
        return result
    if isinstance(value, list):
        return [clean_identity(v) for v in value]
    return value
