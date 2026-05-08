from typing import List, Set


def apply_business_rules(
    items: List[dict],
    purchased_ids: Set[int],
    shown_ids: Set[int],
) -> List[dict]:
    return [
        item for item in items
        if item["id"] not in purchased_ids and item["id"] not in shown_ids
    ]
