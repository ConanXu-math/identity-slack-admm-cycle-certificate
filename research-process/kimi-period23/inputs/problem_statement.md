# Slack-variable 三块 ADMM 研究问题

设 \(\theta_1:\mathbb{R}^{n_1}\to(-\infty,+\infty]\) 与
\(\theta_2:\mathbb{R}^{n_2}\to(-\infty,+\infty]\) 为适当、闭、凸函数，
\(X\subseteq\mathbb{R}^{n_1}\)、\(Y\subseteq\mathbb{R}^{n_2}\) 为非空闭凸集，且
\(A\in\mathbb{R}^{m\times n_1}\)、\(B\in\mathbb{R}^{m\times n_2}\)、
\(b\in\mathbb{R}^m\)。考虑不等式约束问题

\[
\min_{x\in X,\,y\in Y}\;\theta_1(x)+\theta_2(y)
\quad\text{s.t.}\quad Ax+By\le b.
\]

引入松弛变量 \(z\in\mathbb{R}^m_+\)，得到等价的三块形式

\[
\min_{x,y,z}\; f(x)+g(y)+\delta_{\mathbb{R}^m_+}(z)
\quad\text{s.t.}\quad Ax+By+z=b,
\]

其中 \(f=\theta_1+\delta_X\)、\(g=\theta_2+\delta_Y\)。记
\(r(x,y,z)=Ax+By+z-b\)。对 \(\beta>0\)，采用符号约定

\[
\mathcal L_\beta(x,y,z,\lambda)
=f(x)+g(y)+\delta_{\mathbb{R}^m_+}(z)
-\langle\lambda,r(x,y,z)\rangle
+\frac{\beta}{2}\lVert r(x,y,z)\rVert^2.
\]

所研究的直接顺序三块 ADMM 为

\[
\begin{aligned}
x^{k+1}&\in\arg\min_x\mathcal L_\beta(x,y^k,z^k,\lambda^k),\\
y^{k+1}&\in\arg\min_y\mathcal L_\beta(x^{k+1},y,z^k,\lambda^k),\\
z^{k+1}&\in\arg\min_z\mathcal L_\beta(x^{k+1},y^{k+1},z,\lambda^k),\\
\lambda^{k+1}&=\lambda^k-\beta r(x^{k+1},y^{k+1},z^{k+1}).
\end{aligned}
\]

## 核心问题

在清楚写明可解性、子问题解的选择方式及其他所需假设的前提下，判断上述直接迭代是否收敛。若能收敛，给出严格定理和证明；若一般并不收敛，给出可独立验证的严格反例。允许得到有明确边界的部分定理、否定性结果或尚未闭合的证明义务，但不得把猜想或数值现象表述为严格结论。

三张教师材料位于 `teacher_slides/`，用于核对问题来源与公式语境。
