# Proof Blueprint

## Statement Spine

### T1：严格活动分支局部收敛

若 KKT 点 (w^\star\) 的投影输入 (q^\star\) 无零坐标，令 (D_\star\) 为其符号分支。
若 (T_{D_\star}(\tau)\) 为 Schur 稳定矩阵，则存在显式 Lyapunov 椭球，真实正部投影
从该椭球内任一点出发均保持 (D_\star\) 并线性收敛到 (w^\star\)。

### T2：共同 Lyapunov 步长区间

若存在 (H\succ0\) 使区间端点 (\tau_-,\tau_+\) 均满足

\[
H-T_{D_\star}(\tau_\pm)^\top H T_{D_\star}(\tau_\pm)\succ0,
\]

则因 (T_{D_\star}(\tau)\) 关于 (\tau\) 仿射，残差矩阵关于 (\tau\) Loewner-凹，
故整个区间均严格下降，并共享一个投影安全椭球。

### T3：有限前缀捕获

若某个初值在前 (K\) 步的真实投影符号均严格，并且第 (K\) 步进入 T1/T2 的不变椭球，
则其后全序列收敛。若这些有限不等式在一个初值或参数区间上一致严格，则结论对该邻域或
区间统一成立。

## 证明义务

1. 从原始 ADMM 推导 (T_D(\tau),a_D(\tau),C,d\)，检查索引和乘子符号；
2. 证明 T1 中椭球完全位于真实分支并正向不变；
3. 证明 T2 的矩阵凹性与端点充分性；
4. 对见证区间逐步认证投影符号与最终椭球进入；
5. 推导 `01` 分支精确特征多项式并认证稳定边界夹逼；
6. 分离局部稳定边界、有限前缀捕获边界和任意初值全局结论。

## 当前状态

`accepted_by_internal_verifier_style_review`。T1--T3、实例区间和稳定边界均已由
`outputs/tau_relaxation_theory_2026-07-16/results/certificate.json` 的精确有理证书关闭；
验收与 provenance 边界见本目录的 `acceptance_gate.md`。
