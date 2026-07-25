# Problem Intake

## 研究对象

固定严格 66 周期见证中的有理 QP，保持 `x,y,z` 三个子问题不变，只把乘子更新改为

\[
\lambda^{k+1}=\lambda^k-\tau
\bigl(x^{k+1}+y^{k+1}+z^{k+1}-\bar b\bigr),
\qquad 0<\tau\le 1.
\]

完整状态取 (w=(y,z,\lambda)\in\mathbb R^6\)。

## 目标结论

1. 给出严格 KKT 活动分支上的一般局部收敛判据；
2. 给出共同 (H\) 控制一段有理 `tau` 区间的充分条件；
3. 给出有限严格投影前缀进入不变椭球后收敛的捕获定理；
4. 为原周期初值认证一个非退化有理 `tau` 区间；
5. 对当前 QP 的 `01` 分支局部稳定边界给出严格有理夹逼。

## 允许工具

- 精确有理线性代数与多项式运算；
- Sylvester 正定判据；
- 离散 Lyapunov 方程；
- (H\)-度量 Cauchy--Schwarz 不等式；
- Schur--Cohn/Jury 单位圆判据；
- 精确 Sturm 根计数与有理区间隔离；
- 一元 Bernstein 或有理区间证书。

## 明确不声称

- 不证明该 QP 对任意初值收敛；
- 不证明所有 identity-slack QP 在某统一步长区间收敛；
- 不用有限浮点轨迹证明渐近收敛；
- 不把数值阈值直接称为精确边界。
