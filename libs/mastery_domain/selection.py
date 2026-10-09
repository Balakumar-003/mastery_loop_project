from __future__ import annotations
import random
from collections import defaultdict

from .models import Item, IRTError
from .irt import information

class SelectionError(IRTError):
    pass

def select_next_item(
    theta: float,
    bank: list[Item],
    administered_ids: set[str],
    exposure_caps: dict[str, float],
    content_shares: dict[str, float],
    current_content_counts: dict[str, int],
    target_shares: dict[str, float] = None,
    top_k: int = 5,
    rng: random.Random = None
) -> Item:
    if target_shares is None:
        target_shares = {
            'fundamentals': 0.25,
            'application': 0.35,
            'analysis': 0.20,
            'synthesis': 0.20
        }
    if rng is None:
        rng = random.Random()
        
    # Filter 1: not already administered
    candidates = [i for i in bank if i.item_id not in administered_ids]
    
    # Filter 2: hard exposure cap
    candidates = [i for i in candidates if exposure_caps.get(i.item_id, 0.0) < 1.0]
    
    # Filter 3: must have active calibration (this is handled by passing only active items in `bank` but let's assume it has parameters)
    candidates = [i for i in candidates if i.parameters is not None]
    
    if not candidates:
        raise SelectionError('No eligible items remaining in the bank')
    
    # Determine the content area that is furthest behind its target share
    total_administered = sum(current_content_counts.values())
    
    def deficit(area: str) -> float:
        if total_administered == 0:
            return target_shares.get(area, 0.0)
        current_share = current_content_counts.get(area, 0) / (total_administered + 1)
        return target_shares.get(area, 0.0) - current_share

    # Sort areas by highest deficit
    areas_by_deficit = sorted(target_shares.keys(), key=deficit, reverse=True)
    
    selected_area_candidates = []
    for area in areas_by_deficit:
        area_candidates = [i for i in candidates if i.content_area == area]
        if area_candidates:
            selected_area_candidates = area_candidates
            break
            
    if not selected_area_candidates:
        raise SelectionError('Cannot meet content constraints with remaining items')
    
    # Score by maximum information at current theta
    scored = []
    for item in selected_area_candidates:
        info = information(theta, item.parameters)
        scored.append((info, item))
        
    # Sort descending by information
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Take top-k
    top_candidates = [x[1] for x in scored[:top_k]]
    
    # Random choice
    return rng.choice(top_candidates)
