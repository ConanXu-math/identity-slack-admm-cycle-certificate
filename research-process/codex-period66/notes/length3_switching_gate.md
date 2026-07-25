# Length-3 Switching Gate

状态：`proof_attempt`

本文接在 `notes/length2_pair_class_consolidation.md` 之后。当前 `SC-1` 已由
`proof_reviews/sc1_length2_nonconstant_pairs/verification_report.json` 接受为二维
reduced active-set length-2 局部 theorem；本 note 只定义下一层 length-3 /
arbitrary switching 的证明或反例 gate，不声明 direct slack ADMM 全局收敛。

## 1. 为什么 SC-1 不能直接推出 length-3

`SC-1` 说明每个非恒定 pair product

\[
R_{D_1}(M,N)R_{D_0}(M,N),\qquad D_0\ne D_1,
\]

的非零谱位于闭单位圆内。这个结论是 product-by-product 的 Schur/Jury 证书，不是一个
共同 seminorm 或共同 Lyapunov 函数。没有共同度量时，pairwise spectral nonexpansion
不能组合成 length-3 nonexpansion。

一个纯线性代数 sanity example 是：

\[
A=\begin{pmatrix}-1&-2\\0&-1\end{pmatrix},\quad
B=\begin{pmatrix}1&1\\-1&0\end{pmatrix},\quad
C=\begin{pmatrix}1&1\\0&0\end{pmatrix}.
\]

全部 ordered pair products \(AB,BA,AC,CA,BC,CB\) 的谱半径都不超过 `1`，但
\(\rho(ABC)=2\)。这个例子不属于当前 \(R_D\) 结构；它只说明从 `SC-1` 到
length-3 必须新增共同 seminorm、直接 length-3 Schur/Jury 证书，或 cone-compatible
反例证书，不能靠逻辑外推。

## 2. 最小组合归约

运行：

```bash
/opt/anaconda3/bin/python experiments/enumerate_length3_switching_classes.py \
  --output outputs/wo5_active_set_2026-07-05/length3_switching_classes.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_switching_classes.json
```

得到 length-3 非恒定 words 共 `60` 个。按 cyclic shift 和二维坐标交换归约后有
`11` 类，其中 `7` 类含 adjacent repeat，`4` 类由三个不同 masks 组成且没有相邻重复。
这个归约不使用顺序反转；除非另证 reversal spectral equivalence，不能再压缩。

## 2.1 L3-1a determinant-zero lemma

运行：

```bash
/opt/anaconda3/bin/python experiments/symbolic_length3_switching_products.py \
  --output outputs/wo5_active_set_2026-07-05/length3_switching_symbolic_check.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_switching_symbolic_check.json
```

在二维 reduced map \(R_D(M,N)\) 中，单步 determinant 为：

| mask | \(\det(R_D)\) |
| --- | --- |
| `[0,0]` | `0` |
| `[1,0]` | `0` |
| `[0,1]` | `0` |
| `[1,1]` | `det(M) det(N)` |

因此任何非恒定 length-3 word 至少含有一个 non-full mask，进而由 determinant
multiplicativity 得到

\[
\det(R_{D_2}R_{D_1}R_{D_0})=0.
\]

这把 length-3 谱问题降到剩余 cubic factor，但不控制该 cubic factor 的根。

## 2.2 L3-1b cubic coefficient gate

运行：

```bash
/opt/anaconda3/bin/python experiments/symbolic_length3_cubic_coefficients.py \
  --output outputs/wo5_active_set_2026-07-05/length3_cubic_coefficients.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_cubic_coefficients.json
```

对每个 canonical word，令

\[
P=R_{D_2}R_{D_1}R_{D_0}.
\]

由于 `L3-1a` 已知 \(\det(P)=0\)，写

\[
\det(tI-P)=t(t^3+a_1t^2+a_2t+a_3).
\]

系数用 Newton identities 从 \(\operatorname{tr}(P)\)、\(\operatorname{tr}(P^2)\)、
\(\operatorname{tr}(P^3)\) 精确给出：

\[
a_1=-\operatorname{tr}(P),
\]

\[
a_2=\frac{\operatorname{tr}(P)^2-\operatorname{tr}(P^2)}{2},
\]

\[
a_3=-\frac{\operatorname{tr}(P)^3
-3\operatorname{tr}(P)\operatorname{tr}(P^2)
+2\operatorname{tr}(P^3)}{6}.
\]

`outputs/wo5_active_set_2026-07-05/results/length3_cubic_coefficients.json`
保存了全部 `11` 个 canonical classes 的 exact expression；Markdown 报告只保存
operation count、表达式长度和 hash，避免过程文档失控。当前最大表达式大小是
`len(a3)=161665`、`ops(a3)=29691`，说明直接人工读公式不可行，下一步应转为
结构化 margin / exterior-power / common-seminorm gate，而不是把公式全文搬进 note。

## 2.3 L3-2 Schur/Jury margin scaffold

运行：

```bash
/opt/anaconda3/bin/python experiments/symbolic_length3_jury_margins.py \
  --output outputs/wo5_active_set_2026-07-05/length3_jury_margins.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_jury_margins.json
```

该脚本从 `L3-1b` 的 \(a_1,a_2,a_3\) 构造

\[
J_+=1+a_1+a_2+a_3,\qquad
J_-=1-a_1+a_2-a_3,
\]

\[
J_{\rm mid}=1-a_2+a_1a_3-a_3^2,\qquad
J_{\rm const}: 1+a_3,\ 1-a_3.
\]

当前只记录每个 margin 的 expression length、operation count 和 hash；不把完整 margin
表达式写入 JSON。最大对象为 `Jmid`，长度 `347008`、operation count `63734`。
这说明 `L3-2` 不能靠人工展开阅读完成，下一步应寻找结构化 factorization、
Bernstein certificate、exterior-power 解释或 common-seminorm 证书。

## 2.4 L3-2b-coordinatewise Bernstein certificate

运行：

```bash
/opt/anaconda3/bin/python experiments/certify_length3_coordinatewise_bernstein.py \
  --output outputs/wo5_active_set_2026-07-05/length3_coordinatewise_bernstein_certificate.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_coordinatewise_bernstein_certificate.json
```

在 coordinatewise / simultaneous diagonalization 情形，每个坐标只需分析标量
\(m,n\in[0,1]\) 下的两个 \(2\times2\) blocks：

- `A`：该坐标 active；
- `Z`：该坐标 inactive。

脚本覆盖全部 `AAA, AAZ, AZA, AZZ, ZAA, ZAZ, ZZA, ZZZ` 八种 length-3 words。
对每个 word 的二次特征多项式，用 Schur 条件

\[
J_+=1-\operatorname{tr}(P)+\det(P),\quad
J_-=1+\operatorname{tr}(P)+\det(P),\quad
J_{\rm const}=1-\det(P)
\]

并将三个 margins 写成 degree `(3,3)` Bernstein form。所有 Bernstein coefficients
均非负，故该子情形下每个坐标块的谱半径不超过 `1`。因此若 \(M,N,D_j\) 可同时对角化，
任意 length-3 product 满足 \(\rho\le1\)。这是 `theorem` for coordinatewise /
commuting subcase；它不处理非交换二维 \(R_D\) 的耦合项。

## 2.5 L3-2c-rank-one-projector boundary

运行：

```bash
/opt/anaconda3/bin/python experiments/analyze_length3_rank_one_projector_boundary.py \
  --output outputs/wo5_active_set_2026-07-05/length3_rank_one_projector_boundary.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_rank_one_projector_boundary.json
```

该脚本把非交换二维 `L3-2c` 的一个边界子族固定为 rank-one projectors

\[
M=\frac1{1+x^2}\begin{pmatrix}1&x\\x&x^2\end{pmatrix},\qquad
N=\frac1{1+y^2}\begin{pmatrix}1&y\\y&y^2\end{pmatrix}.
\]

对全部 `11` 个 canonical length-3 classes 做 exact characteristic polynomial
分解后，去掉零根和允许的单位根，剩余因子的次数分布为：

- degree `1`：`6` 类；
- degree `2`：`4` 类；
- degree `3`：`1` 类。

其中 6 个一次 residual factor classes 已经由 \(S=x^2+y^2\)、\(u=xy\) 改写和
exact Sturm 正性检查闭合：

```text
L3C02, L3C05, L3C06, L3C07, L3C09, L3C11
```

两个最简单的 Schur numerator SOS 形态是：

\[
L3C07:\quad J_+=(x-y)^2,\qquad
J_-=2x^2y^2+(x+y)^2+2.
\]

\[
L3C11:\quad J_+=\left(x-\frac y2\right)^2+\frac34y^2+1,
\]

\[
J_-=2x^2y^2+\left(x+\frac y2\right)^2+\frac34y^2+1.
\]

其他 4 个一次类的 numerator 已在
`outputs/wo5_active_set_2026-07-05/length3_rank_one_projector_boundary.md`
中写成 \(S,u\) 形式；剩余单变量四次项由 exact Sturm sequence 给出
`real_root_count=0` 且正值点，从而恒正。

4 个二次 residual factor classes

```text
L3C01, L3C03, L3C04, L3C10
```

也已用同一个 half-domain split 闭合。具体令 \(S=x^2+y^2,u=xy\)，按
`u>=0` 与 `u<=0` 分别写成

\[
u=a,\ S=2a+t,\qquad u=-a,\ S=2a+t,\qquad a,t\ge0.
\]

`L3C10` 的所有 branch residual 都是非负系数多项式；`L3C04` 额外使用两个
half-line Sturm 正性检查；`L3C03` 与 `L3C01` 使用 AM-GM / square controls 加
half-line Sturm 正性检查。完整 branch residual 与 controls 写入 JSON。

`L3C08` 的三次 residual factor 也已闭合。五个 cubic Schur/Jury numerators
在 \(\alpha=x-y,\beta=x+y\) 坐标下均为偶偶次，故可写成
\(A_i(U,V)\ge0\)，其中 \(U=\alpha^2,V=\beta^2\ge0\)。`Jplus`、`Jmid`
与两个 `Jconst` margin 由 `U=rV` 系数证书闭合；`Jminus` 的直接系数法失败，
但两段证书闭合该缺口：`0<=r<=1` 时取 \(s=1-r\) 后系数为 \(s,1-s\) 的非负组合；
`r>=1,V>0` 时取 \(W=(r-1)V\)，把 `H=2048*P_r(V)` 分解为非负项加
\[
L(W)=W^4(W-14)^2+284W^2\left(W-\frac{152}{71}\right)^2
+\frac{271104}{71}W^2+6144W+4096.
\]

因此 rank-one projector affine chart 的 `11/11` 个 canonical classes 已闭合。
进一步用齐次参数
\[
P(a,b)=\frac1{a^2+b^2}\begin{pmatrix}a^2&ab\\ab&b^2\end{pmatrix}
\]
处理 projective infinity：`a=1,b=x` 是 affine chart，`a=0,b=1` 是
infinity projector。一步 reduced map 和 length-3 product 都是 \(M,N,D\) 的多项式表达，
谱半径关于矩阵 entries 连续，因此 finite affine theorem 可取极限覆盖
\(x=\infty\) 或 \(y=\infty\)。这个 closure argument 使用原始 product 矩阵的谱半径连续性，
不要求极限处 residual factor 的次数保持不变。

因此 rank-one projector projective boundary 已闭合。该结论仍只是 rank-one
projector boundary 子定理，不覆盖 scaled rank-one、full-rank interior，也不证明完整
`L3-2c`。

## 2.6 L3-2d-scaled-rank-one scaffold

运行：

```bash
/opt/anaconda3/bin/python experiments/analyze_length3_scaled_rank_one_scaffold.py \
  --output outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_scaffold.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_scaled_rank_one_scaffold.json
```

下一层子族释放 rank-one projector 的 eigenvalue：

\[
M=mP_x,\qquad N=nP_y,\qquad 0\le m,n\le1.
\]

这个子族不能由 `m=n=1` 的 projector boundary 直接推出。exact scaffold 显示：

- residual degree `2`：`10` 类；
- residual degree `3`：`1` 类，即 `L3C08`；
- 一些在 projector case 中只剩一次 residual 的类，在释放 `m,n` 后升为二次 residual。

因此 scaled rank-one 分支仍可控，但需要新的 Schur/Jury 非负证书。下一步优先尝试：

1. 对二次 residual classes 做 \(S=x^2+y^2,u=xy\) 改写，再对 \(m,n\in[0,1]\)
   做 Bernstein / endpoint split；
2. 对 `L3C08` 复用偶次 \(U,V\) 降维，再引入 `m,n` 的分片或 Bernstein 证书；
3. 若 margin 证书膨胀，转向 exterior-power 或 common-seminorm route。

该 artifact 只是 `proof_obligation_scaffold`，不是 theorem，也不是 counterexample。
本轮 multi-agent 审查还排除了三个看似自然但不成立的捷径：谱半径不沿 `m,n`
简单单调；`m=n=1` 不能作为 scaled 子族的上界代理；`m=0` 或 `n=0`
不自动落入 coordinatewise 子定理，因为非零谱仍可能含有与 mask 不对齐的
rank-one coupling。

## 2.7 L3-2d-first-certificate: scaled rank-one `L3C07`

运行：

```bash
/opt/anaconda3/bin/python experiments/certify_length3_scaled_rank_one_l3c07.py \
  --output outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c07_certificate.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_scaled_rank_one_l3c07_certificate.json
```

该脚本闭合第一个 scaled rank-one canonical class：

```text
L3C07: [0,0] -> [1,1] -> [1,1].
```

对 \(M=mP_x,N=nP_y,0\le m,n\le1\)，去掉两个零根后 residual 为二次多项式
\[
a\eta^2+b\eta+c,
\]
且 leading coefficient 为
\[
a=(1+x^2)(1+y^2)>0.
\]
因此只需证明二次 Schur/Jury margins
\[
a+b+c\ge0,\qquad a-b+c\ge0,\qquad a-c\ge0.
\]

`L3C07` 的三个 margins 都能写成 \(S=x^2+y^2,u=xy,m,n\) 的多项式。按
\[
u\ge0:\ u=a_0,\ S=2a_0+t,\qquad
u\le0:\ u=-a_0,\ S=2a_0+t,\qquad a_0,t\ge0
\]
分成两个半域。随后对 \(m,n\in[0,1]\) 做 degree `(3,3)` Bernstein 展开。结果是：

| margin | positive_u direct/special/open | negative_u direct/special/open | closed |
| --- | ---: | ---: | --- |
| `quadratic_Jplus_num` | 16/0/0 | 15/1/0 | `True` |
| `quadratic_Jminus_num` | 16/0/0 | 16/0/0 | `True` |
| `quadratic_Jconst_num` | 16/0/0 | 16/0/0 | `True` |

唯一非直接非负系数是
\[
\frac{9a_0^2-2a_0+4t+9}{9}
=\frac{9(a_0-\frac19)^2+4t+\frac{80}{9}}{9}\ge0.
\]

因此 `L3C07` scaled rank-one class 已闭合为局部 theorem。finite affine slope
证书通过齐次 rank-one projector 参数和 product matrix 谱半径连续性延拓到
projective slope 边界。该结论只覆盖 `L3C07`；剩余 scaled rank-one 义务仍包括
其他 `9` 个二次 residual classes 与 `L3C08` 三次 residual class。后续进展已继续
闭合 `L3C05/L3C06/L3C09/L3C10/L3C11`，见下方更新小节。

## 2.8 L3-2d-S,u batch certificate: `L3C02` and `L3C07`

运行：

```bash
/opt/anaconda3/bin/python experiments/certify_length3_scaled_rank_one_su_classes.py \
  --output outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_su_certificates.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_scaled_rank_one_su_certificates.json
```

该脚本把上面的 \(S,u\) 半域 + `(m,n)` Bernstein 模板批量应用到 scaled rank-one
的 `10` 个二次 residual classes。结果为：

- closed S,u classes：`L3C02`, `L3C07`；
- `S,u` 对称性不适用：`L3C01`, `L3C03`, `L3C04`, `L3C05`, `L3C06`,
  `L3C09`, `L3C10`, `L3C11`；
- `S,u` 可用但仍有 open Bernstein coefficients：无。

`L3C02=[0,0]\to[0,0]\to[1,1]` 的三个 quadratic margins 在 \(u\ge0\) branch
全部由非负 \(a_0,t\) 系数闭合；在 \(u\le0\) branch 只有三个特殊 Bernstein
系数需要额外证明：

\[
(4a_0+t)(3a_0^2-2a_0+t+3)
=(4a_0+t)\left(t+3(a_0-\frac13)^2+\frac83\right)\ge0,
\]

\[
\frac{11a_0^4+64a_0^3+27a_0^2t-6a_0^2+18a_0t+64a_0+9t^2+27t+11}{9}
\]
\[
=\frac{64a_0^3+27a_0^2t+18a_0t+64a_0+9t^2+27t}{9}
+\frac{11(a_0^2-\frac{3}{11})^2}{9}+\frac{112}{99}\ge0,
\]

\[
2a_0^4-4a_0^3+a_0^2t+20a_0^2+6a_0t-4a_0+t^2+t+2
\]
\[
=2a_0^2(a_0-1)^2+18(a_0-\frac19)^2+a_0^2t+6a_0t+t^2+t+\frac{16}{9}\ge0.
\]

因此 `L3C02` 和 `L3C07` 作为 scaled rank-one \(S,u\)-symmetric 子类已闭合。
对当时剩余 8 个二次类，`su_symmetry_unavailable` 只是路线诊断：当前模板不能使用，
不表示存在反例，也不表示这些类不可证明。其中 `L3C11` 已由下一节的非对称
判别式证书单独闭合；其余类仍需要非对称坐标、relative-angle、exterior-power
或 common-seminorm 路线。

## 2.9 L3-2d-discriminant certificate: `L3C11`

运行：

```bash
/opt/anaconda3/bin/python experiments/certify_length3_scaled_rank_one_l3c11_discriminant.py \
  --output outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c11_discriminant_certificate.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_scaled_rank_one_l3c11_discriminant_certificate.json
```

`L3C11=[[0,1],[1,1],[1,1]]` 不是 \(S,u\)-symmetric class，但三个 Schur/Jury
margins 在 finite affine slope chart 中都可写成关于 \(x\) 的二次式
\[
p(x)=Ax^2+Bx+C.
\]
脚本令 \(v=y^2\ge0\)，在 \(0\le m,n\le1\) 上用 Bernstein 系数闭合
\(A\ge0\)、\(C\ge0\) 和 \(4AC-B^2\ge0\)。具体证据为：

- `A` 与 `C`：degree `(3,3)` Bernstein in `(m,n)`，全部系数是 \(v\ge0\)
  上的非负多项式；
- `4AC-B^2`：degree `(6,6)` Bernstein in `(m,n)`，全部系数是 \(v\ge0\)
  上的非负多项式；
- 三个 margins 的 open coefficient count 均为 `0`。

若 \(A>0\)，由配方
\[
p(x)=A\left(x+\frac{B}{2A}\right)^2+\frac{4AC-B^2}{4A}\ge0
\]
闭合；若 \(A=0\)，则 \(4AC-B^2\ge0\) 推出 \(B=0\)，再由 \(C\ge0\)
得到 \(p(x)\ge0\)。因此 `L3C11` scaled rank-one canonical class 已闭合为
局部 theorem。projective slope 边界仍由齐次 rank-one projector 参数和谱半径
连续性闭合；这里得到的是 \(\rho\le1\)，不证明严格收缩、单位根半单或
power boundedness。该结论只覆盖 `L3C11`，不是完整 scaled rank-one theorem。

## 2.10 L3-2d-parity certificate: `L3C05`

运行：

```bash
/opt/anaconda3/bin/python experiments/certify_length3_scaled_rank_one_l3c05_parity.py \
  --output outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c05_parity_certificate.md \
  --json-output outputs/wo5_active_set_2026-07-05/results/length3_scaled_rank_one_l3c05_parity_certificate.json
```

`L3C05=[[0,0],[0,1],[1,1]]` 的三个 margins 不是 \(S,u\)-symmetric，但均有
parity 形式
\[
p(x,y)=E(X,Y,m,n)+xy\,O(X,Y,m,n),\qquad X=x^2,\ Y=y^2.
\]
因此只需证明 \(E\ge0\) 和 \(E^2-XYO^2\ge0\)，即可覆盖 \(xy=\pm\sqrt{XY}\)
两个符号分支。脚本用 \(X=a/(1-a),Y=b/(1-b)\) compactification 把
\(X,Y\ge0\) 化为 \(a,b\in[0,1]\)，再对 \((m,n,a,b)\) 做 exact Bernstein
检查。`Jminus` 与 `Jconst` 的 guard 直接 Bernstein 非负；`Jplus` 的 guard
只有 `m=n=1` top face 出现负 Bernstein 系数，该 face 精确分解为
\[
(a-b)^2(4a^2b+4ab^2+1)\ge0.
\]
因此 `L3C05` scaled rank-one canonical class 已闭合为局部 theorem。该结论
只覆盖 `L3C05`，不是完整 scaled rank-one theorem。

## 2.11 L3-2d-parity / exterior-square certificates: `L3C06`, `L3C09`, `L3C10`

后续 breakthrough route 继续处理 scaled rank-one priority classes：

- `L3C06=[[0,0],[1,1],[0,1]]` 复用 `L3C05` 的 parity/Bernstein 模板闭合；
- `L3C09=[[0,1],[0,1],[1,1]]` 由 exterior-square rank-defect reduction 把
  `Jmid` 化为 quadratic `Jconst`，并由 parity/Bernstein gate 闭合三个 margins；
- `L3C10=[[0,1],[1,0],[1,1]]` 的 `Jminus` 与 trace/Jmid (`Jconst`) 直接闭合；
  剩余 `Jplus` guard 一盒 Bernstein 有 `25` 个负系数，但 depth-1 dyadic 后只剩
  两个坏盒 `[1,1,0,0]` 与 `[1,1,1,1]`，沿 `a=b` 对角线三角化后四个 charts
  全部 exact Bernstein 非负。

对应 artifacts：

```text
outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c06_parity_certificate.md
outputs/breakthrough_attempts/stage3_exterior_square/l3c09_l3c10_trace_route.md
outputs/breakthrough_attempts/stage3_exterior_square/l3c10_jplus_triangle_certificate.md
```

因此当前 scaled rank-one 已闭合的 canonical classes 为：

```text
L3C02, L3C05, L3C06, L3C07, L3C09, L3C10, L3C11
```

该节点之后曾仍有三个二次 residual classes 与 `L3C08` 三次 residual class；
后续其中的 `L3C04` 与 `L3C03` 已由后续三角化证书闭合，当前只剩 `L3C01`
和 `L3C08`。

## 2.12 L3-2d-triangle certificate: `L3C04`

`L3C04=[[0,0],[0,1],[1,0]]` 也满足 parity 形式
\[
p(x,y)=E(X,Y,m,n)+xy\,O(X,Y,m,n).
\]
`Jminus` 与 `Jconst` 的 \(E\) 和 guard 在 compactified \((m,n,a,b)\) box 上
直接由 exact Bernstein 系数闭合。`Jplus` 的 \(E\) 经 depth-1 dyadic subdivision
闭合；guard 在 depth-1 后只剩 `[1,1,0,0]` 与 `[1,1,1,1]` 两个坏盒。
沿 `a=b` 对角线把两个坏盒的 `a,b` square 分成 `a>=b` 与 `b>=a` 两个 triangular
charts 后，四个 charts 全部 exact Bernstein 非负。

对应 artifact：

```text
outputs/breakthrough_attempts/stage3_exterior_square/l3c04_jplus_triangle_certificate.md
```

因此当前 scaled rank-one 已闭合的 canonical classes 更新为：

```text
L3C02, L3C04, L3C05, L3C06, L3C07, L3C09, L3C10, L3C11
```

## 2.13 L3-2d-triangle certificate: `L3C03`

`L3C03=[[0,0],[0,1],[0,1]]` 继续使用 parity gate：
\[
p(x,y)=E(X,Y,m,n)+xy\,O(X,Y,m,n).
\]
`Jconst` 的 \(E\) 与 guard 在 compactified \((m,n,a,b)\) box 上一盒闭合。
`Jminus` 的 \(E\) 与 guard 一盒 Bernstein 分别有负系数，但 depth-1 dyadic
subdivision 后全部子盒 exact Bernstein 非负。`Jplus` 的 \(E\) 也经 depth-1
闭合；guard 在 depth-1 后只剩 `[1,1,0,0]` 与 `[1,1,1,1]` 两个同半区坏盒。
沿 `a=b` 对角线把 lower/lower 与 upper/upper 的 `a,b` square 分成四个 triangular
charts 后，四个 charts 全部 exact Bernstein 非负。

对应 artifact：

```text
outputs/breakthrough_attempts/stage3_exterior_square/l3c03_triangle_certificate.md
```

因此当前 scaled rank-one 已闭合的 canonical classes 更新为：

```text
L3C02, L3C03, L3C04, L3C05, L3C06, L3C07, L3C09, L3C10, L3C11
```

## 2.14 L3-2d-triangle certificate: `L3C01`

`L3C01=[[0,0],[0,0],[0,1]]` 仍用同一 parity gate：
\[
p(x,y)=E(X,Y,m,n)+xy\,O(X,Y,m,n).
\]
`Jminus` 的 \(E\) 与 guard 经 depth-1 dyadic subdivision 闭合。`Jconst` 的
guard 在 depth-1 后只剩 `[1,1,1,1]` 一个坏盒，沿 `a=b` 对角线三角化后两个
charts exact Bernstein 非负。`Jplus` 的 guard 在 depth-1 后只剩
`[0,0,1,1]`、`[0,1,1,1]`、`[1,0,1,1]`、`[1,1,0,0]` 与 `[1,1,1,1]`
五个 same-half 坏盒；逐盒沿 `a=b` 三角化后十个 charts 全部 exact Bernstein 非负。

对应 artifact：

```text
outputs/breakthrough_attempts/stage3_exterior_square/l3c01_triangle_certificate.md
```

因此当前 10 个二次 residual scaled-rank-one canonical classes 均已闭合：

```text
L3C01, L3C02, L3C03, L3C04, L3C05, L3C06, L3C07, L3C09, L3C10, L3C11
```

该节点之后，scaled-rank-one 义务只剩 `L3C08` 三次 residual class；下一节已将其闭合。

## 2.15 L3-2d-cubic certificate: `L3C08`

`L3C08=[[0,1],[0,1],[1,0]]` 是 scaled-rank-one 分支中唯一 cubic/rank-3
residual class。五个 cubic Schur/Jury margins 仍保持 parity gate
\[
p(x,y)=E(X,Y,m,n)+xy\,O(X,Y,m,n).
\]
两个 `Jconst` margins 的 \(E\) 与 guard 一盒 exact Bernstein 闭合。`Jminus`
的 \(E\) 一盒闭合，guard 经 depth-1 dyadic subdivision 闭合。`Jplus` 的 \(E\)
经 depth-1 闭合，guard 在 depth-1 后只剩 `[1,1,0,0]` 与 `[1,1,1,1]`
两个 same-half top boxes，沿 `a=b` 三角化后四个 charts 全部 exact Bernstein
非负。最大项 `Jmid` 的 \(E\) 与 guard 也一盒闭合，其中 guard 的 Bernstein
degree 为 `(12,12,12,12)`，负系数为 `0`。

对应 artifact：

```text
outputs/breakthrough_attempts/stage3_exterior_square/l3c08_cubic_certificate.md
```

结合前面十个二次 residual classes，scaled-rank-one length-3 canonical classes
已全部闭合：

```text
L3C01, L3C02, L3C03, L3C04, L3C05, L3C06, L3C07, L3C08, L3C09, L3C10, L3C11
```

assembly artifact：

```text
outputs/breakthrough_attempts/stage3_exterior_square/scaled_rank_one_assembly.md
```

## 3. 下一层 theorem targets

强版本：

```text
L3-strong:
For dim=2 and every nonconstant length-3 mask word,
rho(R_D2 R_D1 R_D0) <= 1 for all 0 <= M,N <= I.
```

更贴近反例排除的版本：

```text
L3-cone:
For dim=2 and every nonconstant length-3 mask word,
there is no positive real eigenpair eta > 1 compatible with all switching cone margins.
```

若找反例，最低证书不能只是数值谱半径；必须给出 canonical word、exact/interval 形式的
\(\rho>1\) 证据、周期 basepoint、每段 signed-q cone margin，以及可嵌入凸二次
slack QP 的 active-region invariant 检查。

## 4. Proof obligations

1. `L3-0`：固定上面的 `11` 个 canonical words，不再扩大普通随机筛查。
2. `L3-1a`：length-3 determinant-zero lemma 已由单步 determinant 公式闭合。
3. `L3-1b`：剩余 cubic factor exact coefficients 已生成；determinant-zero 和
   coefficient extraction 不能替代 Schur/Jury 或 cone-margin 证明。
4. `L3-2a`：Schur/Jury margin scaffold 已生成；当前只是 exact symbolic object
   construction，不是 nonnegativity certificate。
5. `L3-2b`：基于系数检查
   \(J_+=1+a_1+a_2+a_3\)、\(J_-=1-a_1+a_2-a_3\)、
   \(J_{\rm mid}=1-a_2+a_1a_3-a_3^2\) 和 \(J_{\rm const}=1-|a_3|\)；
   若直接 margin 过大或结构不透明，转为 exterior-power
   或 singular-value 型证书。
6. `L3-2b-coordinatewise`：coordinatewise / commuting 情形已由 degree `(3,3)`
   Bernstein certificate 闭合为子定理。
7. `L3-2c-rank-one-projector`：rank-one projector projective boundary 已生成 exact
   boundary artifact；6 个线性 residual classes、4 个二次 residual classes
   和 `L3C08` 三次 residual 均已闭合，并由连续闭包覆盖 projective infinity，
   因此该 rank-one boundary 子定理为 `11/11`。
8. `L3-2d-scaled-rank-one`：exact scaffold 已生成。释放 \(m,n\) 后，`10`
   类为二次 residual，`L3C08` 为三次 residual；当前 `11/11` canonical classes
   均已由 Bernstein / parity / discriminant / trace / triangle 证书闭合。该结论仍
   不能由 projector boundary 直接外推到 full-rank interior。
9. `L3-2e-full-rank-interior-scaffold`：Stage 4 已采用
   \(N=\operatorname{diag}(\nu_1,\nu_2)\)、
   \(M=R(c,s)\operatorname{diag}(\mu_1,\mu_2)R(c,s)^T\)、\(c^2+s^2=1\)
   对 `11` 个 canonical classes 生成 proof-obligation scaffold。当前 closed faces
   为 coordinatewise / scaled-rank-one / rank-one projector 相关 faces；open faces
   为 `m_rank_one_n_full`、`m_full_n_rank_one` 和 `n_isotropic_m_rotated`。该 scaffold
   不是 full-rank theorem。
10. `L3-2f-mixed-boundary-faces`：Stage 4A 已将两个 mixed codim-1 faces
    做成 exact symbolic scaffold。`m_full_n_rank_one` 的 `11/11` canonical words
    都有 product rank upper bound `<=2`，所以可优先走 `Jmid` 的 exterior-square
    trace route；`m_rank_one_n_full` 中 `L3C08/L3C09/L3C10/L3C11` 没有这个
    rank shortcut，已由 Stage 4C 的 cubic Schur 证书单独处理。
11. `L3-2g-m_full_n_rank_one`：Stage 4B 已闭合当前参数化下的
    `m_full_n_rank_one` face。该 face 上 product rank `<=2`，非零 characteristic
    factor 降为二次，三个 Schur margins `1-e1+e2`、`1+e1+e2`、`1-e2`
    全部由 exact Bernstein 证书闭合。该结论不是 full-rank interior theorem。
12. `L3-2h-m_rank_one_n_full`：Stage 4C 已闭合当前参数化下的
    `m_rank_one_n_full` face。该 face 中四个 hard-rank classes
    `L3C08/L3C09/L3C10/L3C11` 不能降为二次 factor；本节点用 principal minors
    计算 \(e_1,e_2,e_3\)，并对完整 cubic Schur/Jury margins 做 exact Bernstein
    证书，`11/11` canonical classes 全部闭合。该结论仍不是 full-rank interior theorem。
13. `L3-2i-n_isotropic_m_rotated`：Stage 4D 已闭合当前参数化下的
    `n_isotropic_m_rotated` face。该 face 中 \(N=\nu I\)，但 active-mask signs
    仍与 rotated \(M\) 交互，所以不能简单归入 coordinatewise case。本节点用完整
    cubic Schur/Jury margins 和 exact Bernstein 证书闭合 `11/11` canonical classes；
    只有 `L3C08/Jplus` 使用 depth-1 dyadic Bernstein。该结论仍不是 full-rank
    interior theorem。
14. `L3-2j-full-rank-interior-assembly`：Stage 4G 已闭合 full-rank 参数盒上的
   全部 `11*5=55` 个 length-3 cubic Schur/Jury margins。`51` 个 margins 一盒
   Bernstein 直接闭合，`L3C01:Jminus`、`L3C03:Jminus`、`L3C08:Jplus`、
   `L3C10:Jplus` 由 depth-1 dyadic Bernstein repair 闭合。该结论由
   `proof_reviews/stage4_full_rank_interior_margin_assembly/` 接受为
   `accepted_by_review`。
15. `L3-3`：并行尝试 common seminorm：寻找半正定 \(H\) 使相关 quotient maps 在同一
   \(H\)-seminorm 下非扩张。若存在，任意 switching 会比逐个 length-3 更强。
16. `L3-4`：二维 length-3 reduced-product theorem 已闭合；下一步进入 arbitrary
   switching / common seminorm，或寻找更高维 active-mask counterexample pressure。

## 5. 本轮边界

当前新增内容推进到了 rank-one projector projective boundary exact artifact，并闭合了
`11/11` 个 boundary classes，包括 projective infinity closure；scaled rank-one
已生成 exact scaffold，并通过 \(S,u\) batch certificate 闭合了 `L3C02` 与
`L3C07`，通过非对称判别式证书闭合了 `L3C11`，又通过 parity 证书闭合了
`L3C05`。`L3C03` 与 `L3C01` 又由 depth-1 dyadic 与 `a=b` 三角化 Bernstein
证书闭合；`L3C08` 由 cubic parity/Bernstein 证书闭合。当前 scaled-rank-one
canonical classes 已 `11/11` 闭合。它仍不是完整 `L3-2c` theorem，也不是
`candidate_counterexample`。
已有 numerical screens 仍只能说明当前候选没有短周期证书；不能把它们改写成严格反例不存在。

## 6. Stage 4 full-rank interior scaffold 更新

Stage 4 已新增：

```text
experiments/breakthrough/analyze_length3_full_rank_interior_scaffold.py
outputs/breakthrough_attempts/stage4_full_rank_interior/full_rank_interior_scaffold.md
outputs/breakthrough_attempts/stage4_full_rank_interior/full_rank_interior_scaffold.json
notes/breakthrough_routes/stage4_full_rank_interior_route.md
```

该 scaffold 只生成 full-rank interior 的 proof obligations。它记录到 full 5D
interior 的 Schur/Jury margins 即使不展开也已有最高 `93917` 的 operation count，
因此当前路线先处理 mixed boundary faces：

```text
m_rank_one_n_full
m_full_n_rank_one
n_isotropic_m_rotated
```

当前两个 mixed codim-1 faces 已由 Stage 4B/4C 闭合，`n_isotropic_m_rotated`
已由 Stage 4D 闭合。随后 Stage 4G 已闭合 full-rank 参数盒的全部 length-3
Schur/Jury margins，因此二维 noncommuting length-3 reduced-product theorem 已在该
局部谱意义下闭合。

## 7. Stage 4A mixed boundary faces 更新

新增 mixed boundary face scaffold：

```text
outputs/breakthrough_attempts/stage4_full_rank_interior/mixed_boundary_faces.md
```

关键结构发现：

- `m_full_n_rank_one`：`11/11` 个 canonical words 有 product rank `<=2` shortcut；
- `m_rank_one_n_full`：`7/11` 个 canonical words 有 product rank `<=2` shortcut；
- `m_rank_one_n_full` 的 `L3C08/L3C09/L3C10/L3C11` 是没有单步 rank shortcut 的
  hard classes。

Stage 4B/4C 已分别闭合这两个 mixed faces，Stage 4D 已闭合
`n_isotropic_m_rotated`。下一步应转向 full 5D interior lift，而不是重复处理
boundary faces。

## 8. Stage 4B m_full_n_rank_one 更新

当前参数化下的 `m_full_n_rank_one` face 已闭合：

```text
outputs/breakthrough_attempts/stage4_full_rank_interior/m_full_n_rank_one_quadratic_schur_certificate.md
```

证明结构：

- \(N=\operatorname{diag}(\nu_1,0)\)，
  \(M=R(c,s)\operatorname{diag}(\mu_1,\mu_2)R(c,s)^T\)；
- product rank `<=2`，非零 characteristic factor 降为二次；
- 三个二次 Schur margins `1-e1+e2`、`1+e1+e2`、`1-e2` 全部 exact Bernstein 非负；
- `L3C08/L3C10` 的 `quadratic_Jplus` 使用 depth-1 dyadic Bernstein，其余 margins
  one-box 闭合。

## 9. Stage 4C m_rank_one_n_full 更新

当前参数化下的 `m_rank_one_n_full` face 已闭合：

```text
outputs/breakthrough_attempts/stage4_full_rank_interior/m_rank_one_n_full_cubic_schur_certificate.md
```

证明结构：

- \(M=R(c,s)\operatorname{diag}(\mu_1,0)R(c,s)^T\)，
  \(N=\operatorname{diag}(\nu_1,\nu_2)\)；
- `L3C08/L3C09/L3C10/L3C11` 没有 product-rank `<=2` shortcut；
- 直接用 principal minors 计算 \(e_1,e_2,e_3\)，避免 `trace(P**3)` 大展开；
- 五个 cubic Schur/Jury margins 全部 exact Bernstein 非负；
- `L3C01/L3C03/L3C08/L3C10` 使用 depth-1 dyadic Bernstein，其余 margins
  one-box 闭合。

## 10. Stage 4D n_isotropic_m_rotated 更新

当前参数化下的 `n_isotropic_m_rotated` face 已闭合：

```text
outputs/breakthrough_attempts/stage4_full_rank_interior/n_isotropic_m_rotated_cubic_schur_certificate.md
```

证明结构：

- \(N=\nu I\)，
  \(M=R(c,s)\operatorname{diag}(\mu_1,\mu_2)R(c,s)^T\)；
- active-mask signs 仍与 rotated \(M\) 交互，因此保留完整 cubic factor；
- 直接用 principal minors 计算 \(e_1,e_2,e_3\)；
- 五个 cubic Schur/Jury margins 全部 exact Bernstein 非负；
- 只有 `L3C08/Jplus` 使用 depth-1 dyadic Bernstein，其余 margins one-box 闭合。

至此 Stage 4 scaffold 中显式列出的三个 boundary faces 均已闭合。

## 11. Stage 4G full-rank all-margin assembly 更新

full-rank 参数盒上的全部 length-3 margins 已闭合：

```text
outputs/breakthrough_attempts/stage4_full_rank_interior/full_rank_interior_all_margin_dyadic_depth1_assembly.md
proof_reviews/stage4_full_rank_interior_margin_assembly/
```

证明结构：

- \(N=\operatorname{diag}(\nu_1,\nu_2)\)，
  \(M=R(c,s)\operatorname{diag}(\mu_1,\mu_2)R(c,s)^T\)，\(c^2+s^2=1\)；
- 使用 \(c^2=t,s^2=1-t\) 把三角约束化为盒约束；
- 对每个 canonical word 计算 \(e_1,e_2,e_3\)，再用稀疏系数字典组合
  `Jplus/Jminus/Jmid/Jconst_upper/Jconst_lower`；
- `55/55` margins 闭合，其中 `51` 个 one-box Bernstein，`4` 个 depth-1 dyadic
  Bernstein repair；
- proof review verdict 为 `correct`，acceptance gate 为 `accepted_by_review`。

由 determinant-zero lemma 与 cubic Schur/Jury criterion，可得二维 reduced active-set
length-3 非恒定 products 的局部 spectral nonexpansion。剩余开放义务已经转为
arbitrary switching、common seminorm / path-complete Lyapunov，或更高维
proof-grade counterexample route。

## 12. Stage 5 arbitrary switching gate 更新

Stage 5 已把 Stage 4G 之后的 arbitrary switching 问题改写为 length-2 memory
graph 上的 proof-obligation scaffold：

```text
experiments/breakthrough/build_stage5_arbitrary_switching_gate.py
outputs/breakthrough_attempts/stage5_arbitrary_switching/arbitrary_switching_gate.md
outputs/breakthrough_attempts/stage5_arbitrary_switching/arbitrary_switching_gate.json
notes/breakthrough_routes/stage5_arbitrary_switching_gate.md
```

枚举结果：

```text
node_count = 16
transition_count = 64
nonconstant_transition_count = 60
constant_self_loop_count = 4
stage4g_covered_nonconstant_transition_count = 60
stage4g_uncovered_nonconstant_transition_count = 0
```

因此 Stage 4G 已覆盖所有非恒定三步窗口；没有剩余的 length-3 Schur/Jury margin
义务。新的开放义务是：

- `AS-1`：构造或排除 length-2 memory path-complete seminorm；
- `AS-2`：处理四条 constant self-loop windows 的 fixed-mask cone/admissibility；
- `AS-3`：寻找 finite-window theorem 到 arbitrary switching 的 semigroup /
  active-cone composition lemma；
- `AS-4`：若走反例路线，必须给出 exact expansion、active-region inequalities 和
  slack-QP embedding。

该 gate 不是 arbitrary switching theorem；它只把 Stage 4G 之后还缺的桥接结构
精确列出来。
