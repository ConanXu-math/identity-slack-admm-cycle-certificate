# Strict-KKT local expansion and finite-history Lyapunov obstruction

状态：`exact_obstruction_checked_by_codex`。

## 1. A strongly convex rational slack QP

取 $A=B=I_2$、$\beta=1$，并令

$$
M=\frac1{1000}I+left(\frac9{10}-\frac1{1000}\right)
\frac{(-1,20)(-1,20)^T}{401},
$$

$$
N=\frac1{1000}I+left(\frac{999}{1000}-\frac1{1000}\right)
\frac{(-1,10)(-1,10)^T}{101}.
$$

它们的谱分别为 $\{1/1000,9/10\}$ 与
$\{1/1000,999/1000\}$。定义

$$
Q_1=M^{-1}-I\succ0,\qquad Q_2=N^{-1}-I\succ0,
$$

以及

$$
b=(0,1)^T,\qquad c_1=c_2=(-1,0)^T.
$$

考虑

$$
\min\ \frac12x^TQ_1x+c_1^Tx+rac12y^TQ_2y+c_2^Ty,
\qquad x+y+z=b,\quad z\ge0. \tag{1}
$$

其唯一 KKT 点为

$$
x^\star=y^\star=0,\qquad z^\star=(0,1)^T,
\qquad\lambda^\star=(-1,0)^T. \tag{2}
$$

在仓库符号约定下，$Q_ix^\star+c_i=\lambda^\star$，并且式 (2) 满足
可行性和严格互补性。signed projection state 为

$$
q^\star=z^\star+\lambda^\star=(-1,1)^T,
$$

所以 KKT 点严格位于 selector $D=\operatorname{diag}(0,1)$ 的开 orthant，
不是 facet/boundary 构造。

## 2. Exact locally expanding branch

在 signed state $s=(y,q)$ 中，分支 Jacobian 为

$$
B_D=
\begin{pmatrix}
NM&-N(I-M)S_D\\
(I-N)M&D-(I-N)(I-M)S_D
\end{pmatrix},\qquad S_D=2D-I. \tag{3}
$$

$B_D$ 有一个零特征值；其剩余 monic cubic 的 Jury middle margin 是

$$
J_{\rm mid}
=-rac{433775258062294638209}
{40047143579101562500000000}<0. \tag{4}
$$

因此 $\rho(B_D)>1$。式 (4) 与 Stage 31 的精确有理证书相同，但这里新增了
strict KKT embedding：由于 $q^\star$ 两个坐标与零有正距离，原 ADMM 在 KKT
点的一个开邻域内确实由式 (3) 的 affine branch 给出。

## 3. Static quadratic Lyapunov no-go

不存在 $H\succ0$ 使 KKT 邻域内每一步都满足

$$
\|s^{k+1}-s^\star\|_H^2
\le\|s^k-s^\star\|_H^2. \tag{5}
$$

否则在 strict cell 内线性化即可得到
$B_D^THB_D\preceq H$，进而 $\rho(B_D)\le1$，与式 (4) 矛盾。
同理，任何在 KKT 点具有正定二阶主部的 $C^2$ 单步 Lyapunov 都不可能局部单调。

## 4. Finite-history quadratic Lyapunov no-go

固定任意有限 history depth $p$。若一个二次能量

$$
V_k=V(e_k,e_{k-1},\ldots,e_{k-p+1}),qquad e_k=s^k-s^\star,
$$

在所有足够靠近 KKT 的真实轨道上非增，并在一致 history 子空间上正定控制
$\sum_{j=0}^{p-1}\|e_{k-j}\|^2$，也会产生矛盾。

理由是 strict cell 对任意有限步数 $T$ 都允许把初始扰动缩放得足够小，使前
$T+p$ 步保持在同一 branch。该段上 $e_{k+1}=B_De_k$。一致 history 子空间

$$
\{(B_D^{p-1}v,\ldots,B_Dv,v):v\}
$$

在 history shift 下继承 $B_D$ 的非零谱。若 $V$ 非增且正定，则所有
$B_D^T$ 在该子空间上有统一幂界，迫使 $\rho(B_D)\le1$，仍与式 (4) 矛盾。

所以，加入任意固定有限阶 lag 并不能产生一个“每一步都降、同时局部控制状态”的
普适二次证明。可行的正向路线必须允许能量在 strict segment 内上升，并只在
mask exit / 多步 block 上获得净下降，或使用不局部等价于范数的非标准势函数。

## 5. Claim boundary

- `experiments/breakthrough/certify_local_expansion_history_obstruction.py` exact 核对
  强凸性、KKT、strict orthant、fixed-point recurrence 与 Jury margin；
- 该 obstruction 严格否定一大类 static/finite-history monotone Lyapunov 模板；
- 它不证明 ADMM 发散：局部扩张轨道会离开该 mask，离开后仍可能返回并收敛；
- 因而一般全局结论的下一门应是 exit-to-exit block energy 或真实 itinerary
  admissibility，而不是继续给一步交叉项配有限个历史系数。
