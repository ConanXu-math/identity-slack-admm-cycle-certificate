# 固定二维 QP 的 phase-dependent Lyapunov 收敛定理

状态：`theorem_with_exact_certificate`，已通过独立复核。本结论只针对下述固定 QP，不是一般三块 ADMM 收敛定理。

## 问题与算法

考虑

\[
\min \frac12x^\top(3I)x+\frac12y^\top
\begin{pmatrix}7&4\\4&3\end{pmatrix}y,
\qquad x+y+z=0,\quad z\geq0,
\]

并取直接三块 ADMM 的 \(\beta=1\) 及本仓库的乘子符号。令 canonical reduced state 为
\(r_k=(y^k,u^k)\in\mathbb R^4\)，mask 为 \(b_k\in\{00,01,10,11\}\)。完成一次
\(z\)-update 和乘子 update 后，逐坐标有 \(z^k\geq0\)、\(\lambda^k\leq0\) 和
\(z_i^k\lambda_i^k=0\)，故任意有限初值从 \(k=1\) 起均可使用该表示。

## 精确证书

取 \(\varepsilon=1/20\) 及

\[
\begin{aligned}
H_{00}&=\operatorname{diag}(1,1,6/5,11/10),\\
H_{01}&=\operatorname{diag}(1,2,6/5,11/5),\\
H_{10}&=\operatorname{diag}(21/10,1,21/10,11/10),\\
H_{11}&=\operatorname{diag}(5/2,23/10,19/10,2).
\end{aligned}
\]

`certify_phase_edge_rational.py` 从原始有理 QP 直接推导全部 reduced maps。对四个 masks 和
全部 16 条 source-target edges，它以所有主子式非负精确验证

\[
H_b-H_b^{\rm core}\succeq0,
\qquad
H_b-A_{bc}^\top H_cA_{bc}-\frac1{20}C_{bc}^\top C_{bc}\succeq0,
\]

其中 \(C_{bc}r_k=(\Delta\lambda^{k+1},\Delta y^{k+1},\Delta z^{k+1})\)。这不是浮点
screen；共精确检查 60 个 core 主子式和 240 个 edge 主子式。

## 定理与证明

**定理。** 对任意有限初值，上述直接三块 ADMM 迭代收敛到唯一 KKT 点
\((x,y,z,\lambda)=(0,0,0,0)\)。

从 \(k\geq1\) 起令 \(V_k=r_k^\top H_{b_k}r_k\)。edge 证书对任意 mask 切换给出

\[
V_k-V_{k+1}\geq\frac1{20}
\bigl(\|\Delta\lambda^{k+1}\|^2+\|\Delta y^{k+1}\|^2+
\|\Delta z^{k+1}\|^2\bigr).
\]

因此 \(V_k\) 下降且三类差分平方可和。四个 \(H_b\) 一致正定，故 \(r_k\) 有界；canonical
表示进一步给出 \(y^k,z^k,\lambda^k\) 有界，而显式 \(x\)-update 给出 \(x^k\) 有界。
于是存在聚点，且三类差分趋于零。由三步 update 的精确恒等式

\[
x^k+y^k+z^k=\lambda^{k-1}-\lambda^k,
\qquad
3x^k-\lambda^k=\Delta y^k+\Delta z^k,
\qquad
Q_2y^k-\lambda^k=\Delta z^k,
\]

原始残差及两个 stationarity gap 均趋于零；投影恒等式逐步给出精确互补性。故每个聚点
均满足 KKT 条件。

两个目标 Hessian 均正定，原问题的唯一最优点为 \(x=y=z=0\)，对应唯一乘子
\(\lambda=0\)。有界序列只有该聚点，因此整列收敛到零，目标值也收敛到零。

## 证据边界

- 精确机器证书：`outputs/breakthrough_attempts/stage10_phase_edge_certificate/phase_edge_rational.json`。
- 可读证书：`outputs/breakthrough_attempts/stage10_phase_edge_certificate/phase_edge_rational.md`。
- 该结果证明一个固定 QP 的任意真实 mask switching 收敛，不证明一般模型收敛。
- 独立复核结论为 `accept`；复核记录保存在
  `proof_reviews/fixed_qp_phase_lyapunov/final_verification.json`。
