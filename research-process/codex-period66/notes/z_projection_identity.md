# Z Projection Identity

## Sign Convention

本仓库使用如下增广拉格朗日函数符号：

\[
{\cal L}_\beta=\theta_1(x)+\theta_2(y)-\lambda^\top r+\frac{\beta}{2}\|r\|^2,\quad
r=Ax+By+z-b.
\]

因此 multiplier 更新是：

\[
\lambda^{k+1}=\lambda^k-\beta r^{k+1}.
\]

如果改用常见的 \(+\mu^\top r\) 符号，则 \(\mu=-\lambda\)。normal cone 和互补性陈述必须先确认使用哪个符号。

## Projection Formula

固定 \(x^{k+1},y^{k+1},\lambda^k\)，令

\[
q^{k+1}=b-Ax^{k+1}-By^{k+1}+\lambda^k/\beta.
\]

\(z\)-子问题等价于：

\[
z^{k+1}=\arg\min_{z\ge0}\frac{\beta}{2}\|z-q^{k+1}\|^2
=\Pi_{\mathbb{R}^m_+}(q^{k+1}).
\]

按坐标写就是：

\[
z_i^{k+1}=\max\{0,q_i^{k+1}\}.
\]

## Multiplier Identity

由 \(r^{k+1}=Ax^{k+1}+By^{k+1}+z^{k+1}-b\) 得

\[
\lambda^{k+1}
=\lambda^k-\beta r^{k+1}
=\beta(q^{k+1}-z^{k+1}).
\]

因此 \(\lambda^{k+1}\) 是投影残差的缩放。在当前符号下，active constraint 上的 \(\lambda\) 是非正的；常见非负不等式乘子是 \(\mu=-\lambda\)。

## Normal Cone And Complementarity

投影最优性条件给出：

\[
q^{k+1}-z^{k+1}\in N_{\mathbb{R}^m_+}(z^{k+1}).
\]

在当前 \(\lambda\) 符号下：

\[
\lambda^{k+1}\in \beta N_{\mathbb{R}^m_+}(z^{k+1}).
\]

这里采用的 normal cone 定义是
\[
N_K(z)=\{g\mid \langle g,w-z\rangle\le0,\ \forall w\in K\}.
\]
因此对 \(K=\mathbb{R}^m_+\)，如果 \(z_i^{k+1}=0\)，则 \(\lambda_i^{k+1}\le0\)。

若改用不等式约束 \(Ax+By\le b\) 的非负乘子 \(\mu^{k+1}=-\lambda^{k+1}\)，坐标互补性表现为：

\[
z_i^{k+1}\ge0,\quad \mu_i^{k+1}\ge0,\quad z_i^{k+1}\mu_i^{k+1}=0.
\]

这说明 slack-variable 三块 ADMM 的第三块不仅是一个优化子问题，还带有投影和 active-set 结构。
