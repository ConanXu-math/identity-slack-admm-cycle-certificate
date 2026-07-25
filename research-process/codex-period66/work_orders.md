# 工作单：VeryMath Skill 驱动的 ADMM 研究

## 通用规则

- 每个工作单开始前先读 `research_state.md`。
- 涉及 ADMM 证明或反例时，还要读 `skills/admm-proof-workflow/SKILL.md`。
- 所有重要输出必须写入下方指定路径，不能只留在聊天中。
- 证明状态必须严格使用：`theorem`、`proof_attempt`、`numerical_screen`、`candidate_counterexample`、`unverified`。
- 执行这些工作单时不要修改工作区之外的 AI4Math Skill 仓库。

## WO-1：文献地图与证明套路

**使用 skill：** `math-paper-reading`，然后 `paper-to-skill`

**当前进展：**

- Phase 1A 已建立 `papers/reading_queue.md` 和 `outputs/literature_report.md`。
- 文献开放来源已登记到 `papers/source_manifest.md` 和 `papers/source_manifest.json`。
- 21 篇 ADMM 相关文献已用 MinerU 转为 `papers/markdown/<paper_id>/paper.md`。
- 21 篇已基于 MinerU Markdown 完成带行号 SkillCard 抽取，索引见 `papers/skills/README.md`。

**输入：**

- `knowledge_base/literature_map.md`
- 可用的 ADMM 论文 PDF 或已转换 Markdown
- 第一批主题：多块发散反例、强凸收敛、prediction-correction、不等式/slack ADMM

**任务：**

1. 建立或更新 `papers/reading_queue.md`。
2. 对每篇论文抽取定理陈述、假设、证明依赖和反例机制。
3. 将可复用证明步骤转成 proof-pattern cards。
4. 标明哪些假设不匹配 identity-block 问题。

**输出：**

- `papers/reading_queue.md`
- `papers/markdown/<paper_id>/paper.md`
- `papers/skills/<paper_id>/*.yaml`
- `knowledge_base/theorem_cards/*.md`
- `knowledge_base/proof_patterns/*.md`
- `knowledge_base/counterexamples/*.md`
- `outputs/literature_report.md`

**验收标准：**

- 每篇论文都有来源 metadata 和处理状态。
- 每个抽取 pattern 都说明它在 \([A,B,I]\) 中可能失效的位置。
- 文献结论不能无来源。

## WO-2：猜想格与证明义务

**使用 skill：** `discover-math-problems`

**当前进展：**

- Preliminary WO-2 已建立 `docs/problem_menu.md`、`docs/conjecture_lattice.md`、`docs/proof_obligations.md` 和 `docs/counterexample_pressure.md`。
- 当前状态是 `proof_obligations_ready`，不是 `verification_ready`。
- `PO8` 已有 21 篇逐行 SkillCard 证据；后续工作不再是抽取文献，而是把这些 assumption-boundary 卡片用于 proof review。

**输入：**

- `research_state.md`
- `notes/problem_formulation.md`
- `notes/z_projection_identity.md`
- `notes/candidate_lyapunov.md`
- WO-1 的文献输出

**任务：**

1. 将主问题拆成弱版本、标准版本和强版本猜想。
2. 分离一般 identity-block 模型和 slack-variable 模型。
3. 为每个猜想生成 proof obligations。
4. 补充 counterexample pressure 和 assumption-boundary notes。

**输出：**

- `docs/problem_menu.md`
- `docs/conjecture_lattice.md`
- `docs/proof_obligations.md`
- `docs/counterexample_pressure.md`

**验收标准：**

- 每个猜想都明确假设。
- 每个猜想都有证明义务或反例压力说明。
- 不能把 conjecture 标成 theorem。

## WO-3：Lyapunov 证明蓝图审查

**使用 skill：** `proof-blueprint-review`

**当前进展：**

- 第一轮闭环已完成，输出见 `proof_reviews/identity_block_lyapunov/`。
- `verification_report.json` verdict 为 `incomplete`，projection-only Lyapunov 路线未通过 acceptance gate。
- 针对用户提供的 VI/PPA 两页框架，已按 VeryMath / AI4Math `proof-blueprint-review`
  新增 `proof_reviews/vi_ppa_direct_admm/`。该 gate 现已完成 `Q,M,H,G`
  实例化：`q_m_h_derivation.md` 使用 He-Yuan 2018 的 `v=(y,z,lambda)`、
  `Q`、`M`、`H`、`G`，并专门检查 \(C=I\) slack 特例。独立 reviewer
  `Linnaeus` 接受该推导。结论是 `direct_vi_ppa_condition_failure`：
  标准 VI/PPA / He-Yuan prototype convergence condition 在原始 direct slack
  ADMM 上失败；`G_slack` 无法吸收 \(\langle B\Delta y,\Delta z\rangle\)。
  因此 VI/PPA 不能作为原始 direct slack ADMM 的收敛证明，只能作为
  direct-route 诊断和 corrected-algorithm repair route。
- 已设置 `human_checkpoint.md`，下一步必须选择加强假设、修正算法、反例或 error-bound 局部路线。
- 修正算法分支已继续推进到 `proof_reviews/vi_ppc_corrected_algorithm/`：
  `q_p_predictor_derivation.md` 修补了具体 proximalized predictor 的 \(Q_P\) 推导，
  `restricted_y_unconstrained_theorem.md` 给出 \(Y=\mathbb R^n\) 的 z-fixed theorem
  candidate。`restricted_y_cluster_kkt_limit.md` 已补出条件性 KKT-cluster bridge：
  若 \(\tilde x^k\) 有收敛子列，则 predictor cluster point 满足 slack-variable
  KKT 的 VI 形式；Reviewer `Avicenna` 已给出 `correct_local`。Reviewer `Hume`
  初审 verdict 仍为 `incomplete`。`restricted_y_x_boundedness_sources.md` 已把
  \(x\)-有界性来源拆成 `x_predictor_bounded`、\(X\) compact、原约束矩阵 \(A\)
  full column rank 和 recession gate；Reviewer `Mencius` 已给出 `correct_local`。
  `restricted_y_essential_convergence_theorem.md` 已进一步把 VI/PPC 黑箱改写为
  essential-variable 收敛证明；Reviewer `Maxwell` 已给出 `correct_local`。当前
  restricted \(Y=\mathbb R^n\), z-fixed corrected algorithm 的 essential-variable
  theorem 可标为 `accepted_by_review`，但这不是原始 direct ADMM 收敛证明，也不覆盖一般
  closed convex \(Y\)。
- 一般 closed convex \(Y\) 的文献修正路线已经推进到 accepted theorem：
  `general_y_admg_theorem_candidate.md` 采用 block order \((z,x,y)\) 的 ADM-G，
  在 \(X=\mathbb R^p\)、\(A^TA\succ0\)、\(B^TB\succ0\)、\(\alpha\in(0,1)\) 下证明
  全序列收敛到 KKT/VI solution；Reviewer `Anscombe` 已给出 `correct_local`。
  `general_y_admg_invariant_x_theorem_candidate.md` 进一步把 \(X=\mathbb R^p\) 放宽为
  explicit middle-block invariance：
  \(X-\alpha C_{xy}(Y-Y)\subseteq X\)，Reviewer `McClintock` 已给出 `correct_local`。
  这些结果仍是 modified algorithm，不是原始 direct ADMM theorem，也不覆盖 arbitrary
  closed convex \(X,Y\)。`projected_admg_general_xy_theorem_candidate.md` 已降级为
  `proof_attempt`；`image_space_h_projected_fejer_gate.md` 已由 reviewer `Confucius`
  接受为抽象代数 Fejer gate。最新 `closed_image_and_lift_gate.md` 已由 reviewer
  `Dirac` 审查为 `incomplete`：arbitrary closed convex \(X,Y\) 版本过强。最新
  `image_regular_corrected_theorem_candidate.md` 又经 reviewer `Bacon` 审查为
  `incomplete_predictor_inequality_open`；`image_predictor_inequality_lemma.md` 显示当前
  \(v=(c,z,\lambda)\) scaled-\(Q_P\) route 消去 \(a\)-block 后留下未控交叉项。
  `full_image_state_predictor_route.md` 已优先尝试 full-image-state \(w=(a,c,z,\lambda)\)
  route，并由 reviewer `Chandrasekhar` 接受 predictor inequality 与 \(S_{\rm full}\succ0\)
  gate。`full_image_state_convergence_theorem_candidate.md` 已由 reviewer `Halley` 接受为
  image-regular full-image-state corrected theorem；下一步若继续 arbitrary \(X,Y\)，应处理
  closed value functions、closed image domains、fiber attainment 和 executable selection。
  PCB-ADMM 仍是更强结构假设下的备选。

**输入：**

- `notes/candidate_lyapunov.md`
- `docs/proof_obligations.md`
- `knowledge_base/proof_patterns/*.md`

**任务：**

1. 为最保守且可能成立的猜想写 proof blueprint。
2. 审查 projection firm nonexpansiveness 这一步是否有效。
3. 审查 \(B(y^{k+1}-y^k)\) 与 \(z^{k+1}-z^k\) 交叉项能否被控制。
4. 对失败的证明义务输出 repair hints。

**输出：**

- `proof_reviews/identity_block_lyapunov/proof_blueprint.md`
- `proof_reviews/identity_block_lyapunov/verification_report.json`
- `proof_reviews/identity_block_lyapunov/repair_hints.md`
- `proof_reviews/identity_block_lyapunov/acceptance_gate.md`
- `proof_reviews/vi_ppa_direct_admm/problem_intake.md`
- `proof_reviews/vi_ppa_direct_admm/proof_blueprint.md`
- `proof_reviews/vi_ppa_direct_admm/q_m_h_derivation.md`
- `proof_reviews/vi_ppa_direct_admm/verification_report.json`
- `proof_reviews/vi_ppa_direct_admm/repair_hints.md`
- `proof_reviews/vi_ppa_direct_admm/acceptance_gate.md`
- `proof_reviews/vi_ppc_corrected_algorithm/q_p_predictor_derivation.md`
- `proof_reviews/vi_ppc_corrected_algorithm/restricted_y_unconstrained_theorem.md`
- `proof_reviews/vi_ppc_corrected_algorithm/restricted_y_cluster_kkt_limit.md`
- `proof_reviews/vi_ppc_corrected_algorithm/restricted_y_cluster_kkt_limit_review.md`
- `proof_reviews/vi_ppc_corrected_algorithm/restricted_y_x_boundedness_sources.md`
- `proof_reviews/vi_ppc_corrected_algorithm/restricted_y_x_boundedness_sources_review.md`
- `proof_reviews/vi_ppc_corrected_algorithm/restricted_y_essential_convergence_theorem.md`
- `proof_reviews/vi_ppc_corrected_algorithm/restricted_y_essential_convergence_theorem_review.md`
- `proof_reviews/vi_ppc_corrected_algorithm/gaussian_back_substitution_assumption_match.md`
- `proof_reviews/vi_ppc_corrected_algorithm/pcb_admm_assumption_match.md`
- `proof_reviews/vi_ppc_corrected_algorithm/verification_report.json`

**验收标准：**

- `verification_report.json` 有明确 verdict。
- 所有 gap 都被列成可修复目标。
- acceptance gate 未通过前，不得称为证明完成。

## WO-4：二次型谱半径反例搜索

**使用 skill：** `scientific-computing-reproduction`

**输入：**

- `experiments/slack_admm_core.py`
- `tests/test_slack_admm_core.py`
- `knowledge_base/counterexamples/direct_extension_spectral_radius.md`

**任务：**

1. 推导或实现凸二次 identity-block ADMM 的线性迭代矩阵。
2. 加入 PSD 检查和子问题可解性诊断。
3. 用固定 seed 搜索低维 \(\rho(T)>1\) 实例。
4. 保存候选和 reproduction report。

**输出：**

- `src/admm_identity/quadratic_iteration.py`
- `experiments/search_quadratic_counterexample.py`
- `tests/test_quadratic_iteration.py`
- `outputs/counterexample_candidates.jsonl`
- `outputs/counterexample_report.md`

**验收标准：**

- 测试覆盖维度、PSD 检查、谱半径计算和候选持久化。
- 候选记录 seed、矩阵、beta、\(\rho(T)\) 和复现说明。

## WO-5：Slack Active-Set 反例搜索

**使用 skill：** `scientific-computing-reproduction`，并结合 `admm-proof-workflow`

**当前进展：**

- 第一版 fixed-active-set recurrence scaffold 已完成：
  - `src/admm_identity/slack_projection.py`
  - `experiments/search_slack_active_set_counterexample.py`
  - `tests/test_slack_projection.py`
  - `notes/active_set_effective_recurrence.md`
  - `notes/active_set_reduced_theory.md`
  - `notes/active_set_quotient_reduction.md`
  - `notes/general_active_mask_reduction.md`
  - `notes/multi_agent_fixed_mask_debate.md`
  - `notes/fixed_mask_invariant_impossible_lemma.md`
  - `experiments/search_reduced_map_abstract_expansion.py`
  - `experiments/build_reduced_map_qp_candidate.py`
  - `experiments/analyze_candidate_invariant.py`
  - `experiments/search_fixed_mask_invariant_candidate.py`
  - `experiments/search_active_set_switching_cycle.py`
  - `experiments/optimize_signed_q_tangent.py`
  - `experiments/analyze_near_unit_modes.py`
  - `notes/near_unit_mode_analysis.md`
- 最近运行见 `outputs/wo5_active_set_2026-07-05/RUN_SUMMARY.md`。
- 2D/3D structured all-mask screens 均未找到 effective \(\rho(T_D)>1+10^{-6}\) 且 active region 可保持的 pressure candidate。
- near-unit modes 主要落在 \(z/y\) 分量，几乎没有 \(\lambda\) 分量；`notes/active_set_reduced_theory.md` 已解释 \(D=I\) 时非零特征值对应特征向量必有 \(\xi_\lambda=0\)，`notes/active_set_quotient_reduction.md` 进一步给出 \(D=I\) 的 quotient maps \(M_x,M_y\)，说明 PSD 情形下这些 near-unit modes 不产生谱扩张。
- `notes/general_active_mask_reduction.md` 已给出一般 \(D\ne I\) 的 complementarity reduced map \(R_D\)，并由测试验证 \(R_D\) 保留 \(T_D\) 的非零谱。coordinatewise/commuting 情形已证明 \(\rho(R_D)\le1\)。fixed-mask 正实扩张已由 `notes/fixed_mask_invariant_impossible_lemma.md` 与 `proof_reviews/fixed_mask_impossible/` 排除为局部模型定理；当前 QP candidate 的 affine switching cone screen 长度 `2..10` 未找到 expansion。二维 length-2 nonconstant switching 已完成 proof-first chain：`PC-0` symmetry、`zero_full`、`zero_single`、`single_full` 与 `single_single` 均已通过本地 review，最终 `SC-1` assembly 已由 `proof_reviews/sc1_length2_nonconstant_pairs/` 接受。下一步不要继续普通 numerical screen；原算法分支应研究 length-3 / arbitrary switching、common seminorm 或更高维 active-mask obstruction。
- `outputs/wo5_active_set_2026-07-05/zero_single_relative_angle_symbolic_sublemma.md` 已把 relative-angle 路线固化成 exact symbolic artifact：`Qplus D` 的 rank-one quotient 无负 power-basis 系数，`Qconst_minus D` 的 AM-GM remainder 无负 power-basis 系数。该结果本身只闭合 rank-one projector 边界；`Qconst_minus` 的邻域已由后续 weighted Bernstein certificate 补齐，`Qplus` 也已由后续 depth-2 covering 与 full-chain review 补齐。
- `outputs/wo5_active_set_2026-07-05/zero_single_qconst_boundary_neighborhood.md` 已把 `Qconst_minus` 的 exact Bernstein 失败定位到四个角点邻域：depth `3` 时 `64` 个 dyadic boxes 中 `60` 个闭合，剩余 `4` 个正是角点 boxes。
- `outputs/wo5_active_set_2026-07-05/zero_single_qconst_corner_eigen_localization.md` 已在四个角点 boxes 内继续二分 eigenvalue variables：每个角点 `16` 个 eigenvalue boxes 中 `15` 个闭合，唯一坏盒正是匹配的 rank-one projector box。
- `outputs/wo5_active_set_2026-07-05/zero_single_qconst_minus_weighted_bernstein_certificate.md` 已用 weighted Bernstein certificate 闭合最后四个 rank-one projector boxes：四个 case 均满足 `F_bad=H_bad=-1/1024`、`scale=1`、`remainder_negative_count=0`。该证书已由 `proof_reviews/zero_single_qconst_minus/` 接受为 local theorem。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_psd_route.md` 已把 `Qplus` 改写为 `det(sym(I-L)) + skew^2` 的 PSD route。该输出只是 proof obligation rewrite，还不是 closed certificate。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_psd_minor_diagnostics.md` 已检查 `S11`、`S22` 主子式：`A` components 由 angle bisection 闭合，`D` components 各剩四个角点坏盒；直接 `det(S)` 展开过重，因此下一步应走相对角 / determinant-plus-square 结构而不是直接主子式蛮算。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_exact_obstruction_gate.md` 已用 exact rational grid 检查 `S11`、`S22`、`detS`、`skew_sq` 和 `Qplus`；默认 `30625` 个有理点没有发现 PSD route failure 或 margin failure，classification 为 `certificate_failure_only`。这不是证明，只是排除一批 exact obstruction。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_relative_angle_localization.md` 已对 `Qplus D` 做 dyadic Bernstein localization：depth `1..3` 的坏盒精确匹配 `s=t` 与 `s+t=1` 两条 relative-angle strips。该输出不是 closed certificate，但说明下一步应做 strip-neighborhood coordinate blow-up / weighted Bernstein，而不是 Qconst 风格的角点-only 证书或普通 subdivision。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_strip_boundary_certificate.md` 已闭合 `s=t` 与 `s+t=1` 两条 strips 本身：`A` 和 `D` 限制到两条 strips 后，单盒 Bernstein 仍有负系数，但对 strip parameter `s` 二分一次即可全部非负。该证书不闭合 strip neighborhoods 或 full two-angle interior。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_strip_neighborhood_charts.md` 已把两条 strips 的邻域拆成四个三角 chart：`diag_lower`、`diag_upper`、`anti_lower`、`anti_upper`。`A` 分量在 depth `1` 闭合，`D` 分量在 depth `2` 时每个 chart 仍剩 `5` 个 bad boxes。下一步应针对这些 bad boxes 构造 endpoint-weighted control 或局部 determinant-plus-square certificate，不要退回普通 subdivision。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_badbox_endpoint_support.md` 已分析这些 `D` bad boxes 的负 Bernstein support：每个 chart 的 `707` 个负系数中 `704` 个落在两个 rank-one endpoint slabs 上，剩余 `3` 个是相邻 endpoint index。下一步优先尝试 multi-control endpoint-weighted `F=H+R`，失败后再走局部 determinant-plus-square certificate。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_endpoint_control_search.md` 已对四个代表 bad boxes 做 simple endpoint-weighted AM-GM 单控制搜索：top endpoint signatures、exponents `{2,3,4}` 和前 `20` 个 controls 均未找到 feasible scale。该结果只排除这一有限候选族，不排除 multi-control linear feasibility 或局部 determinant-plus-square certificate。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_multicontrol_feasibility.md` 已把四个代表 bad boxes 写成 LP-guided multi-control `F=sum_j gamma_j H_j+R` 搜索：`H_j` 使用 chart-specific rank-one slab weights 与 top negative endpoint signature weights 乘 `X^2+Y^2-X*Y`，LP feasible 只算候选，必须有理化后 exact Bernstein remainder 非负才算局部证书。当前全 `78` 个 low-degree angle controls 在 `4` 个代表 boxes 上得到 `0` 个 LP feasible box 和 `0` 个 exact certificate box；这只说明该有限候选族不足，不是 `Qplus` 反例。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_slab_residual_multicontrol_feasibility.md` 已加入 slab 外自由变量的 degree-1 residual weights，并用前 `12` 个 low-degree angle controls 检查四个代表 bad boxes；结果仍为 `0/4` LP feasible、`0/4` exact certificate。该结果继续只说明有限候选族不足。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_det_square_badbox_diagnostic.md` 已在同一批代表 bad boxes 上做 `Qplus=det(sym(I-L))+skew_sq` exact rational-grid diagnostic；`567` 个 samples 中 `detS` negative count 和 `Qplus` negative count 均为 `0`。这不是证明，但提示下一步应优先尝试局部 exact `det(S)` certificate；若后续发现 `detS<0` 但 `Qplus>=0`，再使用 `skew_sq` square reserve。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_local_det_square.md` 已把 `det(S)` 的 parity gate 投到同一批四个代表 bad boxes：`detS_A` 全部 exact Bernstein 闭合，但 `detS_D=A0^2-u*v*B0^2` 全部未闭合，负 Bernstein 系数为 `1740/1740/2797/1740`。这说明 naive local `det(S)` parity certificate 不足，不是负值 witness。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_detS_support.md` 已分析同一批四个代表 bad boxes 中 `detS_D` 的负 Bernstein support：`8017` 个负系数中 `8006` 个精确落在 rank-one endpoint slabs 上，`8007` 个落在 near-slab 上；`anti_lower` 是唯一带少量外侧样本的 chart。该结果仍不是 certificate，但把下一步 factor/residual controls 收窄到 endpoint-slab 结构。
- `notes/zero_single_qplus_endpoint_slab_theory.md` 已把 `Qplus` 义务改写成理论证明路线：先使用 `Qplus=det(sym(I-L))+skew^2` 的二维恒等式判断 square reserve 是否可直接闭合；再对 `diag_lower`、`diag_upper`、`anti_upper` 建 endpoint-slab factor/residual 引理；最后单独处理 `anti_lower` 的 zero-endpoint quarantine。后续脚本只能作为恒等式、候选分解和 exact remainder 非负校验，不作为主线 screen。
- `notes/zero_single_qplus_square_reserve_local_lemma.md` 已将下一步改成更具体的局部命题：不要先证明过强的 `det(S)>=0`，而是在四个代表 strip-neighborhood bad boxes 上保留 \(K^2\) reserve，尝试显式有理分解 \(F_B=K_B^2+\sum_j\gamma_jW_jC_j+R_B\)，并用 exact Bernstein coefficients 证明 \(R_B\ge0\)。
- `experiments/search_zero_single_qplus_square_reserve_local_certificate.py` 已建立直接 `Qplus D` 的 sparse-support local certificate scaffold，输出 `outputs/wo5_active_set_2026-07-05/zero_single_qplus_square_reserve_local_certificate.md`。first-pass `diag_lower` depth-1 一个代表盒没有 LP feasible，只排除极小控制族；该结果不是反例。
- `experiments/certify_zero_single_qplus_square_reserve_local.py` 将同一路线推进到 `diag_lower` depth-2 代表盒 `(2,1)`：基础版 `112` 个 endpoint/strip-normal controls 与加强版 `634` 个 controls 均 LP infeasible。该结果只排除两个有限直接控制族；下一步应实现显式 \(K_B^2\) / sign-aware square split，而不是继续堆同类 LP controls。
- `experiments/analyze_zero_single_qplus_explicit_square_split.py` 已完成显式 split scaffold：共同分母下 `4*C*Qplus_num = detS_num + K_num^2`、A/B parity identities 和 `K_num=xP(u,v)+yR(u,v)` 均 exact 成立。输出 `outputs/wo5_active_set_2026-07-05/zero_single_qplus_explicit_square_split.md` 只固化代数骨架，不是非负证明；下一步应让 local certificate 脚本消费这些 split components。
- `experiments/certify_zero_single_qplus_partial_square_remainder.py` 已把 explicit split 接到第一个 partial-square local gate：在 `diag_lower` depth-2 代表盒 `(2,1)` 上，`alpha=1/2` 时 `A_alpha` exact Bernstein 负系数为 `0`，但 `D_alpha` 仍有 `1738` 个负 Bernstein 系数，故没有局部证书。这只排除该无-control partial-square split，不是 `Qplus` 反例。
- `experiments/certify_zero_single_qplus_sign_aware_square_gate.py` 已把 explicit split 接到 sign-eliminated fixed-source gate：在 `diag_lower` depth-2 代表盒 `(2,1)` 上，`F_A` exact Bernstein 负系数为 `0`，固定 \(D_K=(uP^2-vR^2)^2\) 的 identity residual 为 `0`，但 `D_F-D_K` 仍有 `1738` 个负 Bernstein 系数；极小 endpoint/strip-normal 控制族 `4` controls 的 active LP infeasible。该结果只排除当前固定源 + 小控制族，不是 `Qplus` 反例。
- `proof_reviews/qplus_theory_rebalance/` 已把当前“实验偏多”的问题改成 proof-blueprint 约束：全局 Lyapunov 线只接受为 `incomplete`，base-algorithm 分支下一步优先证明 `diag_lower` 的 fixed-source remainder \(G=D_F-D_K\) strip-normal / endpoint-slab 分解。该目录的 `verification_report.json` verdict 为 `incomplete`；`current_gate_alignment.md` 明确 \(D_\alpha\) 只是前置诊断，当前主对象是 \(G\)；`endpoint_slab_attempt.md` 已排除 predecessor \(D_\alpha\) 的 direct endpoint-face Bernstein / 一次 bisection 路线。
- `experiments/analyze_zero_single_qplus_fixed_remainder_faces.py` 已把当前 \(G=D_F-D_K\) 直接限制到 `diag_lower` 代表盒的两个 endpoint faces：两个 faces 各有 `869` 个负 Bernstein coefficients，strip \(r=1\) faces 各有 `134` 个；两条 joint lower strip edges 含 \((3a-2)^2\) 且 square quotient Bernstein 负系数为 `0`，但 simple strip-lift quotient 在 \(a=3/4,r=3/4\) 有 exact 负值 witness。该 artifact 排除 direct endpoint-face Bernstein 和 simple strip-lift 路线，不是 `Qplus` 负值 witness；后续以 joint edge 因子证书作为新的 base lemma。
- `notes/zero_single_qplus_joint_edge_factor_lemma.md` 已把上述两条二维 joint lower edges 进一步闭合：\(G_{\rm edge}=-(ar+5a+2r-6)^2P(a,r)/2^{28}\)，并且两条 edge 的 \(-P\) exact Bernstein 负系数均为 `0`。这说明 simple strip-lift 失败不代表 edge 未闭合；下一步应把该平方因子向 single-zero edge / endpoint face lift。
- `notes/zero_single_qplus_single_zero_factor_lemma.md` 已把同一结构提升到四条 single-zero edges：\(G_{\rm single}=-(ar+5a+2r-6)^2(1-\tau)^2P(a,r,\tau)/2^{28}\)，四条 edge 的 \(-P\) exact Bernstein 负系数均为 `0`。下一步应把该平方结构向完整 endpoint face lift。
- `notes/zero_single_qplus_endpoint_face_factor_lemma.md` 已把两个 endpoint faces 闭合：\(G_{\rm face}=-(ar+5a+2r-6)^2P(a,r,\eta,\tau)/2^{28}\)，两个 face 的 \(-P\) exact Bernstein 负系数均为 `0`。完整 6D local box 不由该因子直接整除，下一步应做 face-to-interior lift。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_face_to_interior_hermite_gate.md` 已检查简单 Hermite lift：`m2=1,n1=1` face 的两个一阶 normal quotients 有 exact 负值 witness，故不要把 \(A,B,H\ge0\) 的 Hermite lift 作为主线；下一步应走 top-slice endpoint-face lift 或 paired-slab AM-GM block。
- `notes/zero_single_qplus_top_slice_lift_certificate.md` 已闭合 `diag_lower` depth-2 代表盒 `(2,1)`：\(G=m_1^2n_2^2C_{12}+m_2^2n_1^2C_{21}+R_2\)，其中 \(R_2\) exact Bernstein 负系数为 `0`。该证书只覆盖该代表盒；下一步应推广到其他 chart 代表盒或全部 depth-2 bad boxes。
- `notes/zero_single_qplus_top_slice_representative_extension.md` 已检查四个 chart 代表盒：`diag_lower`、`diag_upper`、`anti_upper` 均由 \(p=2,\gamma=1\) top-slice 证书闭合；`anti_lower (0,0)` 由 `notes/zero_single_qplus_anti_lower_quarantine_theory.md` 与 `outputs/wo5_active_set_2026-07-05/zero_single_qplus_anti_lower_endpoint_controls.md` 闭合。具体为 \(G=m_1^4n_1^4C_{11}+m_2^4n_2^4C_{22}+R_4\)：\(R_4\) 由 zero-endpoint face 和 \(p=2\) normal lift 闭合；\(C_{11},C_{22}\) 由 endpoint-control 的分片 relative-angle strip 证书闭合。因此四个代表盒均已有局部证书。后续已整合到全部 depth-2 bad boxes，并由 `notes/zero_single_qplus_full_chain_review.md` 接回完整 `Qplus` margin。
- `notes/zero_single_qplus_depth2_covering_blueprint.md` 与 `proof_reviews/qplus_depth2_covering/` 已把“实验偏多”的问题改成新的 proof-first gate。随后 `notes/zero_single_qplus_diag_lower_depth2_covering.md`、`notes/zero_single_qplus_diag_upper_depth2_covering.md`、`notes/zero_single_qplus_anti_upper_depth2_covering.md` 和 `notes/zero_single_qplus_anti_lower_depth2_covering.md` 闭合了四个 chart 的全部 depth-2 `D` bad boxes。当前进度为 `20/20`，总装审查见 `notes/zero_single_qplus_depth2_covering_assembly_review.md`。`proof_reviews/qplus_depth2_covering/verification_report.json` verdict 已升级为 `correct_for_depth2_covering_lemma`；`notes/zero_single_qplus_full_chain_review.md` 已进一步将该 local theorem 接回完整 `Qplus` margin；该结论仍不是 ADMM 收敛证明。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_detS_endpoint_control_search.md` 与 `outputs/wo5_active_set_2026-07-05/zero_single_qplus_detS_endpoint_geometry_control_search.md` 已测试 `detS_D` 的 bounded single-control endpoint-slab family：degree-8 baseline 与 `{7,8}` near-slab geometry controls 在四个代表盒上均为 `0/4` feasible。该结果只排除有限 single-control 族，不是 `Qplus` 反例；下一步若继续 endpoint route，应转向 multi-control。
- multi-agent 审查确认：`Qplus` 没有 exact obstruction，直接主子式 PSD route 更像坐标证书不适配；`Qconst_minus` 的 corner route 已由 weighted Bernstein certificate 实现；`single_single` 不能复用二次降阶，后续需要独立 cubic Jury/Bernstein artifact。
- `notes/length3_switching_gate.md` 已建立 `SC-1` 之后的下一层 proof gate：length-2 pairwise spectral nonexpansion 不能在无 common seminorm 时推出 length-3；length-3 非恒定 words 共 `60` 个，按 cyclic shift 和二维坐标交换归为 `11` 类，枚举见 `outputs/wo5_active_set_2026-07-05/length3_switching_classes.md` 与 `outputs/wo5_active_set_2026-07-05/results/length3_switching_classes.json`。该输出是 `combinatorial_enumeration`，不是数值 screen 或 theorem。
- `experiments/symbolic_length3_switching_products.py` 已闭合 `L3-1a` determinant-zero lemma：单步 determinant 只有 full mask `[1,1]` 可能非零，而非恒定 length-3 word 至少含一个 non-full mask，所以全部 `11` 个 canonical classes 的 product determinant 都为 `0`。输出见 `outputs/wo5_active_set_2026-07-05/length3_switching_symbolic_check.md` 和 `outputs/wo5_active_set_2026-07-05/results/length3_switching_symbolic_check.json`。该结果只降到剩余 cubic factor，不是 length-3 nonexpansion theorem。
- `experiments/symbolic_length3_cubic_coefficients.py` 已完成 `L3-1b` exact coefficient extraction：对全部 `11` 个 canonical classes 写出 `det(tI-P)=t(t^3+a1*t^2+a2*t+a3)` 中的 `a1,a2,a3`。完整 expressions 写入 `outputs/wo5_active_set_2026-07-05/results/length3_cubic_coefficients.json`，摘要见 `outputs/wo5_active_set_2026-07-05/length3_cubic_coefficients.md`。当前最大 `a3` 长度为 `161665`，说明下一步要做结构化 margin / exterior-power / common-seminorm gate，而不是人工读公式。
- `experiments/symbolic_length3_jury_margins.py` 已完成 `L3-2a` margin scaffold：对全部 `11` 个 canonical classes 构造 `J+`、`J-`、`Jmid`、`Jconst_upper/lower` 的 expression metadata，输出见 `outputs/wo5_active_set_2026-07-05/length3_jury_margins.md` 和 `outputs/wo5_active_set_2026-07-05/results/length3_jury_margins.json`。当前最大 `Jmid` 长度为 `347008`，该结果仍不是非负证书。
- `experiments/certify_length3_coordinatewise_bernstein.py` 已闭合 `L3-2b-coordinatewise`：对 coordinatewise 标量 active/inactive blocks 的全部 `8` 个 length-3 words，`J+`、`J-`、`Jconst` 的 degree `(3,3)` Bernstein coefficients 全部非负。输出见 `outputs/wo5_active_set_2026-07-05/length3_coordinatewise_bernstein_certificate.md` 和 `outputs/wo5_active_set_2026-07-05/results/length3_coordinatewise_bernstein_certificate.json`。这是 simultaneous diagonalization / coordinatewise 子定理，不是非交换二维完整 theorem。
- `experiments/analyze_length3_rank_one_projector_boundary.py` 已推进 `L3-2c-rank-one-projector`：在 \(M=vv^\top/\|v\|^2\)、\(N=ww^\top/\|w\|^2\) 的 finite affine slope chart 中，全部 `11` 个 canonical length-3 classes 的 characteristic polynomial 已 exact 分解。去掉零根和允许的单位根后，剩余次数为 `6` 个一次、`4` 个二次、`1` 个三次；全部 6 个一次 residual classes 已由 \(S=x^2+y^2,u=xy\) 改写、显式正项和 exact Sturm 无实根检查闭合；4 个二次 residual classes 已由 \(S,u\) half-domain split、AM-GM / square controls 与 half-line Sturm 检查闭合；`L3C08` 三次 residual 的五个 cubic margins 已由 \(U=\alpha^2,V=\beta^2\) 降维、`U=rV` 系数证书和 `Jminus` 两段分组证书闭合。projective infinity 由齐次 rank-one projector 参数和谱半径连续性闭合。输出见 `outputs/wo5_active_set_2026-07-05/length3_rank_one_projector_boundary.md` 和 `outputs/wo5_active_set_2026-07-05/results/length3_rank_one_projector_boundary.json`。当前 rank-one projective boundary 已闭合 `11/11` 个 canonical classes。该结论只是 rank-one projector boundary 子定理，不是完整 `L3-2c` theorem。
- `experiments/analyze_length3_scaled_rank_one_scaffold.py` 已建立 `L3-2d-scaled-rank-one` 的 exact scaffold：对 \(M=mP_x,N=nP_y,0\le m,n\le1\)，释放 `m,n` 后 residual degree 分布为 `10` 个二次和 `1` 个三次（`L3C08`）。输出见 `outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_scaffold.md` 和 `outputs/wo5_active_set_2026-07-05/results/length3_scaled_rank_one_scaffold.json`。这只是 `proof_obligation_scaffold`，不是 theorem，也不是 counterexample。
- `experiments/certify_length3_scaled_rank_one_l3c07.py` 已闭合 `L3-2d` 的第一个 scaled rank-one canonical class `L3C07=[0,0]->[1,1]->[1,1]`。输出见 `outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c07_certificate.md` 和 `outputs/wo5_active_set_2026-07-05/results/length3_scaled_rank_one_l3c07_certificate.json`。证书路线是 \(S=x^2+y^2,u=xy\) 半域分解 + `(m,n)` degree `(3,3)` Bernstein；三个 quadratic Schur/Jury margins 全部闭合。该结论只覆盖 `L3C07`，不是完整 scaled rank-one theorem。
- `experiments/certify_length3_scaled_rank_one_su_classes.py` 已把同一 \(S,u\) 半域 + `(m,n)` Bernstein 模板批量应用到 `10` 个二次 residual classes，并闭合 `L3C02` 与 `L3C07`。输出见 `outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_su_certificates.md` 和 `outputs/wo5_active_set_2026-07-05/results/length3_scaled_rank_one_su_certificates.json`。其余 `8` 个二次类为 `su_symmetry_unavailable`，这只是说明当前模板不适用，不是反例。
- `experiments/certify_length3_scaled_rank_one_l3c11_discriminant.py` 已闭合非对称 scaled rank-one canonical class `L3C11=[[0,1],[1,1],[1,1]]`。输出见 `outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c11_discriminant_certificate.md` 和 `outputs/wo5_active_set_2026-07-05/results/length3_scaled_rank_one_l3c11_discriminant_certificate.json`。证书路线是把三个 quadratic Schur/Jury margins 写成 \(Ax^2+Bx+C\)，再用 \(v=y^2\)、`(m,n)` Bernstein 证明 \(A\ge0\)、\(C\ge0\)、\(4AC-B^2\ge0\)。该结论只覆盖 `L3C11`，不是完整 scaled rank-one theorem。
- `experiments/certify_length3_scaled_rank_one_l3c05_parity.py` 已闭合 scaled rank-one canonical class `L3C05=[[0,0],[0,1],[1,1]]`。输出见 `outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c05_parity_certificate.md` 和 `outputs/wo5_active_set_2026-07-05/results/length3_scaled_rank_one_l3c05_parity_certificate.json`。证书路线是 \(E+xyO\) parity gate、\(X,Y\) compactification、4D Bernstein，以及 `Jplus` 的 `m=n=1` endpoint factor。该结论只覆盖 `L3C05`，不是完整 scaled rank-one theorem。

**输入：**

- `notes/z_projection_identity.md`
- `experiments/spectral_radius_search.py`
- `knowledge_base/counterexamples/direct_extension_spectral_radius.md`

**任务：**

1. 形式化 \(z\)-projection 和 active-set map。
2. 对固定 active set 构造局部线性或仿射映射。
3. 搜索局部谱半径大于 1 的 active set。
4. 检查生成轨道是否留在同一个 active region。
5. `PC-2 zero_single` 的 `Qplus` 已由 `notes/zero_single_qplus_full_chain_review.md` 接受；`Qconst_minus` 已由 `proof_reviews/zero_single_qconst_minus/` 接受。不要新增普通随机/网格 screen。
6. `PC-2 zero_single` canonical representative 已由 `proof_reviews/zero_single_pc2/` 接受，`zero_single` ordered class 已由 `proof_reviews/zero_single_ordered_class/` 接受；`PC-1 zero_full` canonical representative 和 ordered class 已由 `proof_reviews/zero_full_pc1/`、`proof_reviews/zero_full_ordered_class/` 接受；`single_single` 的 `Jconst_minus/Jconst_plus` 已由 `proof_reviews/single_single_jconst_margins/` 接受，`Jminus` 已由 `experiments/certify_single_single_jminus_full_domain.py` 闭合，`Jplus A` 已由 `(s,t)` depth-1 dyadic probe 闭合，`Jplus D` 的 top-slice / corner-reserve lift 已由 `proof_reviews/single_single_jplus_top_slice_lift/` 接受；`Jmid` 已由 parity gate + exact Bernstein certificate 闭合，并已由 `proof_reviews/single_single_jmid_bernstein/` 接受；canonical representative assembly 已由 `proof_reviews/single_single_canonical_assembly/` 接受，ordered class 已由 `proof_reviews/single_single_ordered_class/` 接受。`SC-1` length-2 nonconstant pairs assembly 已由 `proof_reviews/sc1_length2_nonconstant_pairs/` 接受。下一步在原算法分支应研究 length-3 / arbitrary switching；VI/PPA/PPC 方向不要混入该原算法 proof chain，它作为 corrected-algorithm / prediction-correction repair route 另开分支。
7. length-3 的旧 \(R_D\)-product 线已闭合 Stage 4G 的 `55/55` 个 Schur/Jury margins；`TS-1` 已由 true/legacy closed-word characteristic-polynomial transfer review 关闭。`TS-2` 的 canonical 半开 edge cells、edge iff、closed-word pullback 与周期等式已由最终独立 review 接受。`TS-3` affine homogeneous transfer 也已由 follow-up review 接受：任意有限 closed word 有齐次 characteristic-polynomial transfer，且可逆 \(\widehat Q\) 时有 affine conjugacy。奇异 \(\widehat Q\) 不搬运 Jordan/fixed points；非方阵 \(B\) 不继承旧 Stage 4G 谱界。当前必须为具体有理 QP/word 生成 exact admissibility 或 Farkas certificate，再按真实 cells 进入 cone-restricted Lyapunov 或 Jordan/affine-drift 红队；严格反例仍须 exact/interval growth、无限轨道 admissibility 与 slack-QP embedding。
8. 脚本只允许校验已写出的候选 lemma；不能把 all-box exact gate、LP infeasibility 或 bad Bernstein coefficients 误称为 `Qplus` 反例。即使 `Qplus` 局部证明链后续闭合，也不能自动声称全局 ADMM 收敛。

**输出：**

- `src/admm_identity/slack_projection.py`
- `experiments/search_slack_active_set_counterexample.py`
- `tests/test_slack_projection.py`
- `outputs/slack_counterexample_report.md`

**验收标准：**

- 报告明确区分 active-set screen 与 proof-grade counterexample。
- 每个候选都记录 active set 和 stay-in-region 检查。

## WO-5B：VI/PPC 修正算法路线

**使用 skill：** `proof-blueprint-review`，并结合 `admm-proof-workflow`

**当前进展：**

- `proof_reviews/vi_ppa_direct_admm/` 已实例化 direct slack ADMM 的 `Q,M,H,G`，
  reviewer 接受推导，但 verdict 为 `direct_vi_ppa_condition_failure`。
- 失败原因是原始 direct route 的 `G_slack` 有负方向，无法吸收
  \(\langle B\Delta y,\Delta z\rangle\)。
- `notes/vi_ppc_corrected_algorithm_route.md` 已把 VI/PPC 保留为 corrected-algorithm
  proof plan，而不是原算法证明。
- `proof_reviews/vi_ppc_corrected_algorithm/` 已建立 proof-review 包。当前
  `q_m_h_g_derivation.md` 给出 z-fixed matrix gate：构造 \(W=H^{-1}\) 和
  \(M_{\rm corr}=WQ_P\)，使 \((M_{\rm corr})_z=[0,I,0]\)，并在 \(P_y\succ0\)、
  \(R,E\succ0\) 足够小时通过 Schur complement 得到 \(G\succeq0\)。`y_feasibility_or_image_space_gate.md` 已说明该 affine correction
  不保持一般 closed convex \(Y\)，只能支持 \(Y=\mathbb R^n\)、不变 affine \(Y\)
  或另行证明 image-space executability 的限制版路线。限制版 \(Y=\mathbb R^n\) theorem
  已由 `restricted_y_essential_convergence_theorem.md` 接受；一般 closed convex \(Y\)
  已由 `general_y_admg_theorem_candidate.md` 的 ADM-G modified algorithm 接受，但要求
  \(X=\mathbb R^p\)；`general_y_admg_invariant_x_theorem_candidate.md` 已接受
  \(X-\alpha C_{xy}(Y-Y)\subseteq X\) 的 invariant-\(X\) 扩展。`full_image_state_convergence_theorem_candidate.md`
  已由 reviewer `Halley` 接受为 image-regular full-image-state corrected theorem：
  image variables 全序列收敛，fiber attainment 下可 conditional lift 为 primal KKT。

**任务：**

1. 从具体 proximalized prediction 子问题推导 \(Q_P\)。
2. 已接受限制版 theorem：在 \(Y=\mathbb R^n\) 下使用 z-fixed convergence proof。
3. 已接受一般 \(Y\) theorem：在 \(X=\mathbb R^p\) 下使用 Gaussian back substitution
   / ADM-G。
4. 已接受 invariant-\(X\) theorem：在
   \(X-\alpha C_{xy}(Y-Y)\subseteq X\) 下使用同一 block-order ADM-G。
5. 不允许把 z-fixed matrix gate、ADM-G 或 invariant-\(X\) theorem 误报为原始
   general-\(Y\) direct slack ADMM 收敛证明。
6. `image-regular` full-image-state corrected theorem 已接受；若继续 simultaneous
   arbitrary closed convex \(X,Y\)，下一步不再是 Fejer 代数，而是证明或替换
   closed value functions、closed image domains、fiber attainment 和 executable selection。

**输出：**

- `proof_reviews/vi_ppc_corrected_algorithm/problem_intake.md`
- `proof_reviews/vi_ppc_corrected_algorithm/proof_blueprint.md`
- `proof_reviews/vi_ppc_corrected_algorithm/q_m_h_g_derivation.md`
- `proof_reviews/vi_ppc_corrected_algorithm/restricted_y_essential_convergence_theorem.md`
- `proof_reviews/vi_ppc_corrected_algorithm/general_y_admg_theorem_candidate.md`
- `proof_reviews/vi_ppc_corrected_algorithm/general_y_admg_theorem_candidate_review.md`
- `proof_reviews/vi_ppc_corrected_algorithm/general_y_admg_invariant_x_theorem_candidate.md`
- `proof_reviews/vi_ppc_corrected_algorithm/general_y_admg_invariant_x_theorem_candidate_review.md`
- `proof_reviews/vi_ppc_corrected_algorithm/projected_admg_general_xy_theorem_candidate.md`
- `proof_reviews/vi_ppc_corrected_algorithm/projected_admg_general_xy_theorem_candidate_review.md`
- `proof_reviews/vi_ppc_corrected_algorithm/image_space_projected_correction_gate.md`
- `proof_reviews/vi_ppc_corrected_algorithm/image_space_h_projected_fejer_gate.md`
- `proof_reviews/vi_ppc_corrected_algorithm/image_space_h_projected_fejer_gate_review.md`
- `proof_reviews/vi_ppc_corrected_algorithm/full_image_state_convergence_theorem_candidate.md`
- `proof_reviews/vi_ppc_corrected_algorithm/full_image_state_convergence_theorem_candidate_review.md`
- `proof_reviews/vi_ppc_corrected_algorithm/corrected_algorithm_route_matrix.md`
- `proof_reviews/vi_ppc_corrected_algorithm/verification_summary.md`
- `proof_reviews/vi_ppc_corrected_algorithm/proof_obligation_patches.json`
- `proof_reviews/vi_ppc_corrected_algorithm/verification_report.json`
- `proof_reviews/vi_ppc_corrected_algorithm/acceptance_gate.md`

**验收标准：**

- 明确证明对象是修正算法，不是原始 direct slack ADMM。
- `verification_report.json` 必须审查 \(G\succeq0\)、projection feasibility 和下降不等式。
- 若任何矩阵条件失败，标为 `incomplete`，不能改写成原算法收敛结论。

## WO-6：搜索器改进

**使用 skill：** `openevolve-experiment-workflow`

**启动条件：** 只有 WO-4 或 WO-5 已经有可运行 evaluator 后才启动。

**任务：** 改进反例搜索器，寻找更小、更简单、更容易复现的候选。

**输出：**

- `outputs/evolving_runs/<run_id>/config.yaml`
- `outputs/evolving_runs/<run_id>/best_candidate.json`
- `outputs/evolving_runs/<run_id>/metrics.json`
- `outputs/evolving_runs/<run_id>/reproducibility.md`

**验收标准：**

- 不提交 API key 或大日志。
- best candidate 能被非 evolving 脚本复现。

## 2026-07-12：WO-5 理论暂停节点

本轮完成了一个可审查的 theory increment，而不是普通数值筛查：

- notes/general_ab_small_gain_phase_gate.md：从原始 direct slack ADMM 的 reduced recurrence
  推导任意有限维 A、B 的 block comparison gate；
- experiments/breakthrough/certify_general_ab_small_gain.py：用有理算术重建非方阵
  B 的 QP，并精确检查 16 条 source-target edges；
- outputs/breakthrough_attempts/stage20_general_ab_small_gain/：机器证书与中文报告；
- tests/test_general_ab_small_gain.py：定向测试 4 passed，相关 phase/small-gain 测试合计
  39 passed。
- notes/selector_iqc_global_mask_condition.md：用一个对角乘子 LMI 替代指数级 mask
  norm 枚举；两名独立 reviewer follow-up verdict 均为 correct；
- notes/selector_iqc_diagonal_lossless.md：证明在固定 orthant 坐标的对角 G 情形无损，
  Stage 22 覆盖三个乘子分支；独立 reviewer 最终 verdict 为 `correct`；
- Stage 21/22 相关定向回归当前为 40 passed，JSON 均为 exact rational/symbolic 证据。
- notes/selector_iqc_nonnormal_robust_neighborhood.md：用显式扰动界把严格对角 IQC
  基点扩张到非正规 (G)，Stage 23 给出可由非交换 (M,N) 实现的 exact 有理见证；
  独立 reviewer verdict 为 `correct`。
- notes/fixed_qp_signed_pwa_contraction_theorem.md：构造旧 SG gate 外的固定有理 QP，
  从原 ADMM 推导 signed-state 连续 PWA recurrence，并用共同
  \(H=\operatorname{diag}(I,9I/4)\)、\(\gamma=99/100\) exact 证明全局增量收缩；
  fixed-point/KKT 双向桥及任意初值全局几何收敛已由两条独立 review 接受。
- notes/fixed_qp_signed_pwa_affine_family_theorem.md：证明任意 rhs/一次项只产生共同 affine
  offset，并将定理扩张到 \(\|M-M_0\|,\|N-N_0\|\le1/100\) 的显式开放邻域；
  Stage 26 exact 余量为 \(405667/3125000\)，两条独立 review 均为 `correct`。

范围裁决：该门只给出 b=0、强凸二次目标下的充分收敛条件；门失败不等于 direct
ADMM 发散。标量 exact boundary red-team 已确认 comparison 单位根可以与算法实际收敛
同时出现。下一次恢复时优先研究一般非交换高维的 phase/cone 度量或 proof-grade
active-itinerary 反例，不回到普通随机筛查。

## WO-7：汇报与写作

**使用 skill：** `paper-writing`

**输入：**

- 已审查的 literature report
- 已审查的 proof report
- reproduction reports
- `research_state.md`

**任务：**

1. 生成阶段性周报。
2. 生成技术 memo。
3. 只基于 reviewed artifacts 起草 working paper。

**输出：**

- `outputs/week_report.md`
- `outputs/admm_identity_memo.md`
- `workspace/final/working_paper.md`

**验收标准：**

- 每个结论都能追溯到 source artifact。
- 开放证明义务和失败路线保持可见。
- 实验结论包含 command、seed 和 output path。

## 2026-07-14：WO-5 终点更新

WO-5 已达到比“继续寻找 candidate”更强的终点：

- `notes/strict_rational_66_cycle_counterexample.md` 给出二维、$A=B=I$、纯强凸二次目标的
  bounded non-KKT 66-cycle；
- word 为 `00^2 01^64`，所有 132 个投影符号不等式 strict，统一余量大于 $1/1000$；
- `experiments/breakthrough/certify_strict_rational_66_cycle.py` 用 exact rational arithmetic
  重验 strong convexity、KKT、period closure、signed recurrence 和原始 ADMM 四步更新；
- Stage 44 certificate 的 `valid=true`；定向测试通过；
- adversarial review verdict 为 `ship with mitigations`，mitigations 是始终写明
  “bounded periodic nonconvergence”与“尚无外部独立 reviewer”。

因此 WO-5 的“proof-grade counterexample”验收门已经满足；旧文本中“当前没有 strict
counterexample”的描述全部作废。WO-5 后续若继续，只允许两个方向：

1. 找更短/更简单的 exact 周期反例；
2. 提炼能排除 Stage 44 机制的最小附加收敛条件。

不得再把原始 general direct slack ADMM 的无条件收敛证明列为开放且可成立的目标。

补充验收：Stage 45 已用六维 full-state raw ADMM 第二实现重验 Stage 44，不导入原 checker，
也不使用其 signed recurrence。输出为
`outputs/breakthrough_attempts/stage45_independent_raw_admm_audit/certificate.json`，状态
`valid=true`。最终整理报告为 `report/final_resolution_2026-07-14.md`。这提升的是仓库内
common-mode implementation assurance；外部独立复核仍未完成。
