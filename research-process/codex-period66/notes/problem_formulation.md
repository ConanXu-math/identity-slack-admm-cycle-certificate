# Problem Formulation

## 原始问题

从两块不等式约束问题出发：

\[
\min\{\theta_1(x)+\theta_2(y)\mid Ax+By\le b,\ x\in X,\ y\in Y\}.
\]

引入 slack variable 后得到三块等式约束形式：

\[
\min\{\theta_1(x)+\theta_2(y)+0(z)\mid Ax+By+z=b,\ x\in X,\ y\in Y,\ z\in \mathbb{R}^m_+\}.
\]

这个问题属于三块可分离凸优化，但线性约束矩阵具有特殊结构 \([A,B,I]\)。

## 直接三块 ADMM

采用如下符号约定：

\[
{\cal L}_\beta(x,y,z,\lambda)
=\theta_1(x)+\theta_2(y)
-\lambda^\top(Ax+By+z-b)
+\frac{\beta}{2}\|Ax+By+z-b\|^2.
\]

直接三块 ADMM 为：

\[
x^{k+1}\in \arg\min_{x\in X}{\cal L}_\beta(x,y^k,z^k,\lambda^k),
\]

\[
y^{k+1}\in \arg\min_{y\in Y}{\cal L}_\beta(x^{k+1},y,z^k,\lambda^k),
\]

\[
z^{k+1}\in \arg\min_{z\ge 0}{\cal L}_\beta(x^{k+1},y^{k+1},z,\lambda^k),
\]

\[
\lambda^{k+1}=\lambda^k-\beta(Ax^{k+1}+By^{k+1}+z^{k+1}-b).
\]

一般三块 ADMM 的直接推广不保证收敛；这个仓库研究的是 \(C=I,z\ge0\) 的特殊结构是否能带来额外控制。

## 关键突破口

\(z\)-子问题是投影而不是一般第三块子问题：

\[
z^{k+1}=\Pi_{\mathbb{R}^m_+}
\left(b-Ax^{k+1}-By^{k+1}+\lambda^k/\beta\right).
\]

因此可以尝试使用：

- 投影单调性；
- firm nonexpansiveness；
- normal cone 最优性条件；
- coordinate-wise complementarity；
- active-set 线性化。

这些结构在一般 \(Ax+By+Cz=b\) 的三块模型中不存在。
