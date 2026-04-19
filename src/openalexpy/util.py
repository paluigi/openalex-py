from __future__ import annotations


def invert_abstract(inv_index: dict[str, list[int]] | None) -> str | None:
    if inv_index is None:
        return None
    if not inv_index:
        return ""
    length = max(max(pos) for pos in inv_index.values()) + 1
    words: list[str] = [""] * length
    for word, positions in inv_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words)
