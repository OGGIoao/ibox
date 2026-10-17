"""检索：离线打分为主，可选 ollama 语义做温和加成。

铁律：强本地命中永远压住语义。语义分被相对归一到 [0, SEMANTIC_W]，而清晰的本地命中
在 30 分以上——不要改成纯语义排序：短中文在嵌入空间里区分度很差，曾把「kill」排到
「type」后面。
"""
import difflib

from ibox import semantic

SEMANTIC_W = 15.0
LEARNED_BOOST = 88


def _bigrams(s):
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) > 1 else {s}


def _overlap(a, b):
    """共享的二元组个数，封顶 3，避免长文本虚高。"""
    return min(len(_bigrams(a) & _bigrams(b)), 3) if a and b else 0


def _names(card):
    return [card.title.lower(), card.id] + [c.lower() for c in card.commands()]


def score(card, query, platform, learned=None):
    q = query.lower().strip()
    if not q:
        return 0
    best_name = 0
    for n in _names(card):
        if len(n) < 2:
            continue
        s = 200 if q == n else 55 if (q in n or n in q) else 0  # 精确命中命令名 / 标题 / id 是最强信号
        best_name = max(best_name, s + 25 * _overlap(q, n))
    s = best_name
    for a in card.aliases:
        s += 90 if q == a else 45 if (q in a or a in q) else 0
        s += 30 * _overlap(q, a)
    impl = card.impl(platform) or {}
    blob = " ".join([card.purpose] + [impl.get(f, "") for f in ("用法", "示例", "踩坑")]).lower()
    if q in blob:
        s += 18
    s += 10 * _overlap(q, blob)
    if learned and card.id in learned.get(q, {}):
        s += LEARNED_BOOST
    return s


def rank(cards, query, platform, learned=None):
    scored = [(score(c, query, platform, learned), c) for c in cards]
    scored = [x for x in scored if x[0] > 0]
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored]


def search(cards, query, platform, learned=None, use_semantic=True):
    """统一入口：ollama 可用就融合语义，否则（或出错）静默退回离线。"""
    if not use_semantic or not semantic.available():
        return rank(cards, query, platform, learned)
    try:
        sims = semantic.similarities(cards, query)
    except Exception:
        return rank(cards, query, platform, learned)
    vals = [v for v in sims.values() if v is not None]
    if not vals:
        return rank(cards, query, platform, learned)
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    scored = []
    for c in cards:
        s = score(c, query, platform, learned)
        sim = sims.get(c.id)
        if sim is not None:
            s += SEMANTIC_W * (sim - lo) / span
        if s > 0:
            scored.append((s, c))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored]


def known_words(cards):
    """标题、id、命令名、别名——这些不需要「学」。"""
    words = set()
    for c in cards:
        words.update(_names(c))
        words.update(c.aliases)
    return words


def suggest(cards, query, n=3):
    """没命中时给「你是不是想找」。"""
    pool = {}
    for c in cards:
        for w in _names(c) + c.aliases:
            pool.setdefault(w, c)
    out = []
    for w in difflib.get_close_matches(query.lower(), list(pool), n=n * 2, cutoff=0.35):
        if pool[w] not in out:
            out.append(pool[w])
    return out[:n]
