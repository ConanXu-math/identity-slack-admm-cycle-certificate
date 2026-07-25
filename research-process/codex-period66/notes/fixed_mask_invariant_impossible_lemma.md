# Fixed-Mask Invariant Expansion Impossible Lemma

状态：`proof_attempt`

本 note 接在 `notes/multi_agent_fixed_mask_debate.md` 之后。目标不是证明 ADMM 收敛，而是尝试证明：即使 fixed mask 的 reduced map \(R_D\) 有 \(\rho(R_D)>1\)，这些扩张模态也不能形成全时保持同一 active region 的严格反例。

## 1. Active-region 条件的线性形式

固定 mask \(D\)，令

\[
S_D=2D-I.
\]

在 reduced coordinate \(v=(y,u)\)、\(u=z-\lambda/\beta\) 中，

\[
u^+=S_Dq^+.
\]

因此若 \(w=(w_y,w_u)\) 是 \(R_D\) 的特征向量，

\[
R_Dw=\eta w,
\]

则对应下一步 signed-q coefficient 满足

\[
S_Dq^+=u^+=\eta w_u.
\]

所以 fixed-mask invariant ray 的关键不是单纯 \(|\eta|>1\)，而是 \(w_u\) 的符号结构。

## 2. 单个主导复扩张与负实扩张会离开 active region

若 \(\eta=\rho e^{i\theta}\)、\(\rho>1\)、\(\theta\notin\{0,\pi\}\)，且 \(w_u\ne0\)，则由该共轭特征对生成的纯实模态会在某个 signed-q margin 中产生

\[
\rho^k\operatorname{Re}(ce^{ik\theta})
\]

型项。该项振荡且幅度增长，因此该纯模态不能全时保持同一组 strict active
inequalities。若它是唯一主导谱对，同样结论适用于含有该非零投影的扰动。

若 \(\eta<-1\) 且 \(w_u\ne0\)，则对应纯实模态的 signed-q margin 交替变号，也不能
全时保持同一 mask。

这里不能直接把逐模态结论扩张为任意初值：同模长特征根、Jordan 链和输出抵消必须
统一处理。`proof_reviews/stage5_fixed_mask_exit/proof_blueprint.md` 已提出一个
dominant Jordan-layer + Cesàro 平均的完整路线，目标是排除 fixed mask 内的一切指数
增长轨道；该 blueprint 尚待独立审查。

这解释了 `outputs/wo5_active_set_2026-07-05/candidate_invariant_analysis.md`：当前 QP candidate 的扩张复模态对 signed-q 可见，因此最终离开 fixed mask。

## 3. Tangent expansion impossible

所谓 signed-q tangent expansion 是指扩张模态对 active inequalities 不可见。由第 1 节，

\[
S_Dq^+=\eta w_u.
\]

若 \(\eta\ne0\) 且 signed-q coefficient 为零，则

\[
w_u=0.
\]

此时 eigenproblem 的 \(y\)-块退化为

\[
\eta w_y
=\beta H_y^{-1}B^\top M_xB\,w_y,
\]

其中

\[
M_x=\beta A(Q_1+\beta A^\top A)^{-1}A^\top.
\]

在 \(Q_1\succeq0\)、\(H_x\succ0\) 下，

\[
0\preceq M_x\preceq I.
\]

因此

\[
0\preceq
\beta H_y^{-1/2}B^\top M_xB H_y^{-1/2}
\preceq
\beta H_y^{-1/2}B^\top B H_y^{-1/2}
\preceq I,
\]

其中 \(H_y=Q_2+\beta B^\top B\)。所以该 \(y\)-块没有大于 1 的特征值。

结论：

```text
signed-q tangent expansion impossible
```

在当前二次模型假设下，切向扩张不能成为 fixed-mask 严格反例。

## 4. Positive real expansion impossible

上一节只排除了 signed-q tangent expansion。剩余看似可能的是 positive outward ray：

\[
\eta>1,\qquad R_Dw=\eta w,\qquad w_u\ge0
\]

或整体取反后 \(w_u\le0\)。此时 signed-q margin 沿该 ray 不会变号。

但在当前凸二次 fixed-mask linearization 假设下，可以证明更强结论：不存在任何正实扩张特征值 \(\eta>1\)，不需要使用 \(w_u\) 单号性。

### 4.1 设定

令

\[
P=D,\qquad J=I-D,\qquad S=P-J.
\]

把 reduced eigenvector 记为 \((y,u)\)，并在 constraint space 中令

\[
a=By,\qquad p=Pu,\qquad n=Ju,\qquad \alpha=Pa,\qquad \gamma=Ja.
\]

记

\[
M=M_x,\qquad N=N_y.
\]

在 \(Q_1,Q_2\succeq0\)、\(H_x,H_y\succ0\) 下，

\[
0\preceq M\preceq I,\qquad 0\preceq N\preceq I.
\]

由 `notes/general_active_mask_reduction.md` 的 fixed-mask recurrence，若 \(R_D(y,u)=\eta(y,u)\)，则 \(a^+=\eta a\)、\(u^+=\eta u\)，并且

\[
M(a+u)=\eta(a+p)-(\eta-1)n. \tag{4.1}
\]

令

\[
b=a+p.
\]

则 (4.1) 写为

\[
M(b+n)=\eta b-(\eta-1)n. \tag{4.2}
\]

同时 \(a^+=N[M(a+u)-u]=\eta a\)，代入 (4.1) 得

\[
N\{\eta a+(\eta-1)p-\eta n\}=\eta a. \tag{4.3}
\]

### 4.2 基本 contraction lemma

若 \(0\preceq C\preceq I\) 且 \(Cv=t\)，则

\[
\|t\|^2\le \langle v,t\rangle. \tag{4.4}
\]

这是因为

\[
\langle v,t\rangle-\|t\|^2
=\langle v,Cv\rangle-\langle Cv,Cv\rangle
=\langle v,C(I-C)v\rangle\ge0,
\]

其中 \(C\) 与 \(I-C\) 同时对角化且均为 PSD。

### 4.3 应用于 \(M\)

将 (4.4) 用到 (4.2)，并使用 \(P\)-space 与 \(J\)-space 正交，得到

\[
[2\eta(\eta-1)+1]\langle \gamma,n\rangle
\ge
\eta(\eta-1)
\left(
\|\alpha+p\|^2+\|\gamma\|^2+\|n\|^2
\right). \tag{4.5}
\]

因此

\[
\langle \gamma,n\rangle\ge0. \tag{4.6}
\]

### 4.4 应用于 \(N\)

将 (4.4) 用到 (4.3)，可得

\[
(\eta-1)\langle \alpha,p\rangle
\ge
\eta\langle \gamma,n\rangle. \tag{4.7}
\]

### 4.5 合并矛盾

展开

\[
\|\alpha+p\|^2=\|\alpha\|^2+2\langle\alpha,p\rangle+\|p\|^2,
\]

并把 (4.7) 代入 (4.5)，得到

\[
[2\eta(\eta-1)+1]\langle \gamma,n\rangle
\ge
2\eta^2\langle\gamma,n\rangle
+\eta(\eta-1)
\left(
\|\alpha\|^2+\|p\|^2+\|\gamma\|^2+\|n\|^2
\right).
\]

移项为

\[
(1-2\eta)\langle\gamma,n\rangle
\ge
\eta(\eta-1)
\left(
\|\alpha\|^2+\|p\|^2+\|\gamma\|^2+\|n\|^2
\right). \tag{4.8}
\]

当 \(\eta>1\) 时，由 (4.6) 左边非正，右边非负。因此只能有

\[
\alpha=p=\gamma=n=0.
\]

于是 \(a=0,u=0\)。回到 \(y\)-block eigen equation：

\[
\eta y=\beta H_y^{-1}B^\top MBy
\]

且 \(By=a=0\)，所以 \(\eta y=0\)，进而 \(y=0\)。这与 eigenvector 非零矛盾。

结论：

```text
positive real expansion impossible
```

在当前凸二次 fixed-mask 模型下，

\[
\eta>1,\quad R_Dw=\eta w
\quad\Longrightarrow\quad
w=0.
\]

因此 positive outward ray 不仅不存在，而且 fixed-mask 的正实扩张方向整体不存在。

### 4.6 Targeted numerical pressure

为避免只停留在手工代数，新增两个定向 screen：

- `experiments/optimize_positive_outward_ray.py`：直接优化正实 cone-compatible eigenmode；
- `experiments/search_positive_outward_ray_feasibility.py`：固定 \(\eta>1\)，消去 \(y\)，枚举 support 并最小化 cone eigenpair 残差。

对应输出：

- `outputs/wo5_active_set_2026-07-05/positive_outward_ray_optimization.md`
- `outputs/wo5_active_set_2026-07-05/positive_outward_ray_feasibility.md`

这些输出状态仍是 `numerical_screen`。它们没有找到 strong candidate，但不能替代上面的 proof argument。

## 5. 当前结论

已经排除或强烈削弱的路线：

1. 单个或唯一主导的 visible complex expansion：会旋转离开 active region；
2. 单个或唯一主导的 negative real expansion：会交替离开 active region；
3. signed-q tangent expansion：退化到收缩块，不能有 \(|\eta|>1\)；
4. positive real expansion：由第 4 节 contraction argument 排除；
5. 短周期 switching ray：当前 screen 未找到证书。

第 4 节已接受的严格结论是“没有正实扩张特征值”；第 2 节的复/负实结论目前只在
纯模态或唯一主导模态层面成立。所有扩张谱分量的统一排除仍以
`proof_reviews/stage5_fixed_mask_exit/` 的审查结果为准。

本 note 不是全局收敛证明。剩余风险包括：

1. \(|\eta|=1\) Jordan block 或 affine offset 引起的 fixed-mask polynomial drift；
2. active-set switching 的非周期或长周期 cone certificate；
3. fixed-mask 之外的 Lyapunov / error-bound 路线；
4. 非二次目标或带额外 \(X,Y\) 约束时，local linearization 假设是否仍可复用。
