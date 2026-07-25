# Phase metric 六参数结构定理

状态：structure_theorem_accepted_by_independent_review。本结论只解释固定有理 QP 的
phase metric 结构，不声称参数或下降系数为 SDP 最优值。

## 六参数 ansatz

令 \(D_b=\operatorname{diag}(b_1,b_2)\)、\(s_b=b_1b_2\)，并定义 mask 坐标代数中的投影

\[
W=\operatorname{Diag}(N_0)=\operatorname{diag}(1/4,1/2).
\]

canonical observable 为

\[
S_b=\begin{pmatrix}0&-(I-D_b)\\I&0\\0&D_b\end{pmatrix},
\qquad r=(y,u)\mapsto(\lambda,y,z).
\]

对六个标量参数
\(\theta=(\ell_0,\ell_1,y_0,c_0,z_0,\zeta)\)，取

\[
\begin{aligned}
L&=\ell_0I+\ell_1W,\\
Y_b&=I+D_b(y_0I+\ell_1W)+s_b(c_0I+\ell_1W),\\
Z_b&=z_0I-\ell_1W+s_b\zeta I,\\
H_b(\theta)&=S_b^\top\operatorname{blkdiag}(L,Y_b,Z_b)S_b.
\end{aligned}
\]

参数

\[
\theta_\star=\left(\frac{13}{10},-\frac25,\frac65,\frac12,2,-\frac15\right)
\]

逐 mask 精确生成

\[
\begin{aligned}
H_{00}&=\operatorname{diag}(1,1,6/5,11/10),\\
H_{01}&=\operatorname{diag}(1,2,6/5,11/5),\\
H_{10}&=\operatorname{diag}(21/10,1,21/10,11/10),\\
H_{11}&=\operatorname{diag}(5/2,23/10,19/10,2).
\end{aligned}
\]

四个 phase 的矩阵条目对六参数的 exact Jacobian rank 为 \(6\)，故这些参数方向在线性
ansatz 内彼此独立。

## 符号群结构

记 \(T_c=2D_c-I\)、\(J_c=\operatorname{blkdiag}(I,T_c)\)。reduced transition 可写为

\[
A_{bc}=J_c\widetilde A_b,
\]

其中

\[
\widetilde A_b=
\begin{pmatrix}
N_0M_0&-N_0(I-M_0)\\
(I-N_0)M_0&N_0+(I-N_0)M_0-(I-D_b)
\end{pmatrix}.
\]

由于 \(H_c\) 的 \(y-u\) 交叉块为零且 \(u\)-块对角，精确有

\[
J_c^\top H_cJ_c=H_c.
\]

此外，\(S_cJ_c\) 将 inactive dual 与 active slack 的符号完全消去。因此

\[
C_{bc}=S_cA_{bc}-S_b=(S_cJ_c)\widetilde A_b-S_b.
\]

脚本对四个 masks 和全部十六条 source-target edges 精确核对上述恒等式。

## 下降系数提升

已有 fixed \(H_b\) 在 \(\varepsilon=1/20\) 时满足更强的逐 edge 界

\[
R_{bc}(1/20)\succeq\frac1{20}I,
\qquad C_{bc}^\top C_{bc}\preceq\frac94I.
\]

因此

\[
\begin{aligned}
R_{bc}(13/180)
&=R_{bc}(1/20)-\frac1{45}C_{bc}^\top C_{bc}\\
&=\left(R_{bc}(1/20)-\frac1{20}I\right)
+\frac1{45}\left(\frac94I-C_{bc}^\top C_{bc}\right)\succeq0.
\end{aligned}
\]

证书还直接检查了 \(R_{bc}(13/180)\) 的全部非空主子式。这证明
\(\varepsilon=13/180\) 是同一组 \(H_b\) 的 exact 可行下降系数，但不证明它是最大值。

## 机器核验

运行：

    /opt/anaconda3/bin/python experiments/breakthrough/certify_phase_metric_six_parameter_ansatz.py \
      --json-output /tmp/phase_metric_six_parameter.json \
      --markdown-output /tmp/phase_metric_six_parameter.md
    /opt/anaconda3/bin/python -m pytest -q tests/test_phase_metric_six_parameter_ansatz.py

所有构造均从原始有理 QP 使用 SymPy Rational 推导，没有把浮点结果重新有理化。

独立复核从原始有理 \(Q_1,Q_2\) 重建了全部 16 条 edges，并逐项核对三类矩阵的
720 个主子式、六参数 Jacobian 秩和 \(J_c\) 符号消去恒等式。正式记录见
`proof_reviews/phase_metric_six_parameter_ansatz/final_verification.json`。
