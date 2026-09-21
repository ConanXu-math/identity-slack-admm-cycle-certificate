# Slack-ADMM：一般强凸目标函数下单位松弛变量的全局收敛性

## 精确数学定义

取任意正整数
[
n_x,n_y,m.
]

变量为
[
xinmathbb R^{n_x},qquad
yinmathbb R^{n_y},qquad
zinmathbb R^m,qquad
lambdainmathbb R^m.
]

给定函数
[
f:mathbb R^{n_x}	omathbb R,qquad
g:mathbb R^{n_y}	omathbb R,
]
满足
[
fin C^1(mathbb R^{n_x}),qquad
gin C^1(mathbb R^{n_y}),
]
并且分别强凸：存在常数
[
mu_f>0,qquad mu_g>0,
]
使得对任意 (u,vinmathbb R^{n_x})，
[
f(u)ge
f(v)+langle
abla f(v),u-vangle
+rac{mu_f}{2}|u-v|^2,
]
对任意 (u,vinmathbb R^{n_y})，
[
g(u)ge
g(v)+langle
abla g(v),u-vangle
+rac{mu_g}{2}|u-v|^2.
]

线性约束数据满足
[
Ainmathbb Q^{m	imes n_x},qquad
Binmathbb Q^{m	imes n_y},qquad
binmathbb Q^m,
]
以及
[
operatorname{rank}[A B]=m.
]

有理数要求只施加于 (A,B,b)。函数 (f,g) 不要求具有有理系数表示。

研究
[
min_{x,y,z}quad f(x)+g(y)
]
满足
[
Ax+By+z=b,qquad zge0.
]

这里 (zge0) 按分量理解。

记
[
r(x,y,z)=Ax+By+z-b.
]

固定乘子符号约定为
[
mathcal L_eta(x,y,z,lambda)
=
f(x)+g(y)+delta_{mathbb R_+^m}(z)
-langlelambda,r(x,y,z)angle
+rac{eta}{2}|r(x,y,z)|^2.
]

固定
[
eta=1.
]

从任意有限实数初态
[
(x^0,y^0,z^0,lambda^0)
in
mathbb R^{n_x}	imes
mathbb R^{n_y}	imes
mathbb R^m	imes
mathbb R^m
]
出发，执行以下精确迭代：
[
x^{k+1}
=
operatorname*{argmin}_{xinmathbb R^{n_x}}
left{
f(x)
-langlelambda^k,Ax+By^k+z^k-bangle
+rac12|Ax+By^k+z^k-b|^2
ight},
]
[
y^{k+1}
=
operatorname*{argmin}_{yinmathbb R^{n_y}}
left{
g(y)
-langlelambda^k,Ax^{k+1}+By+z^k-bangle
+rac12|Ax^{k+1}+By+z^k-b|^2
ight},
]
[
z^{k+1}
=
left[
b-Ax^{k+1}-By^{k+1}+lambda^k
ight]_+,
]
[
lambda^{k+1}
=
lambda^k
-
Ax^{k+1}
-
By^{k+1}
-
z^{k+1}
+b.
]

其中 ([v]_+) 表示逐分量取
[
([v]_+)_i=max{v_i,0}.
]

初态无需满足原始可行性，也无需满足 (z^0ge0)。

由于 (f) 与 (g) 强凸，每个 (x)-子问题与 (y)-子问题均具有唯一极小点。因此，从任意有限初态出发，上述迭代在每一步均有定义。

## KKT 条件

KKT 点
[
(x^star,y^star,z^star,lambda^star)
]
满足
[

abla f(x^star)-A^	oplambda^star=0,
]
[

abla g(y^star)-B^	oplambda^star=0,
]
[
Ax^star+By^star+z^star=b,
]
[
z^starge0,qquad
lambda^starle0,
]
以及
[
z_i^starlambda_i^star=0,
qquad i=1,dots,m.
]

上述假设保证 KKT 点存在且唯一。

由于
[
operatorname{rank}[A B]=m,
]
映射
[
(x,y)mapsto Ax+By
]
满射到 (mathbb R^m)。任取严格正向量 (ar z>0)，均可求得 ((ar x,ar y)) 满足
[
Aar x+Bar y=b-ar z.
]
因此原不等式形式
[
Ax+Byle b
]
满足 Slater 条件。

函数
[
(x,y)mapsto f(x)+g(y)
]
强凸，并具有强制增长性质，因此在非空闭凸可行集上存在唯一最优点
[
(x^star,y^star).
]
随后
[
z^star=b-Ax^star-By^star
]
唯一确定。

Slater 条件保证存在 KKT 乘子。若 (lambda_1,lambda_2) 均为同一最优点对应的 KKT 乘子，则
[
A^	op(lambda_1-lambda_2)=0,qquad
B^	op(lambda_1-lambda_2)=0.
]
因此
[
[A B]^	op(lambda_1-lambda_2)=0.
]
由于 ([A B]) 满行秩，([A B]^	op) 为单射，从而
[
lambda_1=lambda_2.
]

所以完整 KKT 状态
[
(x^star,y^star,z^star,lambda^star)
]
唯一。

## 待判定命题

判定以下全称命题是否成立：

对任意正整数
[
n_x,n_y,m,
]
任意满足上述条件的
[
f,g,A,B,b,
]
以及任意有限实数初态
[
(x^0,y^0,z^0,lambda^0),
]
由上述精确 Slack-ADMM 规则生成的完整迭代序列均满足
[
(x^k,y^k,z^k,lambda^k)
longrightarrow
(x^star,y^star,z^star,lambda^star)
qquad (k	oinfty),
]
其中
[
(x^star,y^star,z^star,lambda^star)
]
为该问题唯一的 KKT 点。

要求判定完整状态序列的收敛性。目标函数值、原始可行性残差、相邻迭代差值以及某个子序列的收敛，可以作为证明中的中间结论。

## LLM 最终交付

### 肯定答案

提交覆盖上述全部量词的完整数学证明，包括：

1. 对任意有限初态，所有子问题均存在唯一解，因此无限迭代序列始终有定义；
2. 对全部满足条件的 (f,g,A,B,b)，证明
   [
   (x^k,y^k,z^k,lambda^k)
   	o
   (x^star,y^star,z^star,lambda^star);
   ]
3. 若使用下降量、Lyapunov 函数、Fejér 单调性、算子理论、固定点理论或其他辅助量，需要完整给出相应不等式及适用条件；
4. 若先证明有界性、渐近正则性、残差收敛或聚点满足 KKT 条件，还需要证明全部聚点相同，并推出完整序列收敛。

### 否定答案

提交一个具体有限维反例，包括：

[
n_x,qquad n_y,qquad m,
]
明确给出的函数
[
f:mathbb R^{n_x}	omathbb R,qquad
g:mathbb R^{n_y}	omathbb R,
]
有理数数据
[
A,qquad B,qquad b,
]
以及明确的有限初态
[
(x^0,y^0,z^0,lambda^0).
]

必须逐项验证：

1. (fin C^1(mathbb R^{n_x})) 且强凸；
2. (gin C^1(mathbb R^{n_y})) 且强凸；
3. (A,B,b) 的全部分量均为有理数；
4. (operatorname{rank}[A B]=m)；
5. 每一步轨道严格按照上述四个更新公式生成；
6. 该无限轨道不收敛到唯一 KKT 点。

二次函数属于上述一般函数类别，因此以二次函数构造的严格反例可以否定该全称命题。

采用分段仿射映射及其特征值证明轨道不收敛时，还必须证明轨道在每一次迭代中均满足所采用分段区域的定义不等式，从而保证对应仿射递推公式对全部迭代次数成立。

采用周期轨道时，必须精确证明周期关系对无限轨道成立。

采用发散特征方向时，必须证明初态或其有限次迭代具有相应特征方向分量，并证明之后的全部轨道始终位于所使用的分段区域。

## 验收要求

验收对象为数学证明。

数值实验可以用于寻找反例、计算候选参数或复核解析结果，但任意有限次数值迭代均不能独立证明无限序列收敛、发散或形成周期轨道。
