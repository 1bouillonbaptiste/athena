from athena.tradingtools.performance_metrics import (
    get_sharpe,
    get_calmar,
    get_sortino,
    get_max_drawdown,
    get_cagr,
)


def test_trades_to_wealth():
    wealth, time = test_trades_to_wealth([])  # noqa : F841 (unused)
    pass


def test_max_drawdown():
    maw_drawdown = get_max_drawdown([])  # noqa : F841 (unused)
    pass


def test_cagr():
    cagr = get_cagr([])  # noqa : F841 (unused)
    pass


def test_sharpe():
    sharpe = get_sharpe([])  # noqa : F841 (unused)
    pass


def test_calmar():
    calmar = get_calmar([])  # noqa : F841 (unused)
    pass


def test_sortino():
    sortino = get_sortino([])  # noqa : F841 (unused)
    pass
