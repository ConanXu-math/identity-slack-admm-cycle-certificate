# Slack-variable 三块 ADMM 当前研究笔记

状态：`pause_summary`

> 2026-07-14 source-of-truth 更新：一般无条件收敛问题已被严格 66 周期反例否定。完整结论、
> 精确 QP 数据、双实现复算和 claim boundary 见
> `report/final_resolution_2026-07-14.md`。本文中较早的“当前没有严格反例”段落仅保留为研究历史，
> 均由文末终点覆盖。

这份笔记只围绕一个问题：

```text
把两块不等式约束问题改写成带 slack variable 的 [A,B,I] 三块等式约束后，
直接三块 ADMM 是否因为 identity/slack/projection 结构而收敛？
如果现在还不能证明，反例搜索到底走到了哪里？
```

当前总判断是：

```text
原始 direct slack-variable 三块 ADMM 的无条件全局收敛命题：已被 exact 66-cycle 否定。
反例范围：A=B=I_2、beta=1、两个目标均为零线性项的纯强凸二次函数。
反例性质：bounded periodic nonconvergence；不声称 iterates 无界。
证据：Stage 44 signed-state exact checker + Stage 45 full-state raw-ADMM 第二实现。
外部复核：尚无；当前只能写“仓库内两套 exact 实现交叉验证”。
正向结果：已有 phase/common-metric/small-gain/标量/对角等条件收敛定理，均不受反例否定。
下一问题：刻画排除 66-cycle 机制的最小附加条件，或研究 corrected algorithm。
```

### 当前 proof-grade 好消息

**第一类：active-set 谱证书比上次推进很多。** length-2 nonconstant switching 已经是局部 theorem。length-3 先后闭合了 coordinatewise、rank-one projector boundary、scaled-rank-one `11/11` classes；随后 Stage 4 继续到 full-rank 参数化，三个关键边界面都已闭合，最后 `11` 个 canonical classes 的 `55` 个 cubic Schur/Jury margins 全部闭合：

```text
51 个 margins：one-box Bernstein
4 个 margins：depth-1 dyadic repair
review status：accepted
```

这说明二维 full-rank length-3 legacy product 线已经不是当前阻塞点。真正的阻塞已经后移到真实 source-target switching、admissibility、cone-restricted metric 和 arbitrary switching。

**第二类：phase-dependent Lyapunov 已经给出原始 direct ADMM 的非平凡正向定理。** 固定

\[
A=B=I,\qquad b=0,\qquad \beta=1,
\]

通过四个 phase-dependent 对角矩阵 \(H_b\)，已得到以下独立复核接受的结论：

1. 固定 QP：\(Q_1=3I\)、\(Q_2=\begin{psmallmatrix}7&4\\4&3\end{psmallmatrix}\)。
2. 一参数族：\(Q_1=aI\)、\(a\in[1,7/2]\)，其余参数固定。
3. 二参数盒：\(Q_2=\begin{psmallmatrix}7&q\\q&r\end{psmallmatrix}\)，
   \(q\in[79/20,81/20]\)、\(r\in[59/20,61/20]\)。
4. 联合三参数盒：\(a\in[119/40,121/40]\) 与上述 \((q,r)\) 盒同时变化。
5. 更高维 reduced 邻域：对称 \(M,N\) 分别位于 \(M_0,N_0\) 的谱范数半径
   \(1/500\) 内时，16 条 edge residual 有统一严格余量
   \(483261/80000000\)。

这些结论使用 exact Rational 主子式或 tensor Bernstein 证书，不是 numerical screen。
它们证明 direct slack ADMM 在一个非平凡开放 QP 邻域内收敛，但仍不能外推为一般模型定理。

**第三类：common-metric / Selector-IQC / signed-PWA 分支补出了新的充分条件。**

- 任意有限维强凸二次 reduced recurrence 已有 block small-gain sufficient condition；满足显式比较矩阵条件时，存在 common metric 并给出严格收缩。
- Selector-IQC 把指数级 mask norm 枚举替换成一个对角乘子 LMI；对角 \(G\) 情形还有无损刻画，非正规 \(G\) 的鲁棒邻域也已有 exact 见证。
- small-gain gate 外，已经构造一个固定二维 QP 的 signed-PWA 全局几何收敛定理；同一结构扩展到任意 rhs、一次项和一个 reduced Hessian 开放邻域，收缩常数为 \(99/100\)。
- 任意维 signed-PWA common-metric theorem 已闭合为条件定理：只要全部 signed branches 共用 \(H\)-Lipschitz 常数 \(\gamma<1\)，则任意 affine 数据和有限初值全局几何收敛。

这些都是原始 direct ADMM 的正向充分条件，不是修正算法定理；但它们仍不是“所有 \([A,B,I]\) 实例都收敛”的全局证明。

**第四类：反例端也有好消息。** 多条候选反例路线已经变成 exact no-go gate：fixed-mask positive outward ray 被排除；固定有理 QP 的很多短 closed words 被 exact admissibility / Farkas gate 排除；Hamiltonian length-4 的三个等价类也完成了单位根面与 strict-row violation 分析。当前仍没有 proof-grade strict counterexample。

**第五类：嵌套 mask 周期的前沿已经压缩。** 最短 nested-mask 二周期 `01 -> 11 -> 01` 及其坐标交换已经由 exact determinant 下界排除。三周期方面，coordinatewise 子族已闭合；一般非交换情形的 Cayley reduction 已证明四个端点 \(E_{11},E_{01},E_{10},E_{00}\) 全部严格为正，因此仅经过 `01`/`11` 的非恒定三周期也已排除。最后的 \(E_{00}\) 使用零点必要条件 \(L-r=3/14\) 与统一下界 \(L-r\ge7/32\) 的严格间隙闭合。当前 blocker 已后移到 length \(\ge4\) 的 fractional-selector products、真实 itinerary cone 或 phase metric。

四周期现已有精确双核门：零和算子与四步闭合算子必须具有非零共同核。真实 binary
itinerary 又压成六个循环类；交替类的 selector 满足 $r_0r_2=r_1r_3$，而四步乘积的
fractional 扰动落在至多四维 Krylov 通道。共同核尚未排除，所以这些只是 verified reductions，
不是四周期无轨道定理。

## 问题背景

原始问题是

\[
\min\{\theta_1(x)+\theta_2(y)\mid Ax+By\le b,\ x\in X,\ y\in Y\}.
\]

引入 slack variable \(z\ge0\) 后，得到

\[
\min\{\theta_1(x)+\theta_2(y)+0(z)
\mid Ax+By+z=b,\ x\in X,\ y\in Y,\ z\in\mathbb R_+^m\}.
\]

约束矩阵变成三块结构

\[
[A,B,I].
\]

这不是普通两块 ADMM，也不是完全一般的三块 ADMM。它的特殊性在于第三块是 identity，且 \(z\)-step 是显式投影。研究的核心就是：这个投影结构能否弥补一般直接三块 ADMM 的不稳定性。

本仓库使用的增广拉格朗日符号是

\[
{\cal L}_\beta
=\theta_1(x)+\theta_2(y)
-\lambda^\top r
+\frac{\beta}{2}\|r\|^2,
\qquad
r=Ax+By+z-b.
\]

所以乘子更新为

\[
\lambda^{k+1}=\lambda^k-\beta r^{k+1}.
\]

若采用常见的 \(+\mu^\top r\) 记号，则 \(\mu=-\lambda\)。因此在当前符号下，active constraint 上的 \(\lambda_i\le0\)，常见非负不等式乘子是 \(\mu_i\ge0\)。

直接三块 ADMM 是

\[
x^{k+1}\in\arg\min_{x\in X}{\cal L}_\beta(x,y^k,z^k,\lambda^k),
\]

\[
y^{k+1}\in\arg\min_{y\in Y}{\cal L}_\beta(x^{k+1},y,z^k,\lambda^k),
\]

\[
z^{k+1}\in\arg\min_{z\ge0}{\cal L}_\beta(x^{k+1},y^{k+1},z,\lambda^k),
\]

\[
\lambda^{k+1}
=\lambda^k-\beta(Ax^{k+1}+By^{k+1}+z^{k+1}-b).
\]

下面分两部分：第一部分写理论推导和卡点；第二部分写反例搜索和实验设置。

## 第一部分：理论推导

### I.1 投影恒等式

固定 \(x^{k+1},y^{k+1},\lambda^k\)，令

\[
q^{k+1}=b-Ax^{k+1}-By^{k+1}+\lambda^k/\beta.
\]

\(z\)-子问题中与 \(z\) 有关的项是

\[
-\lambda^{k\top}z
+\frac{\beta}{2}\|Ax^{k+1}+By^{k+1}+z-b\|^2
+I_{\mathbb R_+^m}(z).
\]

配方得到

\[
\frac{\beta}{2}\|z-q^{k+1}\|^2+I_{\mathbb R_+^m}(z)+\text{constant}.
\]

所以

\[
z^{k+1}=\Pi_{\mathbb R_+^m}(q^{k+1}).
\]

再由残差更新

\[
\lambda^{k+1}=\lambda^k-\beta r^{k+1}
\]

得到

\[
\lambda^{k+1}=\beta(q^{k+1}-z^{k+1}).
\]

投影最优性给出

\[
q^{k+1}-z^{k+1}\in N_{\mathbb R_+^m}(z^{k+1}),
\]

因此

\[
\lambda^{k+1}\in \beta N_{\mathbb R_+^m}(z^{k+1}).
\]

坐标上，在当前 \(\lambda\) 符号下：

\[
z_i^{k+1}>0\Rightarrow \lambda_i^{k+1}=0,
\qquad
z_i^{k+1}=0\Rightarrow \lambda_i^{k+1}\le0.
\]

这一部分是确定的 theorem 级代数事实。

### I.2 \(x,y\) 最优性变成 lag-error VI

记

\[
\Delta x^{k+1}=x^{k+1}-x^k,\quad
\Delta y^{k+1}=y^{k+1}-y^k,\quad
\Delta z^{k+1}=z^{k+1}-z^k.
\]

\(y\)-step 的一阶最优性为

\[
0\in
\partial\theta_2(y^{k+1})+N_Y(y^{k+1})
-B^\top\lambda^k
+\beta B^\top(Ax^{k+1}+By^{k+1}+z^k-b).
\]

由于

\[
Ax^{k+1}+By^{k+1}+z^k-b
=r^{k+1}-\Delta z^{k+1},
\]

且

\[
\lambda^k=\lambda^{k+1}+\beta r^{k+1},
\]

代入后得到

\[
0\in
\partial\theta_2(y^{k+1})+N_Y(y^{k+1})
-B^\top\lambda^{k+1}
-\beta B^\top\Delta z^{k+1}.
\]

也就是说，\(y\)-block 相对 KKT 多出的 lag error 是

\[
-\beta B^\top\Delta z^{k+1}.
\]

同理，\(x\)-step 的一阶最优性为

\[
0\in
\partial\theta_1(x^{k+1})+N_X(x^{k+1})
-A^\top\lambda^k
+\beta A^\top(Ax^{k+1}+By^k+z^k-b).
\]

而

\[
Ax^{k+1}+By^k+z^k-b
=r^{k+1}-B\Delta y^{k+1}-\Delta z^{k+1}.
\]

代入 \(\lambda^k=\lambda^{k+1}+\beta r^{k+1}\)，得到

\[
0\in
\partial\theta_1(x^{k+1})+N_X(x^{k+1})
-A^\top\lambda^{k+1}
-\beta A^\top(B\Delta y^{k+1}+\Delta z^{k+1}).
\]

所以 \(x\)-block 的 lag error 是

\[
-\beta A^\top(B\Delta y^{k+1}+\Delta z^{k+1}).
\]

这一步不是失败点。它说明 direct three-block Gauss-Seidel 顺序带来的误差可以精确写成 \(\Delta y,\Delta z\) 的组合。真正的问题是：这些误差能否被某个下降函数吸收。

### I.3 候选 Lyapunov 与理想下降

尝试的候选能量是

\[
\Phi_k =
\frac{1}{\beta}\|\lambda^k-\lambda^\star\|^2
+\beta\|B(y^k-y^\star)+z^k-z^\star\|^2
+c\beta\|\Delta z^k\|^2
+d\beta\|B\Delta y^k\|^2.
\]

理想目标是证明存在 \(\alpha_i>0\)，使

\[
\Phi_k-\Phi_{k+1}
\ge
\alpha_1\|r^{k+1}\|^2
+\alpha_2\|B\Delta y^{k+1}\|^2
+\alpha_3\|\Delta z^{k+1}\|^2.
\]

若该式成立，就能得到 residual 与相邻差分可求和。再加上 rank、compactness、error bound 或强凸性之类条件，才可能继续推收敛。

当前这个下降式没有闭合。

### I.4 Lyapunov 线卡住的具体位置

先展开 dual energy。由

\[
\lambda^k-\lambda^{k+1}=\beta r^{k+1}
\]

得

\[
\frac1\beta
\left(
\|\lambda^k-\lambda^\star\|^2
-\|\lambda^{k+1}-\lambda^\star\|^2
\right)
=
2\langle \lambda^{k+1}-\lambda^\star,r^{k+1}\rangle
+\beta\|r^{k+1}\|^2.
\]

又因为可行点满足 \(Ax^\star+By^\star+z^\star=b\)，

\[
r^{k+1}
=A(x^{k+1}-x^\star)
+B(y^{k+1}-y^\star)
+z^{k+1}-z^\star.
\]

\(z\)-块可以由 normal cone 单调性处理：

\[
\lambda^{k+1}\in\beta N_{\mathbb R_+^m}(z^{k+1}),\qquad
\lambda^\star\in\beta N_{\mathbb R_+^m}(z^\star).
\]

因此 \(z\)-部分给出可用的非正项。问题出在 \(x,y\)-块。它们不是纯 KKT 单调性，因为一阶条件里有 lag errors：

\[
-\beta A^\top(B\Delta y^{k+1}+\Delta z^{k+1}),
\qquad
-\beta B^\top\Delta z^{k+1}.
\]

把这些项和 dual energy 拼起来，核心残留项就是

\[
\beta\langle B\Delta y^{k+1},\Delta z^{k+1}\rangle.
\]

这个项无定号。

**尝试一：用连续两步 \(y\)-最优性 telescoping。**

把 \(y^{k+1}\) 与 \(y^k\) 的最优性相减，确实会产生一些 \(\|B\Delta y^{k+1}\|^2\) 型项。但旧步的 \(z^k,z^{k-1}\) 与 \(\lambda^k,\lambda^{k-1}\) 又被带回来，最终仍留下与

\[
\langle B\Delta y^{k+1},\Delta z^{k+1}\rangle
\]

同阶的无定号项。它没有自然整理成 \(\Phi_k-\Phi_{k+1}\) 里的非负 telescoping 结构。

**尝试二：用 projection firm nonexpansiveness 控制 \(\Delta z\)。**

投影 FNE 给出

\[
\|\Delta z^{k+1}\|^2
\le
\langle \Delta z^{k+1},q^{k+1}-q^k\rangle.
\]

但是

\[
q^{k+1}-q^k
=
-A\Delta x^{k+1}
-B\Delta y^{k+1}
+(\lambda^k-\lambda^{k-1})/\beta.
\]

所以

\[
\|\Delta z^{k+1}\|^2
\le
-\langle \Delta z^{k+1},A\Delta x^{k+1}\rangle
-\langle \Delta z^{k+1},B\Delta y^{k+1}\rangle
+\frac1\beta
\langle \Delta z^{k+1},\lambda^k-\lambda^{k-1}\rangle.
\]

FNE 是有效入口，但它没有单独给出 \(\|\Delta z\|^2\) 的净下降；它把 \(A\Delta x\)、\(B\Delta y\)、\(\Delta\lambda\) 全带回来了。

**尝试三：Young inequality 吸收坏项。**

形式上可以写

\[
\beta|\langle B\Delta y^{k+1},\Delta z^{k+1}\rangle|
\le
\frac{\eta\beta}{2}\|B\Delta y^{k+1}\|^2
+\frac{\beta}{2\eta}\|\Delta z^{k+1}\|^2.
\]

但这要求下降式里已经有足够强的

\[
\|B\Delta y^{k+1}\|^2,\qquad \|\Delta z^{k+1}\|^2
\]

正项，并且系数能统一压过 \(\eta\) 与 \(1/\eta\)。在当前 base assumptions 下，这些正项来源不够；固定 \(c,d\) 也没有证明能全局吸收。

**尝试四：即使形式下降成立，还缺 coercivity。**

\[
\|B(y^k-y^\star)+z^k-z^\star\|
\]

并不自动控制 \(y^k\) 与 \(z^k\) 各自的距离。若要从下降推出变量收敛，还需要 rank、error bound、compactness、强凸性等额外条件。

因此当前只能说：

```text
projection identity and FNE are valid ingredients,
but projection-only Lyapunov proof is incomplete.
```

不能说：

```text
slack-variable [A,B,I] direct three-block ADMM converges.
```

### I.5 从 Lyapunov 转向 active-set 局部理论

转向 active-set 不是换话题，而是因为 Lyapunov 展开已经指出困难来自 \(B\Delta y\) 与 \(\Delta z\) 的耦合。如果 \(z\)-projection 的分段线性结构能提供额外稳定性，固定一个投影分支后应该能在局部线性动力系统中看出来。

代码中的 mask \(D=\operatorname{diag}(d_i)\) 记录的是 projection derivative：

- \(d_i=1\)：\(q_i>0\)，所以 \(z_i=q_i\)；
- \(d_i=0\)：\(q_i\le0\)，所以 \(z_i=0\)。

固定 \(D\) 后，

\[
z^{k+1}=Dq^{k+1},\qquad
\lambda^{k+1}=\beta(I-D)q^{k+1}.
\]

于是一步后自动满足

\[
z_{D=0}^{k+1}=0,\qquad \lambda_{D=1}^{k+1}=0.
\]

先写 full-state affine map。对无额外集合约束的凸二次 slack QP，令

\[
H_x=Q_1+\beta A^\top A,\qquad
H_y=Q_2+\beta B^\top B.
\]

固定 \(D\) 时，

\[
x^{k+1}=H_x^{-1}\left(A^\top\lambda^k-\beta A^\top(By^k+z^k-b)\right),
\]

\[
y^{k+1}=H_y^{-1}\left(B^\top\lambda^k-\beta B^\top(Ax^{k+1}+z^k-b)\right),
\]

\[
q^{k+1}=b-Ax^{k+1}-By^{k+1}+\lambda^k/\beta.
\]

由于 \(x^{k+1}\) 不依赖旧 \(x^k\)，有效状态可以取

\[
v^k=(y^k,z^k,\lambda^k),
\]

并写成

\[
v^{k+1}=T_Dv^k+c_D.
\]

再进一步消去一步后必为零的互补 bookkeeping 分量。定义

\[
u=z-\lambda/\beta.
\]

在固定 \(D\) 的互补 manifold 上，

\[
z=Du,\qquad \lambda=-\beta(I-D)u.
\]

于是 reduced state 是 \((y,u)\)。令

\[
M_x=\beta A(Q_1+\beta A^\top A)^{-1}A^\top,\qquad
N_y=\beta B(Q_2+\beta B^\top B)^{-1}B^\top,
\]

\[
S_D=2D-I.
\]

则

\[
\begin{pmatrix}\delta y^+\\ \delta u^+\end{pmatrix}
=R_D
\begin{pmatrix}\delta y\\ \delta u\end{pmatrix},
\]

其中

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

非零谱满足

\[
\sigma(T_D)\setminus\{0\}=\sigma(R_D)\setminus\{0\}.
\]

所以 fixed-mask 反例搜索可以转化为 reduced map 的谱问题。

若 \(M_x,N_y,D\) 可同时对角化，每个坐标拆成 \(2\times2\) 小块。active branch 的特征值是 \(\{m,n\}\)，inactive branch 的非零特征值是

\[
mn+(1-n)(1-m).
\]

它们都在 \([0,1]\) 内。因此 commuting / coordinatewise 情形不会扩张。退不下去的位置是非交换情形：\(D\) 与 \(M_x,N_y\) 不必交换，而新的风险项正是

\[
S_D\{N_y+(I-N_y)M_x-(I-D)\}.
\]

接下来做了两层搜索。

第一层是抽象 reduced-map screen：直接随机生成 \(0\preceq M_x,N_y\preceq I\)，在维度 \(2,3,4\)、每个设置 `5000` 次 trial、seed `20260705` 下枚举 mixed masks。总 evaluations 为 `110000`，最大谱半径为 `0.9997018793790761`，没有发现扩张。但对二维 mixed mask `[1,0]` 直接优化 \(\rho(R_D)\) 后得到

```text
optimized spectral radius: 1.002263982483121
```

这说明非交换 reduced map 确实有扩张压力。

第二层是把这个压力嵌回真实凸二次 QP。取 \(A=B=I,\beta=1\)，反解出对应 \(Q_1,Q_2\)，并搜索右端项和固定点位置。得到

```text
fixed-active spectral radius: 1.0022626303042794
expanding eigenvalues: 2
top eigenvalue: 0.9999729077043129 + 0.06770940822244995i
fixed point active-region margin: 0.012718057300436302
```

小扰动在有限步内确实能保持同一 mask：`1e-8`、`1e-6`、`1e-4` 在 `2000` 步内没离开；`1e-3`、`1e-2` 会离开。

这看起来像反例，但还不是 proof-grade counterexample。问题在 invariant step。对扰动 \(e_k=T_D^ke_0\)，active-region 条件是

\[
s\odot(q^\star+Le_k)>0.
\]

top unstable eigenvalue 是复数 \(\eta=\rho e^{i\theta}\)，并且 signed-\(q\) functional 对不稳定子空间可见。因此某个坐标中出现

\[
\rho^k\operatorname{Re}(ce^{ik\theta}).
\]

它会振荡变号并且幅度增长。更长的 stay check 也验证了这一点：`1e-4`、`1e-5`、`1e-6` 的实扰动分别在第 `2296`、`3318`、`4340` 步离开 fixed mask。

于是又专门搜索两类可能支持 fixed-mask 严格反例的结构：

1. 正实扩张特征值 \(\eta>1\)，且 signed-\(q\) margin 沿 eigenray 不变号；
2. 复扩张特征值，但 signed-\(q\) functional 在不稳定子空间上为零，也就是切向扩张。

在维度 \(2,3,4\)、三类随机族、每类 `1000` 次 trial、seed `20260706` 的搜索中，总 evaluations 为 `66000`。出现过扩张记录，最大谱半径为 `1.0079349219063447`，但 candidate mode count 为 `0`；最强扩张仍是 `complex_rotating_visible_to_signed_q`。

进一步直接优化 signed-\(q\) tangent 条件，权重取 `1.0, 0.05, 0.001`，都退到无扩张边界：

```text
spectral radius: 0.9999993332494114
expanding mode count: 0
```

这些现象被整理成 fixed-mask invariant impossible 的证明尝试：

- 可见复扩张会因 \(\rho^k\operatorname{Re}(ce^{ik\theta})\) 振荡离开 active region；
- 负实扩张会交替变号；
- signed-\(q\) tangent expansion 若存在，则由
  \[
  S_Dq^+=u^+=\eta w_u
  \]
  得 \(w_u=0\)，于是 eigenproblem 退化到
  \[
  \eta w_y=\beta H_y^{-1}B^\top M_xB w_y,
  \]
  该块没有 \(|\eta|>1\)；
- 正实扩张 \(\eta>1\) 可由 contraction lemma 排除。核心工具是 \(0\preceq C\preceq I\) 时
  \[
  Cv=t\Rightarrow \|t\|^2\le\langle v,t\rangle.
  \]

将该引理分别用于 \(M\) 与 \(N\)，最终得到

\[
(1-2\eta)\langle\gamma,n\rangle
\ge
\eta(\eta-1)
\left(
\|\alpha\|^2+\|p\|^2+\|\gamma\|^2+\|n\|^2
\right).
\]

当 \(\eta>1\) 时只能推出所有分量为零，与非零 eigenvector 矛盾。

结论：fixed-mask 单段反例路线目前被大幅压缩。有非交换扩张压力，但还没有能全时留在同一 active region 的严格反例。困难自然转向 active-set switching。

### I.6 length-2 switching

fixed-mask 受阻后，下一步尝试 active-set switching。最小非平凡对象是 length-2 nonconstant product：

\[
P_{D_0,D_1}=R_{D_1}(M,N)R_{D_0}(M,N),\qquad D_0\ne D_1.
\]

二维 reduced active-set 模型中有 `12` 个 ordered nonconstant pairs。最开始的目标是找 \(\rho(P)>1\)。结果没有找到，反而逐步转成了局部定理。

第一步是 exact determinant check：

\[
\det(P_{D_0,D_1})=0
\]

对全部 `12` 个 pair 成立。但这只给一个零特征值，不控制剩余 cubic factor。

第二步是对称性归约。坐标置换把 `[1,0]` 和 `[0,1]` 互相化简；顺序反转不改变非零谱。这把 `12` 个 ordered pairs 压成四类：

```text
zero_single
zero_full
single_single
single_full
```

第三步是逐类证明。过程大致是：

- `zero_full` 降成二次 margins；
- `zero_single` 中的困难集中在 `Qplus` 和 `Qconst_minus`，曾经出现很多 bad Bernstein coefficients，但这些只是 certificate failure，不是负值 witness；
- `single_single` 最重，`Jplus` 需要 top-slice / corner-reserve lift，`Jmid` 需要 parity gate 和 exact Bernstein certificate；
- `single_full` 用 full two-angle 参数化和 exact Bernstein certificates 处理 cubic margins。

最终四类合起来覆盖全部 `12` 个 ordered pairs，无 missing、extra 或 duplicate cases。可声明的精确局部定理是：

```text
在二维 reduced active-set 模型中，
全部 12 个 length-2 nonconstant active-mask ordered pair products 的非零谱位于闭单位圆内。
```

这条线现在退不下去的位置不是 length-2，而是从 length-2 往任意 switching 外推。因为该结果是 product-by-product 的谱结论，不给共同 seminorm；并且边界上确实存在 \(\rho=1\)，不能加强成 uniform strict contraction。因此不能推出：

- length-3 非扩张；
- arbitrary switching 非扩张；
- joint spectral radius 不超过 1；
- common Lyapunov seminorm 存在；
- 原始 direct slack-variable ADMM 全局收敛。

### I.7 length-3 switching

先尝试过一个自然捷径：既然全部 length-2 nonconstant products 都不扩张，能不能推出 length-3 也不扩张？不能。原因是没有共同 seminorm。线性代数中存在全部 pair products 谱半径不超过 `1`，但 triple product 谱半径大于 `1` 的例子。这个例子不属于当前 \(R_D\) 结构，但足以说明逻辑外推无效。

于是 length-3 改成 exact scaffold。

第一步枚举非恒定 length-3 words。共有 `60` 个。按 cyclic shift 和二维坐标交换归约后得到 `11` 个 canonical classes，其中 `7` 个含 adjacent repeat，`4` 个由三个不同 masks 组成且没有相邻重复。这里没有使用 reversal spectral equivalence，所以不能再压缩。

第二步是 determinant-zero lemma。单步 determinant 只有 full mask `[1,1]` 可能非零；任意非恒定 length-3 word 至少含一个 non-full mask，因此

\[
\det(R_{D_2}R_{D_1}R_{D_0})=0.
\]

这只去掉一个零根，不控制剩余 cubic factor。

第三步提取剩余 cubic factor。写

\[
\det(tI-P)=t(t^3+a_1t^2+a_2t+a_3),
\]

其中

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

这一步得到了 exact symbolic objects，但表达式巨大：最大 `len(a3)=161665`、`ops(a3)=29691`。直接人工展开已经不可行。

第四步构造 Schur/Jury margins：

\[
J_+=1+a_1+a_2+a_3,\qquad
J_-=1-a_1+a_2-a_3,
\]

\[
J_{\rm mid}=1-a_2+a_1a_3-a_3^2,\qquad
J_{\rm const}: 1+a_3,\ 1-a_3.
\]

最大 `Jmid` 长度达到 `347008`、operation count `63734`。这说明“把所有 margin 展开然后读非负性”这条路走不下去，必须找结构。

随后分子族处理。

**Coordinatewise / commuting 子情形。** 若 \(M,N,D_j\) 可同时对角化，每个坐标只需分析 active/inactive 两个 \(2\times2\) block。八种 scalar length-3 words 的 Schur margins 全部有非负 Bernstein coefficients，因此 coordinatewise length-3 已闭合。缺口是它不处理非交换耦合。

**Rank-one projector boundary。** 取

\[
M=\frac1{1+x^2}\begin{pmatrix}1&x\\x&x^2\end{pmatrix},\qquad
N=\frac1{1+y^2}\begin{pmatrix}1&y\\y&y^2\end{pmatrix}.
\]

对 `11` 个 canonical classes 去掉零根和允许的单位根后，剩余次数分布为：

```text
degree 1: 6 classes
degree 2: 4 classes
degree 3: 1 class
```

6 个一次 residual classes 用 \(S=x^2+y^2,u=xy\) 改写、显式正项和 Sturm 检查闭合；4 个二次 residual classes 用 \(u\ge0/u\le0\) 半域拆分、AM-GM / square controls 与 Sturm 检查闭合；唯一三次 residual `L3C08` 用偶次 \(U,V\) 降维和分段证书闭合。projective infinity 用齐次参数和谱半径连续性闭合。因此 rank-one projector boundary 的 `11/11` 类已闭合。

但这仍不能外推到 scaled rank-one 或 full-rank interior。

**Scaled rank-one 子族。** 放开 projector 的 eigenvalue：

\[
M=mP_x,\qquad N=nP_y,\qquad 0\le m,n\le1.
\]

这里三个自然捷径都失败：

- 谱半径不沿 \(m,n\) 简单单调；
- `m=n=1` 的 projector boundary 不能当上界；
- `m=0` 或 `n=0` 不自动落入 coordinatewise 子定理，因为还可能有与 mask 不对齐的 rank-one coupling。

释放 \(m,n\) 后，`10` 类为二次 residual，`L3C08` 为三次 residual；一些 projector 情形的一次 residual 会升成二次 residual。所以必须逐类证明。

第一批闭合的是几个结构较短的类：

- `L3C02` 与 `L3C07`：用 \(S=x^2+y^2,u=xy\) 的半域拆分，再对 \(m,n\in[0,1]\) 做 Bernstein certificate；
- `L3C11`：用一元二次判别式。每个 margin 写成 \(p(x)=Ax^2+Bx+C\)，证明 \(A\ge0\)、\(C\ge0\)、\(4AC-B^2\ge0\)；
- `L3C05`：用 parity route。每个 margin 写成
  \[
  p(x,y)=E(X,Y,m,n)+xy\,O(X,Y,m,n),\quad X=x^2,\ Y=y^2,
  \]
  再证明 \(E\ge0\) 与 \(E^2-XYO^2\ge0\)。其中一个 endpoint guard 用
  \[
  (a-b)^2(4a^2b+4ab^2+1)\ge0
  \]
  闭合。

随后 `L3C06` 也被同一个 parity route 闭合。到这里为止，还不能说 scaled-rank-one 完成，因为剩下的类虽然 residual 次数仍低，但 bad Bernstein coefficients 集中在 top-corner / diagonal 区域，单盒证书会失败。

下一步换成 exterior-square / trace route。核心观察是：有些 product 的 rank defect 让二次 Schur margins 可以通过 exterior square 的 trace 来写，而不是直接展开原来的三次 characteristic factor。这样先闭合了 `L3C09` 和 `L3C10`：

- `L3C09` 的三个 quadratic margins 可以直接用 parity / Bernstein gate；
- `L3C10` 的 trace / \(J_{\rm mid}\) 与 \(J_-\) 可以直接闭合，剩下 \(J_+\) 需要 depth-1 dyadic subdivision，再沿 \(a=b\) 对角线三角化。

同一种 triangle-Bernstein 思路后来继续闭合 `L3C04`、`L3C03` 和 `L3C01`。这些类的共同困难是：多数 margin 的一盒 Bernstein 系数非负，但 guard 在 same-half top boxes 里留下少量坏盒。处理方式不是把坏盒当反例，而是把坏盒沿对角线分成 triangular charts，再在每个 chart 上做 exact Bernstein certificate。

最后剩下的是三次 residual `L3C08`。它不能按二次 Schur margin 处理。这里的闭合方式是：

- 两个 constant margins 和 \(J_{\rm mid}\) 直接由高阶 exact Bernstein 闭合；
- \(J_-\) 经 depth-1 dyadic subdivision 闭合；
- \(J_+\) 只剩两个 same-half top guard 坏盒，再沿 \(a=b\) 三角化，四个 charts 全部闭合。

因此当前 scaled-rank-one 的精确结论已经更新为：

```text
length-3 scaled-rank-one 子族中，
全部 11 个 canonical classes 的非零 residual factors 满足 Schur/Jury 非扩张条件。
```

这比之前的 `L3C02/L3C05/L3C07/L3C11` 单类结论强得多；但它仍不是完整 length-3 theorem。原因是 scaled-rank-one 只覆盖

\[
M=mP_x,\qquad N=nP_y
\]

这一条边界子族，没有覆盖 \(M,N\) 同时 full rank 且非交换的内点。

**Stage 4 full-rank length-3。** scaled-rank-one 闭合后，下一层问题改成 full-rank 参数化：

\[
N=\operatorname{diag}(\nu_1,\nu_2),
\qquad
M=R(c,s)\operatorname{diag}(\mu_1,\mu_2)R(c,s)^\top,
\qquad
c^2+s^2=1.
\]

其中

\[
0\le \nu_1,\nu_2,\mu_1,\mu_2\le1.
\]

已知闭合的 face 包括：

- relative angle 为零的 coordinatewise face；
- \(M\) isotropic 因而可化成 coordinatewise 的 face；
- rank-one projector corner；
- scaled-rank-one corner。

一开始剩下的自然边界是：

```text
m_rank_one_n_full
m_full_n_rank_one
n_isotropic_m_rotated
```

这三条边界后来都已经闭合。

`m_full_n_rank_one` 中

\[
N=\operatorname{diag}(\nu_1,0),
\qquad
M=R(c,s)\operatorname{diag}(\mu_1,\mu_2)R(c,s)^\top.
\]

因为 product rank 至多为 `2`，非零 characteristic factor 降为二次。二次 Schur margins

\[
1-e_1+e_2,\qquad 1+e_1+e_2,\qquad 1-e_2.
\]

都可以在

\[
(\mu_1,\mu_2,\nu_1,t)\in[0,1]^4,\qquad t=c^2
\]

上用 exact Bernstein certificate 闭合。`m_rank_one_n_full` 和 `n_isotropic_m_rotated` 则保留 cubic factor，用相同的 Schur/Jury margin 逻辑逐类闭合。

之后 Stage 4E 先做 full-rank interior rational-grid pressure map，在 `2376` 个 interior 压力点上没有发现 negative margin、zero margin 或 determinant-zero violation。这一步只是 pressure failure map，不是证明。Stage 4F 再用 sparse power-coefficient arithmetic 闭合 selected target margins。最后 Stage 4G 完成总装：

```text
11 个 canonical classes
5 个 Schur/Jury margins per class
合计 55/55 margins closed
51 个 one-box Bernstein
4 个 depth-1 dyadic repair
```

所以，旧 reduced \(R_D\) 语义下的二维 full-rank length-3 cubic Schur/Jury margin 问题已经闭合。

但随后出现一个重要语义修正：真实 projected ADMM 的 reduced switching edge 不是旧的 self-consistent \(R_D=A_{D,D}\)，而是 source-target matrix

\[
A_{b,c}.
\]

因此不能把 Stage 4G 直接读成 arbitrary switching coverage。后来闭合的是 closed-word transfer：任意有限 closed mask word 的 true source-target product 与对应 legacy product 具有相同 characteristic polynomial。于是，在已覆盖的 nonconstant period-3 closed words 上，谱非扩张可以转移回来；但这仍不等于 arbitrary aperiodic switching、可达性、cone compatibility 或全局收敛。

当前 switching 理论的开放位置已经后移为：

- source-target edge polyhedra 与真实 projected 轨道 admissibility；
- constant self-loop 的 cone-restricted metric 或 active-region exit；
- path-complete seminorm / phase metric；
- 更长 closed words、higher-dimensional switching 和 Jordan / affine-drift 红队；
- 从谱证书到原优化问题 residual、KKT 和有界性的桥。

### I.8 修正算法分支

这一分支需要先写前置推导，否则会显得像突然换了一个算法。逻辑顺序是：

```text
direct ADMM 的 VI/PPA 收缩矩阵失败
-> 把 direct ADMM 看成 prediction
-> 给 prediction 加 proximal 项，得到 Q_P
-> 选择 correction matrix M 和 metric H，使 HM=Q_P 且 G>=0
-> 再检查 correction 是否保持 z>=0、y in Y、x in X
```

#### I.8.1 direct VI/PPA 为什么失败

使用 essential variable

\[
v=(y,z,\lambda).
\]

direct ADMM 的 predictor inequality 可以写成

\[
\theta(u)-\theta(\tilde u^k)+(w-\tilde w^k)^\top F(\tilde w^k)
\ge
(v-\tilde v^k)^\top Q(v^k-\tilde v^k),
\]

其中 slack 特例 \(C=I\) 下

\[
Q_{\rm slack}=
\begin{pmatrix}
\beta B^\top B & 0 & 0\\
\beta B & \beta I & 0\\
-B & -I & \frac1\beta I
\end{pmatrix},
\]

direct update 对应的 correction matrix 是

\[
M_{\rm slack}=
\begin{pmatrix}
I&0&0\\
0&I&0\\
-\beta B&-\beta I&I
\end{pmatrix}.
\]

标准 VI/PPA proof prototype 要求存在 metric \(H\)，使

\[
H M_{\rm slack}=Q_{\rm slack},
\]

并且

\[
G=Q_{\rm slack}^\top+Q_{\rm slack}-M_{\rm slack}^\top H M_{\rm slack}
\]

是正半定，最好正定。直接计算会得到两个问题。第一，

\[
H_{\rm slack}=
\begin{pmatrix}
\beta B^\top B & 0 & 0\\
\beta B & \beta I & 0\\
0&0&\frac1\beta I
\end{pmatrix}
\]

通常不是对称矩阵。第二，更致命的是 \(G\) 有负方向。具体地，

\[
G_{\rm slack}=
\begin{pmatrix}
0&0&0\\
-\beta B&0&0\\
0&0&\frac1\beta I
\end{pmatrix}.
\]

取扰动满足

\[
\Delta z=B\Delta y,\qquad \Delta\lambda=0,\qquad B\Delta y\ne0.
\]

则

\[
\Delta v^\top G_{\rm slack}\Delta v
=-\beta\|B\Delta y\|^2<0.
\]

这正是 Lyapunov 线里的坏交叉项。因此标准 VI/PPA / direct-route 收缩条件不能证明原始 direct slack ADMM。注意：这不是反例，只是证明路线失败。

#### I.8.2 为什么加 proximalized prediction

direct route 失败后，一个自然想法是：不改 \(x,y,z\) 三个 predictor 的 Gauss-Seidel 基本顺序，但在 prediction 子问题里加入 proximal 项，让 predictor inequality 右边的矩阵变强。

prediction 写成：

\[
\tilde x^k\in\arg\min_{x\in X}{\cal L}_\beta(x,y^k,z^k,\lambda^k),
\]

\[
\tilde y^k\in\arg\min_{y\in Y}
{\cal L}_\beta(\tilde x^k,y,z^k,\lambda^k)
+\frac12\|y-y^k\|_{P_y}^2,
\]

\[
\tilde z^k\in\arg\min_{z\ge0}
{\cal L}_\beta(\tilde x^k,\tilde y^k,z,\lambda^k)
+\frac12\|z-z^k\|_{P_z}^2,
\]

\[
\tilde\lambda^k
=\lambda^k-\beta(A\tilde x^k+B\tilde y^k+\tilde z^k-b).
\]

其中 \(P_y\succeq0,P_z\succeq0\)。若取 \(P_z=0\)，\(z\)-prediction 仍是原来的显式投影：

\[
\tilde z^k=
\Pi_{\mathbb R_+^m}
\left(b-A\tilde x^k-B\tilde y^k+\lambda^k/\beta\right).
\]

\(y\)-proximal 最优性比 direct 情形多出

\[
(y-\tilde y^k)^\top P_y(\tilde y^k-y^k).
\]

移到 predictor inequality 右端后，它贡献

\[
(y-\tilde y^k)^\top P_y(y^k-\tilde y^k).
\]

同理，\(z\)-proximal 项贡献

\[
(z-\tilde z^k)^\top P_z(z^k-\tilde z^k).
\]

因此新的 predictor inequality 是

\[
\theta(u)-\theta(\tilde u^k)+(w-\tilde w^k)^\top F(\tilde w^k)
\ge
(v-\tilde v^k)^\top Q_P(v^k-\tilde v^k),
\]

其中

\[
Q_P=Q_{\rm slack}+\operatorname{Diag}(P_y,P_z,0).
\]

写成块矩阵就是

\[
Q_P=
\begin{pmatrix}
\beta B^\top B+P_y&0&0\\
\beta B&\beta I+P_z&0\\
-B&-I&\frac1\beta I
\end{pmatrix}.
\]

于是关键变成：能不能选 \(P_y,P_z\)，使

\[
S_P=Q_P+Q_P^\top
\]

正定。对 \(S_P\) 做右下角 \(\frac2\beta I\) 的 Schur complement，可得到

\[
\widehat S_P=
\begin{pmatrix}
2P_y+\frac32\beta B^\top B&\frac\beta2 B^\top\\
\frac\beta2 B&2P_z+\frac32\beta I
\end{pmatrix}.
\]

若

\[
P_y\succ0,\qquad P_z\succeq0,
\]

则 \(\widehat S_P\succ0\)，从而

\[
S_P\succ0.
\]

这就是 proximalized prediction 的作用：它不是直接证明收敛，而是把原来失败的 direct \(Q\) 改造成一个可以进入 correction 收缩框架的 \(Q_P\)。

#### I.8.3 correction 的基本代数

令

\[
d^k=v^k-\tilde v^k.
\]

corrected algorithm 的抽象形式是

\[
v^{k+1}=v^k-Md^k.
\]

如果能找到 \(H=H^\top\succ0\)，满足

\[
HM=Q_P,
\]

并且

\[
G=Q_P^\top+Q_P-M^\top H M\succeq0,
\]

那么标准代数给出 Fejer 型下降：

\[
\|v^{k+1}-v^\ast\|_H^2
\le
\|v^k-v^\ast\|_H^2-\|d^k\|_G^2.
\]

这就是修正算法分支真正想要的东西：不是直接消灭坏交叉项，而是通过新的 correction metric 让坏项进入 \(G\succeq0\) 的下降结构。

最简单的代数选择是 scaled-\(Q_P\) correction：

\[
H=\alpha^{-1}I,\qquad M=\alpha Q_P.
\]

此时

\[
HM=Q_P,
\]

且

\[
G=S_P-\alpha Q_P^\top Q_P.
\]

只要

\[
0<\alpha\le\frac{\lambda_{\min}(S_P)}{\|Q_P\|_2^2},
\]

就有 \(G\succeq0\)。

这一步说明 corrected route 在矩阵上是可行的。但它有一个致命可行性问题：scaled-\(Q_P\) correction 的 \(z\)-分量一般是

\[
z^{k+1}=z^k-\alpha[Q_P(v^k-\tilde v^k)]_z,
\]

不保证仍在 \(\mathbb R_+^m\)。所以它只是 algebraic gate，不是可执行的 slack-variable theorem。

#### I.8.4 z-fixed correction：保住 \(z\ge0\)

为了不破坏 slack 可行性，下一步强制

\[
z^{k+1}=\tilde z^k.
\]

这要求 correction matrix 的 \(z\)-row 满足

\[
M_z=[0,I,0].
\]

记

\[
A_y=\beta B^\top B+P_y,\qquad D_z=\beta I+P_z.
\]

构造 \(W=H^{-1}\)：

\[
W=
\begin{pmatrix}
\beta^2A_y^{-1}B^\top D_z^{-1}BA_y^{-1}+R
&-\beta A_y^{-1}B^\top D_z^{-1}&0\\
-\beta D_z^{-1}BA_y^{-1}&D_z^{-1}&0\\
0&0&E
\end{pmatrix},
\]

其中 \(R\succ0,E\succ0\)。令

\[
H=W^{-1},\qquad M_{\rm corr}=WQ_P.
\]

直接相乘得到

\[
M_{\rm corr}=
\begin{pmatrix}
RA_y&-\beta A_y^{-1}B^\top&0\\
0&I&0\\
-EB&-E&\frac1\beta E
\end{pmatrix}.
\]

因此 \(M_{\rm corr}\) 的 \(z\)-row 正是 \([0,I,0]\)，所以 correction 后

\[
z^{k+1}=\tilde z^k\in\mathbb R_+^m.
\]

同时

\[
HM_{\rm corr}=W^{-1}WQ_P=Q_P.
\]

剩下要检查 \(G\succeq0\)。因为

\[
G=Q_P^\top+Q_P-Q_P^\top WQ_P.
\]

在 \(R=0,E=0\) 的极限中，Schur complement 给出：若 \(P_y\succ0,P_z\succeq0\)，则极限 \(G_0\succ0\)。由连续性，取足够小的 \(R,E\succ0\)，实际 \(G\) 仍可保持正定或半正定。

到这里，修正算法的核心下降式已经有了：

\[
\|v^{k+1}-v^\ast\|_H^2
\le
\|v^k-v^\ast\|_H^2-\|v^k-\tilde v^k\|_G^2.
\]

它推出

\[
\sum_k\|v^k-\tilde v^k\|_G^2<\infty,\qquad
v^k-\tilde v^k\to0.
\]

这就是 z-fixed corrected theorem 的前置推导。

但它仍有一个新的 blocker：虽然 \(z\) 安全，\(y\) 会被 correction 移动。一般 closed convex \(Y\) 不保证在这种 affine correction 下保持可行。

因此 z-fixed route 只能先得到 restricted 版本。若 \(Y=\mathbb R^n\)，没有 \(y\)-可行性问题，可以证明

```text
Y=R^n, z-fixed corrected algorithm:
v^k=(y^k,z^k,lambda^k) converges,
and every x-predictor cluster point forms a KKT/VI solution with the same v-limit.
```

证明大意是：下降式给出 \(v^k\) bounded 和 \(v^k-\tilde v^k\to0\)；若 \(x\)-predictor 有 cluster point，则沿子列把 predictor optimality、normal cone closed graph 和 residual identity 取极限，得到 KKT/VI；再把这个 cluster solution 放回 Fejer 下降，推出整个 \(v^k\) 收敛。

#### I.8.5 一般 \(Y\)：为什么转到 ADM-G

z-fixed correction 的问题是：它为了保住 \(z\)，牺牲了 \(y\)-可行性。若要处理一般 closed convex \(Y\)，更自然的修正算法是 Gaussian back substitution，也就是 ADM-G。

关键是重新排列块顺序为

\[
(z,x,y).
\]

这样有两个好处：

1. \(z\) 是 first block，correction 不移动它，所以 \(z\ge0\) 安全；
2. \(y\) 是 last block，correction 是凸组合：
   \[
   y^{k+1}=y^k+\alpha(\tilde y^k-y^k).
   \]
   若 \(Y\) closed convex 且 \(0<\alpha<1\)，则 \(y^{k+1}\in Y\)。

真正的 feasibility blocker 变成 middle block \(x\)。ADM-G 的 correction 公式给出

\[
x^{k+1}-x^k
+(A^\top A)^{-1}A^\top B(y^{k+1}-y^k)
=\alpha(\tilde x^k-x^k).
\]

如果 \(X=\mathbb R^p\)，这个问题消失。在

\[
X=\mathbb R^p,\quad A^\top A\succ0,\quad B^\top B\succ0,\quad \beta>0,\quad \alpha\in(0,1)
\]

以及解集非空、子问题可解等条件下，这给出一般 closed convex \(Y\) 的 modified ADM-G 收敛 theorem。

如果想让 \(X\) 不是全空间，就要保证 correction 后仍在 \(X\)。把上式改写为

\[
x^{k+1}
=(1-\alpha)x^k+\alpha\tilde x^k
-\alpha C_{xy}(\tilde y^k-y^k),
\]

\[
C_{xy}=(A^\top A)^{-1}A^\top B.
\]

由于 \(x^k,\tilde x^k\in X\)，凸组合部分在 \(X\) 内；唯一危险是最后的平移项。因此需要

\[
X-\alpha C_{xy}(Y-Y)\subseteq X.
\]

这就是 invariant-\(X\) 条件。它放宽了 \(X=\mathbb R^p\)，但仍不覆盖 arbitrary closed convex \(X,Y\)。一般盒约束、单纯形、有界凸集通常不满足这个条件，除非 correction 方向落在 \(X\) 的 lineality / 可平移方向中。

#### I.8.6 arbitrary closed convex \(X,Y\)：projected route 的两次分叉

最后尝试过 primal projected ADM-G：先做 affine correction，再投影回

\[
\mathcal V=X\times Y\times\mathbb R^m.
\]

这条线目前只能算 proof attempt。原因是原 ADM-G / VI-PPC 收缩证明依赖 exact correction identity

\[
v^{k+1}=v^k-M(v^k-\tilde v^k).
\]

一旦改成 projection，就会多出 projection residual。普通 Euclidean projection 或只投影 primal variables 不保证保留原来的 \(H/G\)-metric contraction。

于是改成 image-space \(H\)-projected Fejer gate。这个门槛本身是成立的：若 affine correction 先给出

\[
\|\hat w^{k+1}-w^\ast\|_H^2
\le
\|w^k-w^\ast\|_H^2-\|d^k\|_G^2,
\]

且

\[
w^{k+1}=\Pi_{\Omega_{\rm img}}^H(\hat w^{k+1}),
\]

则 \(H\)-metric projection 给出

\[
\|w^{k+1}-w^\ast\|_H^2
\le
\|w^k-w^\ast\|_H^2
-\|d^k\|_G^2
-\|w^{k+1}-\hat w^{k+1}\|_H^2.
\]

这说明：只要投影是在同一个 \(H\)-metric、同一个 image feasible set 上做的，projection 本身不会破坏 Fejer 下降。困难不在这一行代数，而在三个前置义务：

1. image feasible set 必须是闭凸的；
2. predictor 和 correction 必须能在 image variables 里真实执行；
3. image limit 必须能 lift 回 primal \(x,y\)，并满足原 slack KKT/VI。

第一次尝试把 image state 压缩为

\[
v=(c,z,\lambda),\qquad c=By.
\]

这样做的动机是减少变量，只把 \(By\) 的 image 保留下来，把 \(a=Ax\) 通过约束关系消掉。但推导到 predictor inequality 时，消去 \(a\)-block 后留下一个未控交叉项。也就是说，压缩变量确实降低了状态维度，却把 \(x\)-block 的曲率和 coupling 信息丢掉了，结果无法证明

\[
\theta(\tilde u^k)-\theta(u)
\quad\text{对应的 predictor inequality}
\]

能给出所需的 \(Q_P/H/G\) 正性结构。因此 \(v=(c,z,\lambda)\) 的 image-regular theorem 不能接受。

第二次改为 full-image-state：

\[
w=(a,c,z,\lambda),\qquad a=Ax,\quad c=By.
\]

这一步的关键不是形式上多放一个变量，而是保留 \(a\)-block 后，predictor inequality 中原本失控的交叉项可以被 full-image \(Q_{\rm full}\) 结构吸收。相应地可以构造 full-image metric，使

\[
H_{\rm full}M_{\rm full}=Q_{\rm full},
\]

并通过参数条件得到

\[
S_{\rm full}=Q_{\rm full}+Q_{\rm full}^\top\succ0.
\]

在这个基础上，先做 affine corrected step，再做 full-image feasible set 上的 \(H\)-projection，得到

\[
\|w^{k+1}-w^\ast\|_{H_{\rm full}}^2
\le
\|w^k-w^\ast\|_{H_{\rm full}}^2
-\|w^k-\tilde w^k\|_{G_{\rm full}}^2
-\|w^{k+1}-\hat w^{k+1}\|_{H_{\rm full}}^2.
\]

所以 full-image-state route 已经给出一个 accepted corrected theorem，但它需要 image-regular 假设：例如 image domains / value functions 的闭性、fiber attainment、可执行 primal selection，以及精确 predictor 和精确 \(H\)-projection。结论也要写窄：

```text
full image state w^k converges to an image KKT point;
若 fiber attainment 和 selection 条件成立，可以 lift 出 primal slack KKT/VI solution。
```

它不证明 primal full sequence \((x^k,y^k)\) 本身收敛，也不覆盖没有 image-regular 假设的 arbitrary closed convex \(X,Y\)。

所以修正算法分支的边界是：

```text
restricted Y=R^n: corrected theorem closed.
general Y with X=R^p: ADM-G modified theorem closed.
general Y with invariant-X: ADM-G modified theorem closed.
image-regular full-image-state: H-projected corrected theorem closed.
arbitrary closed convex X,Y without image-regular assumptions: still open.
original direct ADMM: still open.  # 当时状态；已由文末 2026-07-14 strict 66-cycle 覆盖
```

## 第二部分：反例搜索

### II.1 什么才算 proof-grade counterexample

普通数值发散不够。一个可接受的 strict counterexample 至少要同时给出：

1. 明确的凸二次 slack-variable 问题数据；
2. 子问题 well-posed；
3. 固定 active region 或周期 active itinerary；
4. 局部线性/仿射 recurrence；
5. \(\rho>1\) 或明确扩张机制；
6. 轨道确实全时留在对应 active region / itinerary 中；
7. 可复现的参数、初始化和验证。

当前没有满足这些条件的 counterexample。（当时状态；已由文末 2026-07-14 strict
66-cycle 覆盖。）

### II.2 普通随机筛查

最早的普通随机 QP 筛查设置是：

```text
trials: 5
seed: 0
max_iter: 200
tol: 1e-7
beta: 1.0
dim_x: 2
dim_y: 2
dim_m: 2
```

结果：

```text
converged: 4
stagnated: 1
suspect_unstable: 0
```

对应谱半径 sanity check 中，一个代表样本的 local spectral radius 是

```text
0.6150459074084457
```

这些只是 smoke evidence：没有发现不稳定，但也不能证明收敛。

### II.3 fixed-mask 反例搜索

fixed-mask 搜索的目标是：

```text
找一个 D，使 rho(R_D)>1，
并且真实 projected ADMM 轨道能永远留在这个 fixed mask 的 region 中。
```

结果是：

- 抽象 reduced map 中存在非交换扩张压力；
- 嵌回凸二次 QP 后也得到 \(\rho\approx1.00226\) 的 fixed-active candidate；
- 但扩张特征值是可见复旋转模态；
- 有限步 stay check 最终离开 fixed mask；
- signed-\(q\) tangent 和 positive real expansion 两条能支持 fixed-mask 反例的路线都没有形成 candidate；
- positive real expansion 已有 contraction-based impossibility proof attempt。

所以 fixed-mask 路线目前没有 strict counterexample。

### II.4 switching 反例搜索

fixed-mask 不够后，反例搜索自然转向 active-set switching。目标变成：

```text
找一个周期 mask itinerary，使 product matrix 扩张，
同时每一段都满足对应 signed-q cone margin。
```

短周期 switching screen 曾发现一些扩张记录，最大谱半径约 `1.01365`，但这些扩张仍对应前面那个复旋转 fixed-mask 机制，没有给出正实 switching ray 或 cone-compatible certificate。因此也没有形成严格反例。

length-2 switching 后来反而被证明为局部 theorem。length-3 也已经推进很多：coordinatewise、rank-one projector boundary、scaled-rank-one `11/11` 类，以及 Stage 4 full-rank `55/55` Schur/Jury margins 都已闭合。

但这里有一个重要修正：旧 Stage 4G 闭合的是 legacy \(R_D\) product 语义。真实 projected ADMM switching 使用 source-target \(A_{b,c}\)。closed-word characteristic transfer 已经修复了有限 closed word 的谱对应关系，但还没有给 arbitrary aperiodic switching、cone admissibility 或 path-complete Lyapunov。

反例搜索随后转向 exact admissibility 和周期门。固定有理 QP 的短 closed words 中，大量 word 被 exact edge-row violation 或 Farkas/dual gate 排除；Hamiltonian length-4 的三个等价类也已完成 unit-root face 与 strict-row violation 分析。这些都是反例端的好消息，但都不是严格发散反例。

### II.5 当前反例搜索结论

当前不是“证明了没有反例”。准确说是：

```text
普通随机 QP：没有发现不稳定，只是 smoke。
fixed-mask：有扩张压力，但不能保持 fixed mask。
visible complex / negative expansion：会离开 active region。
signed-q tangent expansion：退化到收缩块。
positive real expansion：被 contraction argument 排除。
length-2 switching：已变成局部 nonexpansion theorem。
length-3 scaled-rank-one：已闭合 11/11 canonical classes。
Stage 4 full-rank legacy margins：已闭合 55/55。
true source-target closed-word transfer：已闭合。
fixed rational QP short closed words：未形成 admissible strict counterexample。
arbitrary aperiodic switching、cone metric、higher-dimensional counterexample：仍开放。
```

因此若继续找反例，应优先做 exact admissibility、Jordan / affine-drift、cone-restricted metric 或更高维 switching，而不是继续普通随机 QP。

## 当前可以声明

可以声明：

- \(z\)-projection formula、multiplier identity、normal cone / complementarity 结构成立；
- projection-only Lyapunov proof 仍未完成；
- direct VI/PPA 收缩条件在 slack 特例下失败；
- fixed-mask 单段反例路线没有形成 proof-grade counterexample；
- 二维 reduced active-set length-2 nonconstant products 已闭合为局部 theorem；
- length-3 coordinatewise、rank-one projector boundary、scaled-rank-one `11/11` canonical classes 已闭合；
- Stage 4 full-rank length-3 legacy Schur/Jury margins 已闭合 `55/55`；
- true source-target closed-word characteristic transfer 已闭合；
- phase-dependent Lyapunov 已证明若干非平凡二维 QP、参数盒和 reduced 邻域中的原始 direct ADMM 收敛；
- block small-gain、Selector-IQC 和 signed-PWA common-metric 给出多类 proof-grade 充分收敛条件；
- 若允许 modified algorithm，restricted \(Y=\mathbb R^n\)、general \(Y\) with \(X=\mathbb R^p\)、invariant-\(X\) 的 ADM-G 版本、以及 image-regular full-image-state H-projected 版本已有可证结论。

## 当前不能声明

不能声明：

- 原始 direct slack-variable 三块 ADMM 全局收敛；
- projection FNE alone proves convergence；
- fixed-mask pressure candidate 是严格反例；
- length-2 theorem 推出 arbitrary switching；
- Stage 4G legacy product 证书直接推出真实 arbitrary switching；
- closed-word transfer 推出 aperiodic switching、admissibility 或 cone compatibility；
- small-gain / Selector-IQC / signed-PWA 充分条件覆盖全部 \([A,B,I]\) direct ADMM；
- corrected / ADM-G theorem 证明了原始 direct ADMM；
- arbitrary closed convex \(X,Y\) 在没有 image-regular 假设下的 projected/image-space corrected theorem 已完成；
- image-regular corrected theorem 推出 primal full-sequence \((x^k,y^k)\) 收敛。

## 下一步

若继续原始 direct ADMM 主线：

1. 不要回到普通 random QP。
2. 优先处理 true source-target / active-cone 语义下的 path-complete seminorm 或 cone-restricted metric。
3. 三周期已闭合；继续 length \(\ge4\) 的 fractional-selector products，或转向更高维 / 更长周期的 proof-grade counterexample gate。
4. 若走正向定理路线，继续把 phase / history / signed-PWA common metric 从充分条件推向更大可检验区域。

若继续修正算法主线：

1. 把 modified algorithm 与 original direct ADMM 分开写。
2. 若目标是 image-regular corrected theorem，可以沿 full-image-state 路线写成局部定理。
3. 若目标是 arbitrary closed convex \(X,Y\)，必须证明或替换 closed image domains、closed value functions、fiber attainment 和 executable selection；不能直接引用 image-regular theorem。

具体证据索引不放在这份正文里；需要查证时再看单独的 source-of-truth 清单。

## 2026-07-14 终点覆盖：一般收敛命题已被严格反例否定

本节覆盖上文所有“当前没有 strict counterexample / original direct ADMM still open”的旧状态。

最新结论：原始 direct three-block slack ADMM 即使在二维 $A=B=I$、两个目标都是纯强凸二次
函数时，也不保证全局收敛。`notes/strict_rational_66_cycle_counterexample.md` 给出一个
proof-grade bounded 66-cycle：mask word 为两个 `00` 后接 64 个 `01`，然后严格闭合。

关键 gates：

- $Q_1,Q_2\succ0$，子问题唯一；
- 问题存在唯一 KKT 点，周期不是 KKT；
- exact closure $s_{66}=s_0$；
- 66 phases × 2 coordinates 的 signed projection margins 全部严格，最小值大于 $1/1000$；
- signed-state recurrence 与原始 $x/y/z/\lambda$ ADMM update 逐 phase exact 一致；
- 线性项版本已平移并再次 exact 验证为 $c_1=c_2=0$ 的纯二次版本；
- word 的最小周期为 66。

复现：

```bash
PYTHON=/opt/anaconda3/bin/python
$PYTHON experiments/breakthrough/certify_strict_rational_66_cycle.py
$PYTHON -m pytest -q tests/test_strict_rational_66_cycle.py
```

输出：

- `outputs/breakthrough_attempts/stage44_strict_rational_66_cycle/certificate.json`
- `proof_reviews/strict_rational_66_cycle/adversarial_risk_register.md`

现在的 claim boundary 是：这是 bounded periodic nonconvergence，足以否定无条件全局收敛，
但不声称 iterates 无界。当前 provenance 是 Codex adversarial audit + exact rational guard，
尚无外部独立 reviewer。

正向研究的合理后续不再是“一般收敛证明”，而是保留已有条件定理，并寻找排除该周期机制的
最小条件（small-gain、common metric、对角/标量结构、proximal/correction 等）。
