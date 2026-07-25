# Gate 外固定 QP Signed-PWA 定理独立复核

最终 verdict：`correct`，无剩余 blocker。

两条独立复核分别从原 ADMM 重推 signed recurrence，并审查连续 PWA 的跨 orthant 增量收缩、fixed-point/KKT 双向桥和时间索引。Gate 外有理数据也经独立复算：\(Q_2\succ0\)，旧 SG 的 \(a\)、\(b\) Gram residual 行列式均严格为负，而四个 signed 分支的 \((99/100)^2H-B_D^THB_D\) 全部 exact 正定。

因此该固定 QP 的直接三块 ADMM 对任意有限初值全局几何收敛。该结论只针对本卡给定的固定 Hessians 和零 rhs，不外推到一般模型。
