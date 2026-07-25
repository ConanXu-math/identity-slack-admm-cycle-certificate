# 非恒定周期 Margin 优化

状态：numerical_screen；目标直接是 canonical itinerary strict margin，不是谱半径。

- canonical words: 15
- best margin: 2.7755575615628914e-17
- positive candidates: 0

## Top Records

- word [[0, 1], [1, 1]]: margin 2.7755575615628914e-17
- word [[0, 1], [0, 1], [1, 1]]: margin 3.469446951953614e-18
- word [[0, 1], [1, 1], [1, 1]]: margin 0.0
- word [[0, 0], [0, 0], [0, 1]]: margin -1.2759506669423716e-10
- word [[0, 0], [0, 1], [0, 1]]: margin -6.421894773660057e-09
- word [[0, 0], [0, 1]]: margin -3.813992692384483e-07
- word [[0, 0], [0, 0], [1, 1]]: margin -0.0032910789286727093
- word [[0, 0], [0, 1], [1, 0]]: margin -0.003299540318959213
- word [[0, 0], [1, 1]]: margin -0.0033020330101111873
- word [[0, 1], [1, 0]]: margin -0.0033080666764422474

## 边界

- 正 margin 只能进入有理化与 exact checker，不能直接称为反例。
- 非正结果只是有限预算 failure map，不能证明不存在周期轨道。
