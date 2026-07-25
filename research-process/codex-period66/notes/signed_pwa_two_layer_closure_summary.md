# Signed-PWA 两层理论闭环总结

状态：`reviewed_two_layer_closure`。本页只汇总已经 exact 认证并独立复核的结论。

## 定理 A：Gate 外固定 QP

考虑 \(A=B=I_2\)、\(b=0\)、\(\beta=1\)，以及

\[
Q_1=3I,\qquad
Q_2=\frac1{779}\begin{pmatrix}4421&2500\\2500&1921\end{pmatrix}.
\]

该实例严格不满足旧 small-gain theorem 的 \(a\le1/6\)、\(b\le1/2\) 两个 norm bounds。
但是 signed state \(s^k=(y^k,q^k)\)、\(q^k=z^k+\lambda^k\) 满足连续 PWA recurrence，
其四个线性分支对

\[
H=\operatorname{diag}(I_2,9I_2/4),qquad \gamma=99/100
\]

共同严格收缩。由跨 orthant 线段分割和 Banach 定理，直接三块 ADMM 对任意有限初值
全局几何收敛到唯一零 KKT 点。

## 定理 B：Affine Family 与开放邻域

对任意 rhs \(b\) 和目标一次项 \(c_1,c_2\)，signed recurrence 只增加共同 offset；因此
增量收缩常数不变。进一步，若实对称 reduced matrices 满足

\[
\|M-I/4\|_2\le1/100,
\qquad
\left\|N-
\begin{pmatrix}27/100&-1/4\\-1/4&13/25\end{pmatrix}
\right\|_2\le1/100,
\]

则整个邻域仍由同一 \(H\)、\(\gamma=99/100\) 全局增量收缩。Exact 扰动计算保留统一
residual 余量

\[
\eta=405667/3125000>0.
\]

因此该邻域中的每个强凸二次 Hessian 对、任意 rhs、任意一次项以及任意有限初值，都
全局几何收敛到各自唯一 KKT 点。

## Proof-Grade 证据

| 义务 | 证据 |
| --- | --- |
| 原 ADMM 到 signed recurrence | `experiments/breakthrough/certify_fixed_qp_signed_pwa.py` |
| Gate 外 exact 证据与四分支 contraction | `outputs/breakthrough_attempts/stage25_fixed_qp_signed_pwa/` |
| 连续 PWA 增量证明与 fixed-point/KKT | `notes/fixed_qp_signed_pwa_contraction_theorem.md` |
| Arbitrary affine offset 与非零 rhs witness | `outputs/breakthrough_attempts/stage26_fixed_qp_affine_family/` |
| 半径 \(1/100\) 的 exact 扰动余量 | `notes/fixed_qp_signed_pwa_affine_family_theorem.md` |
| 两层独立复核 | 两个目录中的 `review_manifest.json` |

本轮 P0/P1 定向回归为 `14 passed`，其中包含独立原 ADMM oracle、任意 affine 数据符号恒等式、
邻域常数重构和非对称证书输入拒绝。全量回归为 `209 passed, 2 SIGKILL`；两个被系统终止的
子进程用例隔离复跑分别通过（`1 passed in 99.47s`、`1 passed in 0.44s`），故这是全量运行的
资源峰值，不是断言失败。相关 JSON 均通过 `json.tool`，`git diff --check` 干净。

## 未解决范围

以上结果仍固定 \(A=B=I\)、\(\beta=1\)，邻域也在 reduced \((M,N)\) 坐标中定义。一般
非交换高维模型是否总收敛，或是否存在 proof-grade 可达发散 itinerary，仍是开放终局问题。
当前不应把两层闭环外推为一般 direct 三块 ADMM 定理。
