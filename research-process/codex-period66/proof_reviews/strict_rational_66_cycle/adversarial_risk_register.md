# Adversarial risk register: strict rational 66-cycle

审计对象：

- `notes/strict_rational_66_cycle_counterexample.md`
- `experiments/breakthrough/certify_strict_rational_66_cycle.py`
- `outputs/breakthrough_attempts/stage44_strict_rational_66_cycle/certificate.json`

| Role | Failure path | Trigger | Impact | Reproduction | Severity | Fix or mitigation |
|---|---|---|---|---|---|---|
| Mathematical semantics reviewer | signed state 的 phase 索引错一位，使 source mask 被误当成 target mask | 用 $D_k$ 生成 $q^{k+1}$ 后却在同一 phase 检查 $D_kq^{k+1}$ | 伪周期；结论失效 | 对 66 个 phase 从 $(y^k,q^k)$ 直接重算 $x^{k+1},y^{k+1},q^{k+1},z^{k+1},\lambda^{k+1}$，并与 phase $k+1$ 比较 | Critical：若存在就是致命错误 | checker 的 `all_original_admm_steps_exact` 和 `all_zero_linear_original_admm_steps_exact` 已按 target phase 逐步精确比较；两者均为 true |
| Boundary/admissibility reviewer | 周期只在浮点 tie 或 $q_i=0$ facet 上成立 | 某一步 projection argument 接近零，branch 可被错误选择 | 只能算预设 itinerary，不能算原 ADMM 轨道 | exact 检查 66 phases × 2 coordinates 的 signed margins | Critical：直接决定轨道真实性 | frozen instance `identity_slack_p66_short_v1` 满足 `uniform_margin_gt_1_over_1000=true`；最小余量约 $0.00371052469443529102$，不是边界轨道 |
| Model-scope reviewer | 周期依赖线性项，无法覆盖仓库常用的零线性纯二次模型 | $c_1=c_2=(-1,0)$ 被误认为反例机制的一部分 | 结论范围比声称的窄 | 作变量平移 $\bar x=x+Q_1^{-1}c_1$、$\bar y=y+Q_2^{-1}c_2$ 并重算原 ADMM | High：影响主结论的强度和可复用性 | 已加入零线性项等价 QP；独立逐 phase exact checks 全部通过 |
| Numerical reliability reviewer | 参数来自 differential evolution，闭合只是浮点近似 | 长周期矩阵乘积病态或 rounding 累积 | 错把近周期写成严格周期 | 将参数固定为有理数，构造 $5\times5$ affine lifts，exact 计算 $(I-P)^{-1}a$ 和 66 步回归 | Critical：浮点证据不能支撑 theorem | 所有 closure、KKT、SPD、更新与不等式都在 SymPy rational arithmetic 中重验；certificate `valid=true` |
| Optimization-model reviewer | $Q_1,Q_2$ 非正定或子问题不唯一 | 从 $M,N$ 反解 $Q_i=M_i^{-1}-I$ 时谱越界 | 反例不属于强凸、well-posed 模型 | exact 检查 $\sigma(M)=\{1/1000,\mu\}$、$\sigma(N)=\{1/1000,\nu\}$ 且 $0<\mu,\nu<1$；检查 $Q_i$ Sylvester minors | Critical：会使模型假设失效 | `Q1_positive_definite=true`、`Q2_positive_definite=true`；$Q_i+I$ 也自动正定 |
| Claim-boundary reviewer | 把 bounded periodic nonconvergence 写成 iterates 无界 | 使用“发散”一词而未区分不收敛和无界 | 研究结论被夸大 | 检查 theorem 与 certificate 的 claim text | Medium：不改变反例，但损害可信度 | 全文统一写为 bounded 66-cycle / periodic nonconvergence，并明确“不声称 iterates 无界” |
| Reproducibility owner | 巨大有理周期点未全文打印，未来无法确认 artifact 未漂移 | 脚本或参数被改动 | 难以复核历史结论 | 重跑 checker，并比较 $M,N,s_0,$ minimum margin 的 canonical SHA-256 | Medium：影响长期审计 | certificate 保存四个 exact hashes，脚本从三个短有理参数和两个方向向量重建全部对象 |
| Independent-review owner | 结论只经过本轮 Codex 反方审计，没有外部人类或 Danus 的第二实现 | 发布为“外部独立复核通过” | provenance 夸大 | 查状态标签和 review provenance | Medium：证明已有 exact guard，但独立性仍有限 | 状态保留 `checked_by_codex`；后续可用另一 CAS/人工逐式复核。不得写成 external-independent review |
| Common-mode implementation reviewer | Stage 44 的周期构造与原 ADMM 回代共享同一 signed-state 实现，可能一起保留相同推导错误 | reduced recurrence、source/target phase 或平移公式在同一函数内共同出错 | 两类 `true` 检查仍可能是假安全感 | 不导入 Stage 44，从 full state ((y,z,\lambda)) 用 exact basis evaluation 重建 raw maps，独立求 period fixed point，再检查所有四步更新 | High：影响“原算法而非 reduced surrogate”的桥 | Stage 45 第二实现全部通过，并与线性项/零线性项周期逐 phase 共轭；它降低共同实现风险，但不等于外部 reviewer |

不适用角色：security、privacy、accessibility 和 data-owner 风险不适用于本地纯数学证书；没有外部写入、凭据或用户数据。

## Release verdict

`ship with mitigations`。

当前 exact artifact 足以在仓库内升级为 proof-grade bounded periodic nonconvergence
counterexample，并据此否定无条件全局收敛；发布时必须同时保留两条边界：

1. 这是 bounded nonconvergence，不是无界发散；
2. provenance 是 Codex adversarial audit + exact rational guard，尚无外部独立 reviewer。

新增实现解耦证据：

- `experiments/breakthrough/audit_strict_rational_66_cycle_independent.py`
- `outputs/breakthrough_attempts/stage45_independent_raw_admm_audit/certificate.json`
- `tests/test_independent_strict_rational_66_cycle_audit.py`

Stage 45 不导入 Stage 44 checker，也不使用其四维 signed recurrence；“independent”仅指实现
边界，不能改写为 external-independent review。
