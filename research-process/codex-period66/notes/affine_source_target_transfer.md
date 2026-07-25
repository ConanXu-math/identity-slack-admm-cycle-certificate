# 仿射 Source-Target Transfer

状态：`accepted_by_independent_followup_review`

证据等级：reviewed theorem；`proof_reviews/affine_source_target_transfer/followup_verification.json` 已关闭初审全部 blocker。

## 1. 仿射 factorization

在 TS-2 的 proof-grade 域内，真实 reduced edge map 可写为

\[
F_{b,c}(r)=G_c(K_br+k),
\qquad
G_d=\operatorname{diag}(I,S_d),\quad S_d=2D_d-I.
\]

这里 \(K_b\) 是 source matrix，而共同 offset 为

\[
k=
\begin{pmatrix}
\beta H_y^{-1}B^\top(I-M)h\\
(I-N)(I-M)h
\end{pmatrix}.
\]

它与 source/target mask 均无关。该公式允许 \(B\) 为非方阵，因为 reduced state 仍是 \(r=(y,u)\)。本文件定义同维的 rectangular legacy affine self-map

\[
L_b(r)=G_b(K_br+k).
\]

当 \(\dim y\ne m\) 时，这不是旧 Stage 4G 的 \(2m\) 维 legacy system，因而不能继承旧 length-3 Schur/Jury 谱界。这里证明的是新的 \((\dim y+m)\)-维 transfer theorem。

## 2. 齐次 lift 与共同 defect

令

\[
\widehat K_b=\begin{pmatrix}K_b&k\\0&1\end{pmatrix},\qquad
\widehat G_d=\begin{pmatrix}G_d&0\\0&1\end{pmatrix}.
\]

则 \(\widehat G_d^2=I\)，并且

\[
\widehat Q=\widehat G_d-2\widehat K_d
=\begin{pmatrix}Q&-2k\\0&-1\end{pmatrix}
\]

与 mask 无关。定义 \(\widehat H_d=\widehat G_d\widehat Q\)。由

\[
\widehat K_d\widehat G_d\widehat Q
=\widehat Q\widehat G_d\widehat K_d
\]

得到每条真实 edge 的 intertwining

\[
\widehat F_{b,c}\widehat H_b
=\widehat H_c\widehat L_b,
\quad
\widehat F_{b,c}=\widehat G_c\widehat K_b,
\quad
\widehat L_b=\widehat G_b\widehat K_b.
\]

沿任意 closed word telescope 后，

\[
\widehat P_F\widehat H_{b_0}
=\widehat H_{b_0}\widehat P_L.
\]

## 3. 可逆情形与 affine chart

因为

\[
\det\widehat Q=-\det Q,
\]

当 \(Q\) 可逆时，两个齐次周期 maps 相似。\(\widehat H_d\) 的最后一行是 \((0,-1)\)：它保持无穷远超平面 \(s=0\)，并把 affine chart \(s=1\) 映到 \(s=-1\)，整体乘 \(-1\) 后规范回 \(s=1\)。因此周期固定点和完整 Jordan structure 可双向搬运，并保持 finite/infinite homogeneous directions 的类型。

若周期 affine map 为 \(r^+=Pr+a\)，则：

- 固定点存在当且仅当 \((I-P)r=a\) 可解；
- 线性 affine drift 需要 \(d\ne0\)、\(Pd=d\)，并存在 finite-chart vector 满足 \((\widehat F-I)[r;1]=[d;0]\)；
- 即使代数 drift 成立，真实 ADMM drift 仍需 TS-2 的无限 itinerary admissibility。

## 4. 奇异情形的完整辅助族

当 \(Q\) 奇异时，原恒等式只给 semiconjugacy。为证明齐次周期 products 的特征多项式仍相同，对标量 \(t\) 定义

\[
\widehat Q_t=\widehat Q+tI,
\qquad
\widehat K_{d,t}=\frac{\widehat G_d-\widehat Q_t}{2}
=\widehat K_d-\frac t2 I,
\]

以及完整辅助族

\[
\widehat F_{b,c}(t)=\widehat G_c\widehat K_{b,t},\qquad
\widehat L_b(t)=\widehat G_b\widehat K_{b,t},\qquad
\widehat H_d(t)=\widehat G_d\widehat Q_t.
\]

对 closed word 定义

\[
\widehat P_F(t)=\widehat F_{b_{L-1},b_0}(t)\cdots
\widehat F_{b_0,b_1}(t),
\]

\[
\widehat P_L(t)=\widehat L_{b_{L-1}}(t)\cdots\widehat L_{b_0}(t).
\]

共同-defect 代数对每个 \(t\) 成立，因此

\[
\widehat P_F(t)\widehat H_{b_0}(t)
=\widehat H_{b_0}(t)\widehat P_L(t).
\]

多项式 \(p(t)=\det(\widehat Q+tI)\) 是首一多项式，只有有限个根。对其他 \(t\)，\(\widehat H_{b_0}(t)\) 可逆，两个辅助 period products 相似。其特征多项式系数都是 \(t\) 的多项式，并在无限多个 \(t\) 上相等，故在 \(t=0\) 也相等。\(t\ne0\) 的辅助族只用于代数延拓，无需保持 affine ADMM 语义。

特征多项式相同不能推出 Jordan 链、固定点或 drift 双向等价。警示例：

\[
A=I_2,\qquad B=\begin{pmatrix}1&1\\0&1\end{pmatrix},\qquad
H=\begin{pmatrix}0&1\\0&0\end{pmatrix}
\]

满足 \(AH=HB\)，且 \(A,B\) 特征多项式相同，但 Jordan 与固定点行为不同。

## 5. 与 TS-2 的关系

该 transfer 只搬运 affine recurrence，不自动搬运 canonical half-open cells。要把 legacy fixed point 或 drift ray 升级成真实 ADMM 结论，仍须：

1. 将 TS-2 edge inequalities 通过 phase maps 拉回；
2. 证明 basepoint 或 recession direction 满足 strict/weak rows；
3. 对无限 drift 证明所有周期重复均保持 admissible；
4. 对具体有理数据给 exact/rational 或 interval certificate。

## Provenance

- `proof_reviews/stage5_true_switching_transfer/proof_blueprint.md`
- `notes/ts2_affine_itinerary_polyhedra.md`
- `src/admm_identity/affine_transfer.py`
- `proof_reviews/affine_source_target_transfer/verification_report.json`

## Uncertainty

- 奇异 \(Q\) 下只接受 semiconjugacy 与 characteristic-polynomial transfer，不接受 Jordan/fixed-point transfer。
- 非方阵 \(B\) 下不继承旧 Stage 4G legacy 谱证书。
- 尚无具体 word 的 exact admissibility 或严格反例。

## Failed Explorations

- 把齐次特征多项式相同解释为 Jordan drift 等价是无效跳步。
- 把 rectangular legacy self-map 当作旧 Stage 4G 的 \(2m\) 维对象会造成 scope leakage。
