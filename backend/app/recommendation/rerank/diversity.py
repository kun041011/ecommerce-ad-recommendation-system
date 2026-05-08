from typing import List, Dict


def mmr_rerank(items: List[dict], n: int = 10, lambda_param: float = 0.5) -> List[dict]:
    if not items:
        return []

    selected = [items[0]]
    remaining = items[1:]

    while len(selected) < n and remaining:
        best_score = -float("inf")
        best_idx = 0

        for i, item in enumerate(remaining):
            relevance = item.get("score", 0)
            max_sim = max(
                (1.0 if item.get("category") == s.get("category") else 0.0)
                for s in selected
            )
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i

        selected.append(remaining.pop(best_idx))

    return selected
