# Phase-dependent edge 有理证书

状态：`exact_certificate`。

## 输入与算术

从原始 QP

\[
Q_1=3I,\qquad Q_2=\begin{pmatrix}7&4\\4&3\end{pmatrix},\qquad
A=B=I,\quad b=0,\quad \beta=1
\]

直接使用 `SymPy Rational` 推导 reduced transition；没有把浮点矩阵重新有理化。固定
\(\varepsilon=1/20\)，并使用题设给定的四个 phase 矩阵 \(H_b\)。

## 精确判据

对四个 masks，脚本检查

\[
H_b-H_b^{\rm core}\succeq0.
\]

对全部 16 条 source-target edges，脚本检查

\[
H_b-A_{bc}^\top H_cA_{bc}-\frac1{20}C_{bc}^\top C_{bc}\succeq0,
\qquad
C_{bc}=[\Delta\lambda,\Delta y,\Delta z].
\]

每个矩阵均为实对称矩阵；根据主子式半正定判据，逐一精确计算全部非空主子式。
共检查 60 个 core 主子式和 240 个 edge 主子式，负主子式数量均为零。

## 结论

四个 core domination 条件和 16 个 edge dissipation 条件全部成立。因此这是给定二维凸
QP 的 `exact_certificate`，而不是浮点 screen。它证明 phase-dependent 能量沿任意真实
mask edge 至少下降

\[
\frac1{20}\left(\|\Delta\lambda\|^2+\|\Delta y\|^2+\|\Delta z\|^2\right).
\]

该证书针对这个固定 QP；它本身不证明所有 slack-variable 三块 ADMM 实例收敛。
