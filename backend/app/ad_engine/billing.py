def calculate_cpc_charge(current_pctr: float, next_ecpm: float) -> float:
    if current_pctr <= 0:
        return 0.01
    charge = next_ecpm / current_pctr / 1000 + 0.01
    return round(charge, 4)


def calculate_cpm_charge(bid_amount: float) -> float:
    return round(bid_amount / 1000, 4)
