# A strict rational 66-cycle counterexample

状态：`exact_rational_strict_periodic_nonconvergence_counterexample`。

## 1. Strongly convex rational QP

取 $A=B=I_2$、$\beta=1$，并令

$$
\varepsilon=\frac1{1000},\qquad
\mu=\frac{8957}{10000},\qquad
\nu=\frac{999}{1000},
$$

$$
M=\varepsilon I+(\mu-\varepsilon)
\frac{(-1,20)(-1,20)^T}{401},
$$

$$
N=\varepsilon I+(\nu-\varepsilon)
\frac{(-1,10)(-1,10)^T}{101}. \tag{1}
$$

于是 $\sigma(M)=\{\varepsilon,\mu\}\subset(0,1)$、
$\sigma(N)=\{\varepsilon,\nu\}\subset(0,1)$。定义

$$
Q_1=M^{-1}-I\succ0,\qquad Q_2=N^{-1}-I\succ0,
$$

$$
b=(0,1)^T,\qquad c_1=c_2=(-1,0)^T. \tag{2}
$$

考虑 direct three-block slack ADMM 应用于

$$
\min_{x,y,z}\
\frac12x^TQ_1x+c_1^Tx+
\frac12y^TQ_2y+c_2^Ty,
\qquad x+y+z=b,\quad z\ge0. \tag{3}
$$

两个目标都强凸，两个 ADMM 子问题矩阵 $Q_i+I$ 正定。问题有唯一 KKT 点

$$
x^\star=y^\star=0,qquad z^\star=(0,1)^T,qquad
\lambda^\star=(-1,0)^T. \tag{4}
$$

这个线性项版本还可精确平移为纯二次版本。令

$$
\bar x=x+Q_1^{-1}c_1,\qquad
\bar y=y+Q_2^{-1}c_2,
$$

$$
\bar b=b+Q_1^{-1}c_1+Q_2^{-1}c_2. \tag{4a}
$$

去掉与变量无关的常数后，式 (3) 等价于

$$
\min_{\bar x,\bar y,z}
\frac12\bar x^TQ_1\bar x+
\frac12\bar y^TQ_2\bar y,
\qquad \bar x+\bar y+z=\bar b,\quad z\ge0. \tag{4b}
$$

ADMM 更新在该平移下逐步共轭：$q,z,\lambda$ 不变，$x,y$ 只作上述固定平移。
因此下面的周期同时给出 $c_1=c_2=0$ 的纯强凸二次反例。exact checker 对
式 (4b) 的四个原始 ADMM updates 另做了一套逐 phase 有理重验。

## 2. Exact signed recurrence

第一次 projection/multiplier 更新后令

$$
q=z+\lambda,qquad z=q_+,qquad\lambda=q_-.
$$

在 signed state $s=(y,q)$ 上，原 ADMM 精确等价于

$$
r=(I-M)b+Mc_1-c_2,
$$

$$
p=My-(I-M)|q|+r,qquad
y^+=Np,qquad
q^+=(I-N)p+q_++c_2. \tag{5}
$$

对 $D=\operatorname{diag}(0,d)$、$d\in\{0,1\}$，记式 (5) 的 affine
lift 为 $L_d\in\mathbb Q^{5\times5}$。取长度 66 的 word

$$
\mathcal W=(0,0,\underbrace{1,\ldots,1}_{64\text{ times}}). \tag{6}
$$

令

$$
L_{\mathcal W}=L_1^{64}L_0^2
=\begin{pmatrix}P&a\\0&1\end{pmatrix},qquad
s_0=(I-P)^{-1}a. \tag{7}
$$

exact checker 验证 $\det(I-P)\ne0$。式 (7) 是周期点的紧凑精确定义；其小数近似为

$$
s_0\approx
(-0.07792080511392698,\ 0.7776744554457875,\
-1.151767163423518,\ -0.008619166161363401)^T. \tag{8}
$$

## 3. Closure and strict itinerary

从 $s_0$ 按式 (5) 和 word (6) 递推得到
$s_1,\ldots,s_{66}$。全有理计算给出

$$
\boxed{s_{66}=s_0}. \tag{9}
$$

更关键的是，66 个 phase 上的全部 132 个 orthant inequalities 都严格满足：

$$
q_{k,1}<0,qquad
\begin{cases}
q_{k,2}<0,&k=0,1,\\
q_{k,2}>0,&k=2,\ldots,65,
\end{cases} \tag{10}
$$

并且 exact checker 证明统一有理余量

$$
\boxed{
\min_{0\le k<66}
\min\{-q_{k,1},\ (2d_k-1)q_{k,2}\}>\frac1{1000}.} \tag{11}
$$

实际最小余量约为 $0.00371052469443529102$。所以这不是浮点 tie、facet orbit
或错误预设 itinerary；每一步都严格使用原正交投影所选择的 branch。

这组四位小数参数来自固定 word 下的有限网格审计，并由两套精确有理实现重新验证；它不是
把八位浮点轨道截断后继续迭代。完整三位小数网格未发现正余量候选，但该有限排查不构成
三位小数参数全局不可能性的定理。

word (6) 不是更短 word 的重复，且 strict masks 由状态唯一决定，因此该轨道的最小周期为
66。

## 4. Return to the original ADMM variables

对每个 phase 置

$$
z^k=(q^k)_+,qquad\lambda^k=(q^k)_-,
$$

并用前一 phase 定义

$$
x^k=M\{-y^{k-1}-|q^{k-1}|+b-c_1\}. \tag{12}
$$

checker 逐 phase 直接重算原始 $x$-update、$y$-update、projection 和 multiplier
update，所有等式均在 $\mathbb Q$ 上精确成立。因此

$$
(x^{k+66},y^{k+66},z^{k+66},\lambda^{k+66})
=(x^k,y^k,z^k,\lambda^k). \tag{13}
$$

该轨道与唯一 KKT 点 (4) 不同，故 direct three-block slack ADMM 不收敛。

## 5. Consequence and claim boundary

式 (3)（等价地，零线性项版本 (4b)）、(6)--(13) 给出原始模型中的 proof-grade bounded periodic
nonconvergence counterexample。因此：

$$
\boxed{
\text{即使两个目标是纯强凸二次函数，原 direct slack 三块 ADMM 的一般全局收敛命题仍为假。}}
$$

- 这是严格的 bounded 66-cycle，不声称 iterates 无界；
- 它足以否定“所有有限初值都收敛”的一般定理；
- 已有 small-gain、common-metric、对角/标量等条件收敛定理仍然有效；
- 可复现 exact artifact：
  `experiments/breakthrough/certify_strict_rational_66_cycle.py`；
- numerical discovery 只用于找到参数，最终 closure、KKT、强凸性、原 ADMM 更新和
  132 个 strict inequalities 均由 exact rational arithmetic 重验。
