<!--
id: P-C-02
route: gpt56_sol_codex
stage: multiplier_relaxation
class: retrospective_distilled
assert_verbatim: false
source: skills/admm-proof-workflow/prompts/multiplier_perturbation_to_extension.md
-->

# Multiplier Perturbation-to-Extension Workflow

状态：`reusable_research_prompt`

## 1. 目的

本工作流用于从一个已经精确验证的 ADMM 反例出发，研究只改变乘子步长后是否恢复
收敛，并判断固定实例结论能否推广到问题类别。它把 AI 的作用拆成候选路线生成、
结构推导、计算筛查和证明蓝图生成；最终数学结论必须通过独立的精确复算或证明审查。

Provenance 边界：本文件是依据保留的研究 artifacts 固化出的可复现协议。除非另有完整
原始对话记录，不得把它描述成发现阶段逐字使用的历史 prompt。

本项目采用

$$
\mathcal L_\beta=f(x)+g(y)+\iota_{\mathbb R_+^m}(z)
-\lambda^\top r+\frac{\beta}{2}\lVert r\rVert^2,
\qquad r=Ax+By+z-b,
$$

以及

$$
\lambda^{k+1}=\lambda^k-\tau r^{k+1}.
$$

标准更新对应 $\tau=\beta$。跨问题比较时应使用无量纲相对步长
$\vartheta=\tau/\beta$。

## 2. 必须先区分的四层量词

| 层级 | 目标陈述 | 最低证明门 |
| --- | --- | --- |
| `S1 fixed-instance local` | 固定问题和步长，在 KKT 点邻域收敛 | 严格 KKT 分支、Schur 稳定、投影安全邻域 |
| `S2 fixed-initialization` | 固定问题和指定初值，在一段步长上收敛 | 严格有限前缀、统一进入已证吸引域 |
| `S3 fixed-problem global` | 对一个固定问题，任意有限初值在足够小步长下收敛 | 全局误差界、下降式、cost-to-go 与势函数收缩 |
| `S4 class-uniform` | 整个问题类共享同一个正相对步长区间 | 问题无关常数，或对任意候选区间的精确反例 |

只有明确写出量词发生了哪一步变化，才能使用 “extension” 或 “generalization”。
`S1` 不能自动推出 `S2`，`S2` 不能自动推出 `S3`，而

$$
\forall \mathcal P\ \exists\bar\tau(\mathcal P)>0
$$

也不能改写成

$$
\exists\bar\tau>0\ \forall\mathcal P.
$$

## 3. 七阶段工作流

### Stage 0：冻结研究合同

记录并冻结：

- 问题数据 $A,B,Q_1,Q_2,b,c_1,c_2$；
- 罚参数 $\beta$、基准初值和已验证轨道；
- 唯一允许的第一阶段改动：把乘子步长从 $\beta$ 改成 $\tau$；
- 当前目标层级 `S1`、`S2`、`S3` 或 `S4`；
- 可使用的信息、禁止泄露的已知答案和人工干预点。

若任务用于独立模型比较，发现模式不得提供已知候选步长、Lyapunov 矩阵、投影 word
或推广定理。复现模式可以提供这些 artifacts，但必须明确标记为 `reproduction`。

### Stage 1：从原始 ADMM 重新推导参数化动力系统

1. 使用完整状态，例如 $w=(y,z,\lambda)$，从原始
   $x\to y\to z\to\lambda$ 更新重新消元。
2. 对每个投影 mask $D$ 推导

   $$
   w^+=T_D(\tau)w+a_D(\tau).
   $$

3. 检查 $T_D(\tau)$ 和 $a_D(\tau)$ 对 $\tau$ 的依赖，并从原始四步更新逐列复算。
4. 再次核对当前乘子符号、normal cone 与 complementarity；不得从标准步长的约简状态
   直接外推到 $\tau\ne\beta$。

输出状态：`symbolic_derivation`。未经逐列或独立实现核对，不得升级为证明。

### Stage 2：AI 候选生成与数值筛查

让模型同时提出至少三条候选路线：

1. KKT 严格分支的局部谱稳定；
2. 原非收敛初值能否被有限前缀捕获到吸引域；
3. 能否由误差界或 primal-dual gap 推出问题依赖的小步长定理。

筛查必须记录：

- 候选 $\tau$ 或 $\vartheta$；
- 完整状态谱、投影 word、最小符号余量和闭合误差；
- 与 KKT 点的关系；
- 初值范围与量词；
- seed、精度、代码入口和输出路径。

这一阶段只能标记为 `numerical_screen`。浮点谱半径、长轨道和看似稳定的残差都不是
定理或证书。

### Stage 3：固定实例的精确证书

从筛查结果中选简单有理目标，并从冻结的原始 QP 重新构造全部对象。依目标层级选择门：

- `S1`：精确特征多项式、Schur/Sturm 或有理 Lyapunov 证书，加严格投影安全椭球；
- 步长区间：在端点验证 Sylvester 主子式，并证明矩阵不等式关于 $\tau$ 的区间传递；
- `S2`：用有理区间敏感度递推验证每一步投影符号，并在有限步后统一进入吸引域；
- 精确边界：给出定义边界的整数多项式和严格有理夹逼，而不是只报十进制根。

至少使用两个不共享约简代码的复算器：一个从分支映射复算，一个从原始
$x,y,z,\lambda$ 四步更新复算。

### Stage 4：从实例到问题类别

先写 quantifier matrix，再选择路线。优先检查：

1. 固定 $\lambda$ 时 primal 子问题是否全局强凸；
2. primal proximal-residual error bound 是否全局成立；
3. 一次 Gauss-Seidel sweep 是否有统一下降常数；
4. residual 是否可由 sweep displacement 控制；
5. dual function 是否有全局 error bound；
6. 以上常数是否依赖问题数据。

若这些义务闭合，可得到

$$
\forall\mathcal P\ \exists\bar\tau(\mathcal P)>0\quad
\forall\tau\in(0,\bar\tau(\mathcal P))
$$

下的固定问题全局收敛。Hong--Luo 提供 primal-dual gap 架构时，必须明确文献归属；
本项目的新增部分只能是针对 slack-last 非紧模型的假设核验、显式常数或边界扩展。

### Stage 5：统一步长与 adaptive 路线的红队

若要研究 `S4`，先改用 $\vartheta=\tau/\beta$ 并明确量词。不得因为每个问题都有
$\bar\tau(\mathcal P)$ 就推断存在统一正下界。

负向路线需要同时闭合：

- 参数化问题族；
- 精确谱或单位圆临界证书；
- 严格投影分支的可达性或不变性；
- 实际原始 ADMM 的有界非收敛轨道。

若固定安全阈值过于保守，可以研究 adaptive look-ahead gate，但必须包含 trial
multiplier、完整 trial primal sweep、接受检验、拒绝后的 full rollback、有限回溯和
接受步长统一正下界。Residual balancing 或 BB 只能生成 proposal，不能替代安全门。

### Stage 6：独立验证与证据升级

每个结论按下列顺序升级：

`numerical_screen` -> `candidate` -> `exact_certificate` ->
`internally_reviewed_theorem` -> `externally_reviewed_result`。

生成模型不得审批自己的证明。验证者至少检查：

- 乘子符号和半步索引；
- SPD、满行秩、KKT 唯一性与严格互补；
- 投影 tie convention 与所有 strict margins；
- 定理量词、初值范围和局部/全局范围；
- 文献归属与新增贡献边界；
- 精确算术、原始 ADMM replay 和可复现命令。

## 4. 可直接复制的主提示词

```text
你是一个负责“候选生成与证明蓝图”的优化研究代理。你的输出不是自动成立的证明；
所有数学主张都必须进入独立精确验证门。

[研究目标]
从一个已经通过精确复算的 slack-last 三块 ADMM 反例出发，只改变乘子更新
lambda^{k+1} = lambda^k - tau r^{k+1}，研究：
1. 固定实例上哪些 tau 可能恢复收敛；
2. 原反例初值能否在一段 tau 区间内进入 KKT 吸引域；
3. 哪些额外假设可把结论推广为“每个固定问题都有问题依赖的小步长区间”；
4. 是否可能存在跨整个问题类统一的相对步长区间。

[输入]
- MODE: <discovery | reproduction | extension | red_team>
- frozen instance manifest: <path>
- base exact certificate: <path>
- beta: <value>
- initial state: <path or values>
- target model class: <assumptions>
- allowed tools and arithmetic: <tools>
- forbidden prior information: <items>
- output directory: <path>

[必须遵守]
1. 使用 L_beta = f+g+iota - lambda^T r + beta/2 ||r||^2 的符号；先核对
   notes/z_projection_identity.md。
2. 冻结所有问题数据和 beta，第一阶段只改变 tau。跨问题比较使用 theta=tau/beta。
3. 从原始 x->y->z->lambda 更新重新推导完整状态分支映射 T_D(tau), a_D(tau)。
4. 开始计算前先提交 quantifier matrix，区分：固定实例局部、指定初值、固定问题
   任意初值、问题类统一区间。
5. 同时提出局部谱、有限前缀捕获、primal-dual gap 三条候选路线，并说明各自
   可能失败的位置。
6. 浮点搜索只能输出 numerical_screen。只有从原始有理 QP 重建并通过 strict
   projection、closure、KKT、Lyapunov/Schur/Sturm 和 raw-ADMM replay 后，才能标记
   exact_certificate。
7. 推广时逐项核验全局 primal error bound、sweep descent、
   residual-to-displacement、dual error bound 和 cost-to-go；不得把固定实例结果外推。
8. 若讨论统一步长，必须按量词分析，并主动寻找依赖条件数退化的反例族。
9. 给出失败结果和开放义务；不得把 solver feasibility、LP infeasibility、坏
   Bernstein 系数或模型解释当成定理。
10. 生成者不得自我批准。最后输出一个独立 verifier 的检查清单。

[阶段输出]
A. problem_contract.md：冻结数据、允许改动、符号和目标量词。
B. route_matrix.md：至少三条路线、预期证书、失败模式和选择理由。
C. numerical_screen.json：候选 tau、谱、word、margin、closure、seed 和命令。
D. exact_certificate_plan.md：有理化对象、精确门和两个独立 replay 路径。
E. quantifier_extension.md：从 S1/S2 到 S3/S4 所需的新假设与不能跨越的边界。
F. proof_blueprint.md：逐 lemma 依赖、文献归属和未闭合义务。
G. generation_trace.json：输入披露、人工干预、工具、被拒路线和最终候选。
H. verifier_checklist.md：由独立角色执行的复算与范围审计。

[停止条件]
- 若只有浮点证据，停止在 numerical_screen。
- 若缺少严格分支可达性，不能由谱结论推出真实 ADMM 轨道结论。
- 若常数依赖问题数据，不能声称 class-uniform step。
- 若任何关键 lemma 未闭合，输出 proof_attempt 和最小下一义务，不得补写结论。
```

## 5. 四个阶段续跑提示词

### A. 候选发现

```text
保持问题数据、beta 和初值完全不变，只改变 tau。先从原始 ADMM 推导 full-state
piecewise-affine map，再筛查局部谱、原初值轨道和投影 word。返回三个候选方向及其
最小证据，不做 theorem claim。所有结果标记 numerical_screen。
```

### B. 精确化

```text
冻结候选 tau 与分支 word。丢弃浮点推导，从原始有理 QP 重建分支矩阵、KKT、投影
输入和完整轨道。分别建立 branch-map verifier 与 raw-ADMM verifier；只有两者一致且
所有 strict margins、Lyapunov/Schur/Sturm 门通过时，才输出 exact_certificate。
```

### C. 类别推广

```text
不要沿用固定实例矩阵。先写目标量词，再列出推广所需的 primal/dual error bounds、
sweep descent、residual-to-displacement 和 cost-to-go。逐条说明哪些来自文献、哪些需
在当前 slack-last 类重新证明。任何常数依赖问题数据时，明确保留 bar_tau(P)。
```

### D. 对抗复核

```text
假设生成者的结论有错。优先检查乘子符号、半步索引、投影 tie、局部到全局跳跃、
固定初值到任意初值跳跃、forall-exists 次序、数值筛查冒充证明和文献归属。输出
verdict、反例压力、必须修复项和可接受的最窄结论。
```

## 6. 当前项目的 artifact 映射

- 固定实例扰动理论：`notes/relaxed_multiplier_interval_theory.md`
- 固定实例 exact certifier：
  `experiments/breakthrough/certify_relaxed_multiplier_interval_theory.py`
- 一般问题依赖小步长：`notes/general_small_dual_step_convergence.md`
- adaptive 安全门：`research/adaptive_dual_step/`
- 统一相对步长红队：`research/universal_dual_step/`
- 乘子符号：`notes/z_projection_identity.md`
- 论文研究路线 provenance：`slack_admm/slack_admm0724.tex`

## 7. 论文中的最小报告模板

正文不需要粘贴完整 prompt。建议只写：

> The human researchers asked Codex with GPT-5.6 Sol whether changing only the
> multiplier step could restore convergence of the verified period-66
> instance. The workflow re-derived the full-state parameterized branch maps,
> screened candidate step regimes, and developed exact-rational certificate
> routes; independent exact replay then checked the fixed-instance claims and
> separated them from the subsequent class-level extension.

完整输入披露、阶段输出、失败路线、人工干预和 verifier checklist 应放在补充材料或
公开仓库，而不是塞入正文。
