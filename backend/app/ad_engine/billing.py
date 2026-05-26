"""广告计费模块

实现CPC和CPM两种计费方式的扣费金额计算，
CPC采用GSP（广义第二价格）机制确保广告主利益。
"""


def calculate_cpc_charge(current_pctr: float, next_ecpm: float) -> float:
    """计算CPC广告的点击扣费金额

    采用GSP（广义第二价格）拍卖机制，扣费 = 下一位eCPM / 当前预估点击率 / 1000 + 0.01。
    保证广告主只需支付略高于下一名的费用。

    Args:
        current_pctr: 当前广告的预估点击率
        next_ecpm: 下一位广告的eCPM

    Returns:
        float: 点击扣费金额，最低0.01元
    """
    # 预估点击率为0时，收取最低费用
    if current_pctr <= 0:
        return 0.01
    # GSP计算：下一名eCPM除以当前点击率，加最低扣费保底
    charge = next_ecpm / current_pctr / 1000 + 0.01
    return round(charge, 4)


def calculate_cpm_charge(bid_amount: float) -> float:
    """计算CPM广告的单次展示扣费金额

    CPM为千次展示费用，单次展示扣费 = 出价 / 1000。

    Args:
        bid_amount: CPM出价金额（每千次展示价格）

    Returns:
        float: 单次展示扣费金额
    """
    return round(bid_amount / 1000, 4)
