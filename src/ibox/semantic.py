"""可选的本地语义检索：调本机 ollama 的 embeddings 接口（只用标准库 urllib）。

ollama 没装 / 没开时一切照常，只是近义说法的命中率低一些。
"""
import hashlib
import json
import math
import urllib.request

from ibox.env import config_dir

BASE = "http://localhost:11434"
EMBED_DEFAULT = "nomic-embed-text"
EMBED_PREFERS = ("bge-m3",)  # 中文区分度明显更好，本机有就优先

_cache = {}


def _get(path, timeout=1.5):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return json.loads(r.read())


def available():
    if "up" not in _cache:
        try:
            _cache["models"] = [m.get("name", "") for m in _get("/api/tags").get("models", [])]
            _cache["up"] = True
        except Exception:
            _cache["up"] = False
    return _cache["up"]


def model():
    if not available():
        return None
    names = [n.split(":")[0] for n in _cache["models"]]
    for pref in EMBED_PREFERS:
        if pref in names:
            return pref
    return EMBED_DEFAULT


def _embed(text, is_query):
    # nomic 系列用 search_query / search_document 前缀对齐效果最好，其他模型无害
    prefix = "search_query: " if is_query else "search_document: "
    req = urllib.request.Request(
        BASE + "/api/embeddings",
        data=json.dumps({"model": model(), "prompt": prefix + text}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["embedding"]


def _cosine(a, b):
    if not a or not b or len(a) != len(b):
        return None
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else None


def _card_text(card):
    return " ".join([card.title, card.purpose] + card.aliases)


def similarities(cards, query):
    """返回 {card.id: 余弦相似度}。卡片向量按「内容 hash + 模型名」缓存，换模型自动重建。"""
    path = config_dir() / "vectors.json"
    try:
        cache = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}
    m = model()
    dirty = False
    qvec = _embed(query, is_query=True)
    out = {}
    for c in cards:
        text = _card_text(c)
        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        rec = cache.get(c.id)
        if not (rec and rec.get("hash") == h and rec.get("model") == m):
            rec = {"hash": h, "model": m, "vec": _embed(text, is_query=False)}
            cache[c.id] = rec
            dirty = True
        out[c.id] = _cosine(qvec, rec["vec"])
    if dirty:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(cache), encoding="utf-8")
        except OSError:
            pass
    return out
