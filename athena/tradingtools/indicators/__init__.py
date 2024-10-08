from athena.tradingtools.indicators.momentum.rsi import rsi, stochastic_rsi
from athena.tradingtools.indicators.trend.ichimoku import ichimoku
from athena.tradingtools.indicators.trend.macd import macd
from athena.tradingtools.indicators.trend.moving_average import (
    exponential_moving_average,
    simple_moving_average,
)

TECHNICAL_INDICATORS = {
    "exponential_moving_average": exponential_moving_average,
    "ichimoku": ichimoku,
    "macd": macd,
    "rsi": rsi,
    "simple_moving_average": simple_moving_average,
    "stochastic_rsi": stochastic_rsi,
}
