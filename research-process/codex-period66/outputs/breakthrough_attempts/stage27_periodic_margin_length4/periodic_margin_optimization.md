# 非恒定周期 Margin 优化

状态：numerical_screen；目标直接是 canonical itinerary strict margin，不是谱半径。

- canonical words: 37
- best margin: 0.0
- positive candidates: 0

## Top Records

- word [[0, 1], [0, 1], [0, 1], [1, 1]]: margin 0.0
- word [[0, 1], [0, 1], [1, 1], [1, 1]]: margin 0.0
- word [[0, 1], [1, 1], [0, 1], [1, 1]]: margin 0.0
- word [[0, 1], [1, 1], [1, 1], [1, 1]]: margin 0.0
- word [[0, 0], [0, 1], [0, 0], [0, 1]]: margin -3.884819549382357e-12
- word [[0, 0], [0, 0], [0, 1], [0, 1]]: margin -4.3861975541442405e-12
- word [[0, 0], [0, 1], [0, 1], [0, 1]]: margin -1.2795013312749681e-11
- word [[0, 0], [0, 0], [0, 0], [0, 1]]: margin -1.7470369838290534e-09
- word [[0, 0], [1, 1], [0, 1], [0, 1]]: margin -0.0025542504876052328
- word [[0, 0], [0, 1], [1, 0], [1, 0]]: margin -0.002711690289024564

## 边界

- 正 margin 只能进入有理化与 exact checker，不能直接称为反例。
- 非正结果只是有限预算 failure map，不能证明不存在周期轨道。
