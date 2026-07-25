# 乘子松弛的局部稳定区间与有限前缀捕获

状态：`exact_theorem_accepted_by_internal_verifier_style_review`

本笔记讨论同一 identity-slack 三块 ADMM，只把乘子更新改为

\[
\lambda^{k+1}=\lambda^k-\tau
\bigl(x^{k+1}+y^{k+1}+z^{k+1}-\bar b\bigr),
\qquad \tau>0.
\]

结论分成三层：一般的严格分支局部定理、共同 Lyapunov 区间定理，以及针对原 66 周期
初值的有限前缀捕获。它们不推出任意初值下的全局收敛。

## 1. 完整状态与参数化分支矩阵

令

\[
M=(Q_1+I)^{-1},\qquad N=(Q_2+I)^{-1},\qquad
w=(y,z,\lambda)\in\mathbb R^6.
\]

由原始四步更新直接消去 \(x^{+}\)，得到

\[
q^{+}=C_y y+C_z z+C_\lambda\lambda+d,
\]

其中

\[
C_y=(I-N)M,\qquad
C_z=N+(I-N)M,\qquad
C_\lambda=(I-N)(I-M),\qquad
d=C_\lambda\bar b.
\]

若本步投影的符号矩阵为 \(D=\operatorname{diag}(\mathbf1_{\{q_i^+>0\}})\)，则
\(z^+=Dq^+\)。又因为

\[
x^++y^++z^+-\bar b=\lambda-q^++z^+,
\]

乘子更新可写成

\[
\lambda^+=(1-\tau)\lambda+\tau(I-D)q^+.
\]

所以在固定符号区域内，原始 ADMM 恰好是

\[
w^+=T_D(\tau)w+a_D(\tau),
\]

其中

\[
T_D(\tau)=
\begin{pmatrix}
NM&-N(I-M)&N(I-M)\\
DC_y&DC_z&DC_\lambda\\
\tau(I-D)C_y&\tau(I-D)C_z&(1-\tau)I+\tau(I-D)C_\lambda
\end{pmatrix},
\]

\[
a_D(\tau)=
\begin{pmatrix}
N(I-M)\bar b\\ Dd\\ \tau(I-D)d
\end{pmatrix}.
\]

特别地，\(T_D(\tau)=A_D+\tau E_D\)、\(a_D(\tau)=c_D+\tau f_D\) 都关于
\(\tau\) 仿射，而 \(q^+=Cw+d\) 与 \(\tau\) 无关。证书程序在
\(D=00,01\) 和多个有理 \(\tau\) 上，从原始 \(x,y,z,\lambda\) 四步更新重新取六个基向量，
逐列验证了上述块矩阵。

## 2. 严格活动分支的局部收敛

**定理 1（严格分支局部收敛）.** 设 \(w^\star\) 是 KKT 状态，且
\(q^\star=Cw^\star+d\) 的每个坐标均非零。令 \(D_\star\) 为 \(q^\star\) 的符号矩阵。
若 \(T_{D_\star}(\tau)\) Schur 稳定，则存在一个显式椭球，使真实正部投影从该椭球内
任一点出发都保持分支 \(D_\star\)，并线性收敛到 \(w^\star\)。

**证明.** Schur 稳定性保证离散 Lyapunov 方程

\[
H-T_{D_\star}(\tau)^\top H T_{D_\star}(\tau)=I
\]

有唯一解 \(H\succ0\)。令 \(e=w-w^\star\)、\(V(e)=e^\top He\)，并把 \(C\) 的第
\(i\) 行记为 \(c_i\)。定义

\[
\alpha=min_i
\frac{|q_i^\star|^2}{c_iH^{-1}c_i^\top}>0.
\]

当 \(V(e)<\alpha\) 时，\(H\)-度量下的 Cauchy--Schwarz 不等式给出

\[
|c_i e|^2\le(c_iH^{-1}c_i^\top)V(e)<|q_i^\star|^2.
\]

故 \(q^+=q^\star+Ce\) 与 \(q^\star\) 逐坐标同号，真实投影采用 \(D_\star\)。在该分支上
\(e^+=T_{D_\star}(\tau)e\)，因而

\[
V(e^+)=V(e)-\|e\|_2^2<V(e).
\]

所以 \(\{V<\alpha\}\) 正向不变；再由 \(H\succ0\) 得到线性收敛。∎

## 3. 一个共同 Lyapunov 矩阵控制整段步长

**定理 2（共同 Lyapunov 区间）.** 固定严格 KKT 分支 \(D_\star\)，设
\(T(\tau)=A+\tau E\)。若存在 \(H\succ0\)，使

\[
F(\tau_-):=H-T(\tau_-)^\top HT(\tau_-)\succ0,
\qquad
F(\tau_+):=H-T(\tau_+)^\top HT(\tau_+)\succ0,
\]

则对每个 \(\tau\in[\tau_-,\tau_+]\)，均有 \(F(\tau)\succ0\)，并且定理 1 的同一
投影安全椭球适用于整个区间。

**证明.** 令 \(\tau=\theta\tau_-+(1-\theta)\tau_+\)。直接展开二次项得到

\[
F(\tau)-\theta F(\tau_-)-(1-\theta)F(\tau_+)
=\theta(1-\theta)(\tau_+-\tau_-)^2E^\top HE\succeq0.
\]

因此 \(F\) 关于 \(\tau\) 是 Loewner-凹的，端点正定推出整段正定。又因 \(C,q^\star,H\)
均不依赖 \(\tau\)，定理 1 中的 \(\alpha\) 可保持不变。

若还需要统一速率，令

\[
\delta_\pm=\frac1{\operatorname{tr}(F(\tau_\pm)^{-1})},qquad
\delta=\min\{\delta_-,\delta_+\}>0.
\]

则 \(F(\tau)\succeq\delta I\)，从而

\[
V(e^+)\le
\left(1-\frac{\delta}{\operatorname{tr}H}\right)V(e).
\]

∎

对严格 66 周期反例的 KKT 分支 \(D_\star=01\)，取原 \(\tau=1/2\) 证书中的有理矩阵
\(H\)。精确 Sylvester 判据验证

\[
F(49/100)\succ0,\qquad F(51/100)\succ0.
\]

故该实例在 \(0.49\le\tau\le0.51\) 上共享一个严格局部吸引椭球。证书给出的统一收缩因子
上界为

\[
0.99985082128383873917.
\]

## 4. 有限严格前缀进入共同椭球

**定理 3（有限前缀捕获）.** 设 \(\tau\) 位于一个闭区间 \(J\)，并已知前 \(K\) 步的
候选分支 \(D_1,\ldots,D_K\)。若可严格证明：

1. 对每个 \(\tau\in J\)，第 \(k\) 步真实投影确实采用 \(D_k\)；
2. 第 \(K\) 步状态统一满足 \(V(w^K(\tau)-w^\star)<\alpha\)；

则对每个 \(\tau\in J\)，该初值生成的真实 ADMM 序列都收敛到 \(w^\star\)。

**证明.** 前两项保证第 \(K\) 步已进入定理 1 或定理 2 的正向不变椭球；以 \(K\) 为新的
起点应用相应局部定理即可。∎

本实例使用如下完全有理的区间敏感度证书。以
\(\tau_c^0=1/2\) 的精确中心轨道为 \(s_k^c\)，令

\[
|s_k(\tau)-s_k^c|\le r_k
\]

逐坐标成立。若 \(|\tau-1/2|\le h\)，并且第 \(k\) 步已认证分支 \(D_k\)，则

\[
r_{k+1}=
|T_{D_k}(1/2)|r_k
+h\bigl(|E_{D_k}|\,|s_k^c|+|E_{D_k}|r_k+|f_{D_k}|\bigr)
\]

是下一步误差的严格逐坐标上界。每一步再用

\[
|q^+(\tau)-q_c^+|\le |C|r_k
\]

检查真实符号。最后，若 \(e_c=s_K^c-w^\star\)，则

\[
V(e_K(\tau))
\le V(e_c)+2|He_c|^\top r_K+r_K^\top|H|r_K.
\]

精确有理程序取

\[
h=10^{-10},\qquad K=232,
\]

验证了区间

\[
\boxed{
\frac{4999999999}{10000000000}
\le\tau\le
\frac{5000000001}{10000000000}}
\]

内的全部轨道先采用两步 \(00\)，随后一直采用 \(01\) 至第 232 步；所有符号下界均严格为
正，并且第 232 步统一满足

\[
\frac{V(e^{232})}{\alpha}
\le 0.97537998816016382196<1.
\]

这给出了一个非退化的有理步长区间。区间很窄是因为逐坐标绝对值递推会累积 wrapping
overestimate；它只是一个保守的充分区间，不表示实际稳定区间只有这么宽。

## 5. 严格 \(01\) 分支的精确谱边界

对该有理实例，精确特征多项式分解为

\[
\det(zI-T_{01}(\tau))
=\frac{z(z+\tau-1)}{405010000000000000}\,Q_\tau(z),
\]

其中

\[
\begin{aligned}
Q_\tau(z)={}&405010000000000000z^4\\
&+(3915586057000000\tau-1169276880943000000)z^3\\
&+(-4222461747714000\tau+1123984258642286000)z^2\\
&+(725214346843457\tau-359717740103975543)z\\
&-362404689543\tau+362404689543.
\end{aligned}
\]

对实四次多项式逐层应用 Schur 递推

\[
\mathcal S P(z)=
\frac{a_0P(z)-a_nz^nP(1/z)}{z},
\qquad |a_n|<a_0,
\]

并对所有一元因子使用精确 Sturm 根计数。除下式外，其余 Schur 因子在 \((0,1)\) 内均
严格为正：

\[
\begin{aligned}
G(\tau)={}&
111794210406295556649228900462157733493\tau^3\\
&+23105776975281816108275814441284422085171521\tau^2\\
&-244157339715898821440243649673959463071543521\tau\\
&+208410060660460340386576638889814578828638507.
\end{aligned}
\]

Sturm 证书给出：\(G\) 在 \((0,1)\) 中恰有一个实根 \(\tau_c\)，并且

\[
\boxed{0.9366061114<\tau_c<0.9366061115}.
\]

因此，在 \(0<\tau<1\) 内有精确等价关系

\[
T_{01}(\tau)\text{ Schur 稳定}
\quad\Longleftrightarrow\quad
0<\tau<\tau_c.
\]

这个边界描述的是 KKT 点附近固定 \(01\) 分支的局部谱稳定性，不是任意初值全局收敛的
临界步长。

## 6. 证据与复现

- exact certifier：`experiments/breakthrough/certify_relaxed_multiplier_interval_theory.py`
- JSON certificate：`outputs/tau_relaxation_theory_2026-07-16/results/certificate.json`
- human summary：`outputs/tau_relaxation_theory_2026-07-16/RUN_SUMMARY.md`
- regression tests：`tests/test_relaxed_multiplier_interval_theory.py`
- fixed \(\tau=1/2\) base certificate：
  `outputs/tau_multiplier_relaxation_2026-07-15/exact_half_convergence_certificate.json`

所有矩阵恒等式、Sylvester 主子式、Sturm 根数、前缀符号和椭球进入判定都使用精确有理数；
十进制只用于正文显示。
