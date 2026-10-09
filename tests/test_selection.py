from __future__ import annotations
import pytest
import random

from libs.mastery_domain.models import Item, ItemParameters
from libs.mastery_domain.selection import select_next_item, SelectionError

def item(item_id, content_area, a=1.0, b=0.0):
    return Item(
        item_id=item_id,
        content_area=content_area,
        skills=[],
        parameters=ItemParameters(item_id, a=a, b=b, c=0.25)
    )

def test_excludes_already_administered():
    bank = [item('1', 'fundamentals'), item('2', 'fundamentals')]
    selected = select_next_item(
        theta=0.0,
        bank=bank,
        administered_ids={'1'},
        exposure_caps={},
        content_shares={},
        current_content_counts={'fundamentals': 0},
        target_shares={'fundamentals': 1.0}
    )
    assert selected.item_id == '2'

def test_hard_exposure_cap():
    bank = [item('1', 'fundamentals', a=2.0), item('2', 'fundamentals', a=1.0)]
    selected = select_next_item(
        theta=0.0,
        bank=bank,
        administered_ids=set(),
        exposure_caps={'1': 1.0}, # item 1 is at cap
        content_shares={},
        current_content_counts={'fundamentals': 0},
        target_shares={'fundamentals': 1.0}
    )
    assert selected.item_id == '2'

def test_maximum_information_selection():
    # Item 1 has higher discrimination and matches theta=0.0 perfectly
    bank = [item('1', 'fundamentals', a=2.0, b=0.0), item('2', 'fundamentals', a=1.0, b=0.0)]
    rng = random.Random(42)
    selected = select_next_item(
        theta=0.0,
        bank=bank,
        administered_ids=set(),
        exposure_caps={},
        content_shares={},
        current_content_counts={'fundamentals': 0},
        target_shares={'fundamentals': 1.0},
        top_k=1, # force max info
        rng=rng
    )
    assert selected.item_id == '1'

def test_content_balancing():
    bank = [
        item('1', 'fundamentals'),
        item('2', 'application'),
    ]
    # If application has 0 out of 1 and target is 1.0, it should be selected
    selected = select_next_item(
        theta=0.0,
        bank=bank,
        administered_ids={'3'},
        exposure_caps={},
        content_shares={},
        current_content_counts={'fundamentals': 1, 'application': 0},
        target_shares={'fundamentals': 0.0, 'application': 1.0}
    )
    assert selected.item_id == '2'

def test_loud_failure_when_content_constraints_cannot_be_met():
    bank = [item('1', 'fundamentals')]
    with pytest.raises(SelectionError, match='Cannot meet content constraints with remaining items'):
        select_next_item(
            theta=0.0,
            bank=bank,
            administered_ids=set(),
            exposure_caps={},
            content_shares={},
            current_content_counts={'fundamentals': 0},
            target_shares={'application': 1.0} # we need application, but only fundamentals in bank
        )

def test_exclusion_of_items_without_active_calibration():
    # item 1 has no parameters
    item1 = Item('1', 'fundamentals', [], None)
    item2 = item('2', 'fundamentals')
    bank = [item1, item2]
    selected = select_next_item(
        theta=0.0,
        bank=bank,
        administered_ids=set(),
        exposure_caps={},
        content_shares={},
        current_content_counts={'fundamentals': 0},
        target_shares={'fundamentals': 1.0}
    )
    assert selected.item_id == '2'
