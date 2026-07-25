# Active-Set Effective Recurrence

状态：`proof_attempt` + `numerical_screen`

本 note 记录 WO-5 当前使用的 fixed-active-set 局部递推。它是反例路线的结构化入口，但还不是严格反例。

## 适用模型

当前实验模块使用无集合约束的凸二次 slack-variable 三块 ADMM：

\[
\min\left\{\frac12 x^\top Q_1x+\frac12 y^\top Q_2y
\mid Ax+By+z=b,\ z\ge0\right\}.
\]

乘子符号沿用 `notes/z_projection_identity.md`：

\[
\lambda^{k+1}=\lambda^k-\beta(Ax^{k+1}+By^{k+1}+z^{k+1}-b).
\]

## 有效状态

direct update 的下一步不使用旧的 \(x^k\)。因此 fixed-active-set 局部动力系统可以写在

\[
v^k=(y^k,z^k,\lambda^k)
\]

上，而不是 full bookkeeping state

\[
s^k=(x^k,y^k,z^k,\lambda^k).
\]

代码入口：

- `pack_effective_state`
- `build_effective_fixed_active_set_map`
- `spectral_diagnostics`

## 固定 active mask

令 \(D=\operatorname{diag}(d)\)，其中 \(d_i=1\) 表示第 \(i\) 个 slack 坐标在当前 active region 中满足 \(q_i>0\)，投影线性化为

\[
z^{k+1}=Dq^{k+1}.
\]

在固定 \(D\) 下，令

\[
H_x=Q_1+\beta A^\top A,\quad
H_y=Q_2+\beta B^\top B.
\]

则一步更新为

\[
x^{k+1}=H_x^{-1}\left(A^\top\lambda^k-\beta A^\top(By^k+z^k-b)\right),
\]

\[
y^{k+1}=H_y^{-1}\left(B^\top\lambda^k-\beta B^\top(Ax^{k+1}+z^k-b)\right),
\]

\[
q^{k+1}=b-Ax^{k+1}-By^{k+1}+\lambda^k/\beta,
\]

\[
z^{k+1}=Dq^{k+1},
\]

\[
\lambda^{k+1}=\lambda^k-\beta(Ax^{k+1}+By^{k+1}+z^{k+1}-b).
\]

因此存在仿射映射

\[
v^{k+1}=T_Dv^k+c_D.
\]

`src/admm_identity/slack_projection.py` 当前通过基向量探测构造 \(T_D,c_D\)。这避免了有限差分 Jacobian，但还没有把矩阵块公式完全手写展开。

矩阵块展开见 `notes/active_set_reduced_theory.md`。

## 谱诊断解释

当前搜索报告同时记录：

- `full_state_spectral_radius`：对 \(s=(x,y,z,\lambda)\) 的 full map；
- `effective_spectral_radius`：对 \(v=(y,z,\lambda)\) 的 effective map；
- `effective_expanding_count`：满足 \(|\eta|>1+10^{-6}\) 的特征值数量；
- `effective_near_unit_count`：接近单位圆的中性特征值数量。

本轮 2D/3D structured all-mask screens 没有发现 `effective_expanding_count > 0` 的 active-region-consistent candidate。

## 仍缺的 proof-grade 步骤

要把某个 candidate 升级为严格反例，仍需：

1. 找到 \(\rho(T_D)>1\) 且 `stay_consistent = true` 的候选；
2. 选取 unstable eigenvector 方向的初值；
3. 将有限步 stay check 升级为 active-region invariant inequalities；
4. 证明子问题良定，且真实 projected ADMM 轨道与 fixed-active recurrence 保持一致。
