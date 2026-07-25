# 非恒定周期 Margin 优化

状态：numerical_screen；目标直接是 canonical itinerary strict margin，不是谱半径。

- canonical words: 105
- best margin: 0.0
- positive candidates: 0

## Top Records

- word [[0, 1], [0, 1], [0, 1], [0, 1], [1, 1]]: margin 0.0
- word [[0, 1], [0, 1], [0, 1], [1, 1], [1, 1]]: margin 0.0
- word [[0, 1], [0, 1], [1, 1], [0, 1], [1, 1]]: margin 0.0
- word [[0, 1], [0, 1], [1, 1], [1, 1], [1, 1]]: margin 0.0
- word [[0, 1], [1, 1], [0, 1], [1, 1], [1, 1]]: margin 0.0
- word [[0, 1], [1, 1], [1, 1], [1, 1], [1, 1]]: margin 0.0
- word [[0, 0], [0, 0], [0, 0], [0, 1], [0, 1]]: margin -2.560585007915783e-10
- word [[0, 0], [0, 0], [0, 1], [0, 0], [0, 1]]: margin -3.960948444237111e-10
- word [[0, 0], [0, 0], [0, 0], [0, 0], [0, 1]]: margin -1.0203054218366518e-09
- word [[0, 0], [0, 1], [0, 0], [0, 1], [0, 1]]: margin -2.387939499282471e-09

## 边界

- 正 margin 只能进入有理化与 exact checker，不能直接称为反例。
- 非正结果只是有限预算 failure map，不能证明不存在周期轨道。
