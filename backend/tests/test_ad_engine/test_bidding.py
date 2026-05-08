from app.ad_engine.bidding import rank_ads_by_ecpm
from app.ad_engine.billing import calculate_cpc_charge, calculate_cpm_charge


def test_rank_ads_by_ecpm():
    ads = [
        {"id": 1, "bid_amount": 1.0, "bid_type": "CPC", "pctr": 0.05},
        {"id": 2, "bid_amount": 0.5, "bid_type": "CPC", "pctr": 0.20},
        {"id": 3, "bid_amount": 2.0, "bid_type": "CPM", "pctr": 0.01},
    ]
    ranked = rank_ads_by_ecpm(ads)
    assert ranked[0]["id"] == 2
    assert ranked[1]["id"] == 1
    assert ranked[2]["id"] == 3


def test_rank_empty():
    assert rank_ads_by_ecpm([]) == []


def test_cpc_charge():
    charge = calculate_cpc_charge(current_pctr=0.05, next_ecpm=40.0)
    assert abs(charge - 0.81) < 0.001


def test_cpm_charge():
    charge = calculate_cpm_charge(bid_amount=5.0)
    assert abs(charge - 0.005) < 0.0001
