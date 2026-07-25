# General Active-Mask Reduction

状态：`proof_attempt`

这份 note 继续 `notes/active_set_quotient_reduction.md`。前一份 note 只处理全 active 情形 \(D=I\)；这里处理一般固定 active mask \(D\ne I\)，目标是把被一步清零的 bookkeeping 分量消去，得到真正承载非零谱的 reduced map。

## 1. 固定 mask 后的一步互补结构

令 \(D=\operatorname{diag}(d_i)\)，其中 \(d_i=1\) 表示 \(q_i>0\) 的 active projection coordinate，\(d_i=0\) 表示 inactive coordinate。固定 mask 下，

\[
z^{k+1}=Dq^{k+1},\qquad
\lambda^{k+1}=\beta(I-D)q^{k+1}.
\]

因此一步后必有

\[
z_N^{k+1}=0,\qquad \lambda_A^{k+1}=0.
\]

所以对 \(T_D\) 的任意非零特征值 \(\eta\ne0\)，对应特征向量必须满足

\[
\xi_{z_N}=0,\qquad \xi_{\lambda_A}=0.
\]

这说明原始 effective state \(v=(y,z,\lambda)\) 中的 \(z_N\) 和 \(\lambda_A\) 只贡献零特征值；真正需要分析的是 invariant complementarity manifold。

## 2. Reduced coordinate \(u=z-\lambda/\beta\)

在该 manifold 上定义

\[
u=z-\lambda/\beta.
\]

于是 active coordinate 满足 \(u_A=z_A\)，inactive coordinate 满足 \(u_N=-\lambda_N/\beta\)。给定 \((y,u)\) 和固定 mask，可以嵌回

\[
z=Du,\qquad \lambda=-\beta(I-D)u.
\]

这个坐标把 active slack 和 inactive normal-cone multiplier 放进同一个 \(m\)-维变量。代码入口是：

- `unpack_complementarity_reduced_state`
- `pack_complementarity_reduced_state`
- `build_complementarity_reduced_map`
- `complementarity_reduced_linear_matrix`

## 3. Reduced map 的解析公式

只看扰动项，令

\[
H_x=Q_1+\beta A^\top A,\qquad
H_y=Q_2+\beta B^\top B,
\]

\[
M_x=\beta A H_x^{-1}A^\top,\qquad
N_y=\beta B H_y^{-1}B^\top,
\]

并令

\[
S_D=2D-I.
\]

由于 \(x\)-step 只通过

\[
By+z-\lambda/\beta=By+u
\]

感知旧的 slack/multiplier 组合，有

\[
\delta x^+=-\beta H_x^{-1}A^\top(B\delta y+\delta u).
\]

\(y\)-step 给出

\[
\delta y^+
=\beta H_y^{-1}B^\top M_xB\,\delta y
-\beta H_y^{-1}B^\top(I-M_x)\,\delta u.
\]

另一方面，

\[
\delta q^+=-A\delta x^+-B\delta y^+-(I-D)\delta u,
\]

并且 \(u^+=S_Dq^+\)。因此 reduced linear map

\[
\begin{pmatrix}\delta y^+\\ \delta u^+\end{pmatrix}
=R_D
\begin{pmatrix}\delta y\\ \delta u\end{pmatrix}
\]

的矩阵为

\[
R_D=
\begin{pmatrix}
\beta H_y^{-1}B^\top M_xB
&
-\beta H_y^{-1}B^\top(I-M_x)
\\
S_D(I-N_y)M_xB
&
S_D\{N_y+(I-N_y)M_x-(I-D)\}
\end{pmatrix}.
\]

## 4. 与 \(T_D\) 的谱关系

令 \(E_D\) 表示从 \((y,u)\) 嵌回 \((y,z,\lambda)\) 的线性映射，令 \(P_D\) 表示从 \((y,z,\lambda)\) 取出 \((y,z-\lambda/\beta)\)。固定 mask 一步更新满足

\[
T_DE_D=E_DR_D.
\]

同时，\(T_D\) 的输出总在 \(z_N=0,\lambda_A=0\) 的 manifold 中。若 \(\eta\ne0\) 是 \(T_D\) 的特征值，则其特征向量已在该 manifold 内，因而对应到 \(R_D\) 的特征向量。反过来，\(R_D\) 的特征向量经 \(E_D\) 嵌回就是 \(T_D\) 的特征向量。因此

\[
\sigma(T_D)\setminus\{0\}=\sigma(R_D)\setminus\{0\}.
\]

这一步已经由 `tests/test_slack_projection.py` 中的 reduced spectrum test 数值校验。

## 5. 与 \(D=I\) 情形的关系

当 \(D=I\) 时，\(S_D=I\)，inactive 项消失，\(u=z\)。此时 \(R_D\) 退回全 active 分析。进一步使用 \(h=By+u\) 可以拆出：

\[
\delta h^+=M_x\delta h,
\]

以及 \(h=0\) 的 split map。前一份 note 已证明这些 reduced maps 在 \(Q_1,Q_2\succeq0\) 且子问题矩阵正定时不产生 \(|\eta|>1\) 的扩张。

## 6. 一般 \(D\ne I\) 的新风险项

一般 mask 中真正新增的是

\[
S_D\{N_y+(I-N_y)M_x-(I-D)\}.
\]

其中 \(-(I-D)\) 只作用于 inactive 坐标，再乘上 \(S_D\) 后会改变符号。这是 inactive normal-cone multiplier 的反馈项，也是下一步理论分析的核心。

当前结论不是收敛定理，也不是反例，而是一个 proof-grade 结构化约简：

```text
general_active_mask_reduced_map_ready
```

## 7. 可证明的 coordinatewise sanity bound

若在某组坐标下 \(B=I\)，并且 \(M_x,N_y,D\) 可以同时对角化，则 \(R_D\) 按坐标拆成 \(2\times2\) 小块。记对应特征值为 \(m,n\in[0,1]\)。

active 坐标 \(d=1\) 的小块是

\[
\begin{pmatrix}
nm & -n(1-m)\\
(1-n)m & n+(1-n)m
\end{pmatrix},
\]

它的两个特征值为

\[
\{m,n\}.
\]

inactive 坐标 \(d=0\) 的小块是

\[
\begin{pmatrix}
nm & -n(1-m)\\
-(1-n)m & (1-n)(1-m)
\end{pmatrix},
\]

它的两个特征值为

\[
\{0,\ nm+(1-n)(1-m)\}.
\]

因为 \(m,n\in[0,1]\)，所以 coordinatewise / commuting 情形下

\[
\rho(R_D)\le1.
\]

这覆盖了完全解耦的 inactive-coordinate 情形；它说明单个 inactive coordinate 本身不会制造扩张。剩余难点是 \(D\) 与 \(M_x,N_y\) 不交换时的耦合。

补充：`experiments/certify_length3_coordinatewise_bernstein.py` 已把该 coordinatewise
sanity bound 推进到 length-3 switching。对标量 active/inactive blocks 的全部
`8` 个 length-3 words，Schur margins 的 degree `(3,3)` Bernstein coefficients
均非负，因此 simultaneous diagonalization / coordinatewise 情形下任意 length-3
product 满足 \(\rho\le1\)。该结论仍不处理 \(D\) 与 \(M_x,N_y\) 不交换时的耦合项。

## 8. 抽象 contraction screen

为避免重复普通随机 QP 筛查，新增脚本直接筛查上面的 reduced map 代数结构：

```bash
/opt/anaconda3/bin/python experiments/search_reduced_map_abstract_expansion.py \
  --dims 2,3,4 \
  --trials 5000 \
  --seed 20260705 \
  --output outputs/wo5_active_set_2026-07-05/abstract_reduced_map_screen.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/abstract_reduced_map_screen.json
```

输出状态是 `numerical_screen`。该 screen 随机生成 PSD contractions \(0\preceq M_x,N_y\preceq I\)，固定 \(B=I\)，枚举 mixed masks。结果：

- evaluations: `110000`
- max spectral radius: `0.9997018793790761`
- expanding count: `0`

随后对二维 mixed mask `[1,0]` 直接优化 \(\rho(R_D)\)，得到一个非交换 PSD contraction pressure candidate：

- optimized spectral radius: `1.002263982483121`
- active mask: `[1,0]`
- status: `numerical_screen`

这说明非交换 \(R_D\) 不能被当前 coordinatewise sanity bound 排除。

## 9. 嵌入实际 QP 的 candidate pressure

新增脚本将上面的抽象 \(M_x,N_y\) 反解为 \(A=B=I,\beta=1\) 下的凸二次数据：

```bash
/opt/anaconda3/bin/python experiments/build_reduced_map_qp_candidate.py \
  --input outputs/wo5_active_set_2026-07-05/results/abstract_reduced_map_screen.json \
  --rhs-trials 5000 \
  --rhs-seed 1 \
  --rhs-scale 100 \
  --stay-steps 2000 \
  --output outputs/wo5_active_set_2026-07-05/reduced_map_qp_candidate.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/reduced_map_qp_candidate.json
```

结果：

- fixed-active spectral radius: `1.0022626303042794`
- expanding eigenvalues: `2`
- top eigenvalue: `0.9999729077043129 + 0.06770940822244995i`
- fixed point active-region margin: `0.012718057300436302`
- perturbations `1e-8`、`1e-6`、`1e-4` 在 `2000` 步 finite stay check 中保持同一 active mask；
- perturbations `1e-3`、`1e-2` 会在有限步后离开该 active region。

这已经是 `candidate_counterexample` pressure，但仍不是 proof-grade counterexample。缺口在于：top unstable eigenvalue 是复数，实扰动会旋转；当前只有有限步 stay check，还没有证明存在非零初值使真实 projected ADMM 轨道全时保持同一个 active region 并发散。

## 10. Active-region invariant 分析

进一步分析见：

```bash
/opt/anaconda3/bin/python experiments/analyze_candidate_invariant.py \
  --input outputs/wo5_active_set_2026-07-05/results/reduced_map_qp_candidate.json \
  --stay-epsilons 1e-4,1e-5,1e-6 \
  --stay-steps 20000 \
  --output outputs/wo5_active_set_2026-07-05/candidate_invariant_analysis.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/candidate_invariant_analysis.json
```

结论：

- verdict: `fixed_mask_invariant_not_established`
- expanding modes 是复共轭对；
- signed-q coefficient 在不稳定旋转子空间上非零；
- `1e-4`、`1e-5`、`1e-6` 的实特征方向扰动分别在第 `2296`、`3318`、`4340` 步离开 fixed mask。

解析原因是：若 \(e_k=T_D^ke_0\)，active-region 条件是

\[
s\odot(q^\star+Le_k)>0.
\]

当非零不稳定投影对应 \(\eta=\rho e^{i\theta}\)、\(\rho>1\)、\(\theta\notin\{0,\pi\}\)，且某个 signed-q coefficient \(c\ne0\) 时，该坐标含有

\[
\rho^k\operatorname{Re}(ce^{ik\theta})
\]

这样的旋转扩张项。它会出现负值并且幅度增长，因此不能全时保持同一个 fixed mask。

所以当前 QP candidate 不能直接升级为 fixed-active proof-grade counterexample。它仍说明非交换 \(R_D\) 有局部扩张压力，但下一步应换目标：

1. 搜索实扩张特征值，或 signed-q functional 在不稳定子空间上消失的切向扩张；
2. 研究 active-set switching 是否能把旋转扩张转成真实发散；
3. 若这两条都失败，再回到加强假设或 correction algorithm 路线。

## 11. Fixed-mask invariant candidate screen

为直接搜索可支持 fixed-mask 严格反例的谱结构，新增：

```bash
/opt/anaconda3/bin/python experiments/search_fixed_mask_invariant_candidate.py \
  --dims 2,3,4 \
  --families uniform,boundary,ill_conditioned \
  --trials 1000 \
  --seed 20260706 \
  --output outputs/wo5_active_set_2026-07-05/fixed_mask_invariant_candidate_screen.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/fixed_mask_invariant_candidate_screen.json
```

该 screen 的目标不是普通谱半径，而是两种更强条件：

1. 正实扩张特征值，且可选择扰动方向使所有 signed-q coefficient 非负；
2. 复扩张特征值，但 signed-q functional 在不稳定子空间上为零，即切向扩张。

本轮结果：

- evaluations: `66000`
- records with expanding modes: `1`
- max spectral radius: `1.0079349219063447`
- candidate mode count: `0`
- top expanding mode: `complex_rotating_visible_to_signed_q`
- top active mask: `[0,1,0,0]`

这说明边界/病态 family 中仍可出现更强局部扩张，但本轮没有找到能全时保持 fixed mask 的实扩张射线或切向复扩张。因此 fixed-mask 反例路线的压力下降；下一步更自然的是 active-set switching 分析，或者使用更强的优化器专门搜索切向条件。

## 12. Switching cycle screen

根据 `notes/multi_agent_fixed_mask_debate.md` 的建议，新增：

```bash
/opt/anaconda3/bin/python experiments/search_active_set_switching_cycle.py \
  --input outputs/wo5_active_set_2026-07-05/results/reduced_map_qp_candidate.json \
  --cycle-lengths 2,3,4,5,6 \
  --mask-neighborhood all \
  --output outputs/wo5_active_set_2026-07-05/switching_cycle_screen_all_masks.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/switching_cycle_screen_all_masks.json
```

结果：

- cycle evaluations: `1364`
- records with expansion: `5`
- max spectral radius: `1.0136528063281143`
- candidate count: `0`

这些扩张记录仍对应重复原 fixed mask 的复旋转机制，没有给出正实 switching ray。因此，当前 QP candidate 没有短周期 all-mask switching 证书。

目前反例路线剩余两个可执行分支：

1. 专门优化 signed-q tangent 条件；
2. 证明 fixed-mask invariant expansion impossible，再研究更一般的 switching cone。

## 13. Signed-q tangent optimization

为避免普通随机 screen 漏掉切向扩张，新增：

```bash
/opt/anaconda3/bin/python experiments/optimize_signed_q_tangent.py \
  --seed 20260706 \
  --maxiter 120 \
  --tangent-weight 1.0 \
  --output outputs/wo5_active_set_2026-07-05/signed_q_tangent_optimization.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/signed_q_tangent_optimization.json
```

并用较小惩罚权重做对照：

```bash
--tangent-weight 0.05
--tangent-weight 0.001
```

三组结果都收敛到无扩张边界：

- spectral radius: `0.9999993332494114`
- expanding mode count: `0`

解释：在当前二维 `[1,0]` 参数化中，优化器宁愿牺牲扩张也无法找到 signed-q 不可见的扩张模态。这不是“不存在切向扩张”的证明，但它进一步支持 fixed-mask invariant expansion impossible 这个证明方向。

因此下一轮更应尝试写 lemma，而不是继续扩大普通 screen：

1. visible complex/negative expansion 被 active margin 振荡排除；
2. tangent expansion 退化到 \(u=0\) 收缩块；
3. positive outward ray 不存在或需要专门构造反例。
