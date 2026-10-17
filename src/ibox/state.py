"""用户状态：最近查看、查看次数（复习用）、学到的说法。存一个 JSON 文件。

所有读写都容错：状态丢了只影响「推荐」，绝不影响查命令本身。
"""
import json
import time

from ibox.env import config_dir

RECENT_MAX = 30


def _path():
    return config_dir() / "state.json"


def load():
    try:
        data = json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    data.setdefault("recent", [])
    data.setdefault("views", {})  # id -> {"count", "last"}
    data.setdefault("learned", {})  # 说法 -> {id: 次数}
    return data


def save(data):
    try:
        _path().parent.mkdir(parents=True, exist_ok=True)
        _path().write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError:
        pass


def record_view(card_id):
    data = load()
    data["recent"] = ([card_id] + [r for r in data["recent"] if r != card_id])[:RECENT_MAX]
    rec = data["views"].setdefault(card_id, {"count": 0, "last": 0})
    rec["count"] += 1
    rec["last"] = int(time.time())
    save(data)


def record_learn(query, card_id, known_words):
    """用户用一句「新说法」搜到并打开了某卡 → 记住，下次同样的说法直接命中。"""
    q = query.lower().strip()
    if len(q) < 2 or q in known_words:
        return
    data = load()
    hits = data["learned"].setdefault(q, {})
    hits[card_id] = hits.get(card_id, 0) + 1
    save(data)


def due_for_review(data, limit=5):
    """看过但看得少（<3 次）或一周没看的卡，越久越靠前。"""
    now = time.time()
    due = []
    for cid, rec in data["views"].items():
        age_days = (now - rec.get("last", 0)) / 86400
        cnt = rec.get("count", 0)
        if cnt and (cnt < 3 or age_days > 7):
            due.append((age_days + (3 - cnt) * 4, cid))
    due.sort(reverse=True)
    return [cid for _, cid in due[:limit]]
