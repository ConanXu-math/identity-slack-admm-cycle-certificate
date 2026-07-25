# Length-2 Pair-Class Consolidation

状态：`local_theorem_accepted_by_review`

本文接在 `notes/short_cycle_switching_nonexpansion_conjecture.md` 和
`notes/single_full_proof_attempt.md` 之后。目标是按剃刀原则收口 `SC-1`：
只整理二维 length-2 nonconstant active-mask pair 的证据等级和最小剩余证明义务，
不扩展到普通随机 screen、length-3、任意周期或全局 ADMM 收敛。

## 1. Setup

固定二维 reduced map

\[
R_D(M,N),\qquad 0\preceq M,N\preceq I,
\]

并考虑非恒定 pair product

\[
P_{D_0,D_1}=R_{D_1}(M,N)R_{D_0}(M,N),\qquad D_0\ne D_1.
\]

全部 `12` 个 ordered pairs 分成四类：

| class | ordered pairs | 当前证据等级 |
| --- | --- | --- |
| `zero_single` | `[[0,0],[1,0]]`, `[[0,0],[0,1]]`, `[[1,0],[0,0]]`, `[[0,1],[0,0]]` | ordered class 已由 `proof_reviews/zero_single_ordered_class/` 接受 |
| `zero_full` | `[[0,0],[1,1]]`, `[[1,1],[0,0]]` | canonical representative 与 ordered class 均已由 `proof_reviews/zero_full_pc1/`、`proof_reviews/zero_full_ordered_class/` 接受 |
| `single_single` | `[[1,0],[0,1]]`, `[[0,1],[1,0]]` | ordered class 已由 `proof_reviews/single_single_ordered_class/` 接受 |
| `single_full` | `[[1,0],[1,1]]`, `[[0,1],[1,1]]`, `[[1,1],[1,0]]`, `[[1,1],[0,1]]` | representative `[[1,0],[1,1]]` 的 cubic margins 已通过本地 review |

## 2. 已能安全声明的内容

第一，`outputs/wo5_active_set_2026-07-05/length2_switching_symbolic_check.md`
用 exact symbolic algebra 验证全部 `12` 个 pair 满足

\[
\det(P_{D_0,D_1})=0.
\]

这只是 determinant 结构：它给出一个零特征值，不控制剩余 cubic factor。

第二，`proof_reviews/single_full_cubic_margins/verification_report.json`
接受了局部命题：

```text
For the 2D single_full representative [[1,0],[1,1]],
the cubic Jury margins J+, J-, Jmid, Jconst are nonnegative
for 0 <= M,N <= I.
```

该结论的依据是 full two-angle 参数化和 exact Bernstein certificates。接受范围只到
`single_full` 的一个 representative，不自动覆盖全部 `SC-1`。

第三，`outputs/wo5_active_set_2026-07-05/length2_switching_product_screen.md`
覆盖了全部 `12` 个 pair 的随机 PSD contraction 诊断；它只能作为 `numerical_screen`。
当前 `zero_single`、`zero_full`、`single_single` 与 `single_full` 都已有 review-backed
证明链，最终 `SC-1` assembly 已由 `proof_reviews/sc1_length2_nonconstant_pairs/` 接受。

## 3. 代表元归约义务

在写完整 `SC-1` 证明前，需要先补一个小的对称性 lemma。

1. 坐标置换：`[1,0]` 与 `[0,1]` 应由同一个坐标交换矩阵共轭归约。由于
   \(0\preceq M,N\preceq I\) 的类对正交共轭封闭，证明一个坐标代表元应覆盖交换后的代表元。
2. 顺序反转：`R_{D_1}R_{D_0}` 与 `R_{D_0}R_{D_1}` 的非零谱相同。结合 determinant-zero，
   Schur/Jury 证明可以只对一个 ordered representative 写。

这两个事实已整理到 `notes/length2_pair_symmetry_reduction.md`，并已由
`proof_reviews/length2_pair_symmetry_reduction/` 接受。因此全部 `12` 个 ordered pairs
的证明目标已压到四个 canonical representatives；这些 representative 与最终总装
现均已完成 review，因此 `SC-1` 可作为二维 length-2 局部 theorem 使用。

## 4. 最小剩余证明义务

`SC-1` 的下一轮不应再跑普通 numerical screen，而应只补以下 exact obligations。

| obligation | 内容 | 优先级 |
| --- | --- | --- |
| `PC-0` | 写出坐标置换和顺序反转的谱归约 lemma，覆盖每个 class 的 ordered variants。 | 已由 `proof_reviews/length2_pair_symmetry_reduction/` 接受 |
| `PC-1` | 对 `zero_full` canonical `[[0,0],[1,1]]` 推导 exact charpoly 或 quotient contraction。 | 已由 `proof_reviews/zero_full_pc1/` 接受；ordered class 已由 `proof_reviews/zero_full_ordered_class/` 接受 |
| `PC-2` | 对 `zero_single` canonical `[[0,0],[1,0]]` 总装四个 quadratic margins，并经 `PC-0` 覆盖 ordered variants。 | 已由 `proof_reviews/zero_single_ordered_class/` 接受 |
| `PC-3` | 对 `single_single` canonical `[[1,0],[0,1]]` 补完整 cubic Jury certificate，并用 `PC-0` 覆盖 ordered class。 | 已由 `proof_reviews/single_single_ordered_class/` 接受 |
| `PC-4` | 将四类证书放入 verifier-style review，再考虑是否把 `SC-1` 从 `conjecture` 升为局部 theorem。 | 已由 `proof_reviews/sc1_length2_nonconstant_pairs/` 接受 |

## 5. 当前不能证明的内容

本 consolidation 不证明：

- length-2 之外的 active-set switching 已经成立；
- length-3 或任意 switching cycle 非扩张；
- joint spectral radius 或 common Lyapunov seminorm 存在；
- 三维及以上 active-mask switching 非扩张；
- 非二次、额外 \(X,Y\) 约束或全局 slack-variable ADMM 收敛；
- 严格收缩或 uniform margin。已有 `single_full` 边界显示单位圆等号是真实存在的。

## 6. 剃刀结论

当前最小主线是：

```text
PC-0 symmetry lemma [accepted]
-> PC-2 zero_single ordered class [accepted]
-> PC-1 zero_full ordered class [accepted]
-> PC-3 single_single ordered class [accepted]
-> SC-1 proof review [accepted]
```

当前 `SC-1` 已可写成局部 theorem：二维 reduced active-set 模型中的全部 length-2
nonconstant ordered pair products 的非零谱位于闭单位圆内。它仍不是 ADMM 收敛证明，
也不是严格反例。
