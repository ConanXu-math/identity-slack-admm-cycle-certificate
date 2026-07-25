# 研究状态：ADMM Identity Block

## 研究问题

本仓库研究带 identity third block 的直接三块 ADMM：

\[
\min\{\theta_1(x)+\theta_2(y)+\theta_3(z)\mid Ax+By+z=b\}.
\]

当前已经实现的最小工作台主要面向 slack-variable 特例：

\[
\min\{\theta_1(x)+\theta_2(y)+0(z)\mid Ax+By+z=b,\ z\ge0\}.
\]

核心问题是：identity / slack 结构是否提供了足够额外结构来证明直接三块 ADMM 收敛；如果不能，是否能构造低维反例。

## 当前 Source Of Truth

- 主控 workflow：`skills/admm-proof-workflow/SKILL.md`
- 问题形式与 ADMM 迭代：`notes/problem_formulation.md`
- 投影恒等式与符号约定：`notes/z_projection_identity.md`
- 候选 Lyapunov 函数：`notes/candidate_lyapunov.md`
- 统一暂停整理：`notes/pause_summary.md`
- 文献地图：`knowledge_base/literature_map.md`
- 文献队列：`papers/reading_queue.md`
- 来源清单：`papers/source_manifest.md`
- 首轮文献报告：`outputs/literature_report.md`
- 66 周期先例审计：`notes/prior_art_novelty_audit_2026-07-14.md`
- 结构化检索产物：`outputs/prior_art_audit_2026_07_14/`
- MinerU Markdown 文献池：`papers/markdown/<paper_id>/paper.md`（当前 21 篇）
- 全量 SkillCards：`papers/skills/<paper_id>/skill_cards/*.yaml`（当前 21 篇，每篇至少 1 张带行号卡）
- 问题菜单：`docs/problem_menu.md`
- 猜想格：`docs/conjecture_lattice.md`
- 证明义务：`docs/proof_obligations.md`
- 反例压力：`docs/counterexample_pressure.md`
- 仓库整理索引：`docs/repository_map.md`
- fixed-mask impossible lemma 审查：`proof_reviews/fixed_mask_impossible/`
- VI/PPA direct ADMM gate：`proof_reviews/vi_ppa_direct_admm/`
- VI/PPC 修正算法路线：`notes/vi_ppc_corrected_algorithm_route.md`
- VI/PPC 修正算法 proof-review 包：`proof_reviews/vi_ppc_corrected_algorithm/`
- single_full cubic margins 审查：`proof_reviews/single_full_cubic_margins/`
- Qplus theory-first proof rebalance：`proof_reviews/qplus_theory_rebalance/`
- Qplus depth-2 covering review：`proof_reviews/qplus_depth2_covering/`
- Qplus full-chain review：`proof_reviews/zero_single_qplus_full_chain/`
- Qconst-minus review：`proof_reviews/zero_single_qconst_minus/`
- PC-2 zero_single canonical review：`proof_reviews/zero_single_pc2/`
- PC-0 length-2 symmetry reduction review：`proof_reviews/length2_pair_symmetry_reduction/`
- zero_single ordered class review：`proof_reviews/zero_single_ordered_class/`
- PC-1 zero_full canonical review：`proof_reviews/zero_full_pc1/`
- zero_full ordered class review：`proof_reviews/zero_full_ordered_class/`
- single_single Jconst margins review：`proof_reviews/single_single_jconst_margins/`
- single_single Jminus full-domain review：`proof_reviews/single_single_jminus_full_domain/`
- single_single Jminus full-domain certificate：`outputs/wo5_active_set_2026-07-05/single_single_jminus_full_domain_certificate.md`
- single_single Jplus support analysis：`outputs/wo5_active_set_2026-07-05/single_single_jplus_support_analysis.md`
- single_single Jplus bad-box face diagnostics：`outputs/wo5_active_set_2026-07-05/single_single_jplus_badbox_face_diagnostics.md`
- single_single Jplus endpoint candidate gate：`outputs/wo5_active_set_2026-07-05/single_single_jplus_endpoint_candidate_gate.md`
- single_single Jplus bad-vertex certificate：`outputs/wo5_active_set_2026-07-05/single_single_jplus_bad_vertex_certificate.md`
- single_single Jplus codim-2 face certificate：`outputs/wo5_active_set_2026-07-05/single_single_jplus_codim2_face_certificate.md`
- single_single Jplus top-slice lift certificate：`notes/single_single_jplus_top_slice_lift_certificate.md`
- single_single Jplus top-slice lift review：`proof_reviews/single_single_jplus_top_slice_lift/`
- single_single Jmid Bernstein certificate：`notes/single_single_jmid_bernstein_certificate.md`
- single_single Jmid Bernstein review：`proof_reviews/single_single_jmid_bernstein/`
- single_single canonical assembly review：`proof_reviews/single_single_canonical_assembly/`
- single_single ordered class review：`proof_reviews/single_single_ordered_class/`
- SC-1 length-2 nonconstant pairs assembly review：`proof_reviews/sc1_length2_nonconstant_pairs/`
- length-3 switching gate：`notes/length3_switching_gate.md`
- length-3 word-class enumeration：`outputs/wo5_active_set_2026-07-05/length3_switching_classes.md`
- length-3 determinant symbolic check：`outputs/wo5_active_set_2026-07-05/length3_switching_symbolic_check.md`
- length-3 cubic coefficient gate：`outputs/wo5_active_set_2026-07-05/length3_cubic_coefficients.md`
- length-3 Jury margin scaffold：`outputs/wo5_active_set_2026-07-05/length3_jury_margins.md`
- length-3 coordinatewise Bernstein certificate：`outputs/wo5_active_set_2026-07-05/length3_coordinatewise_bernstein_certificate.md`
- length-3 rank-one projector boundary：`outputs/wo5_active_set_2026-07-05/length3_rank_one_projector_boundary.md`
- length-3 scaled rank-one scaffold：`outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_scaffold.md`
- length-3 scaled rank-one `L3C07` certificate：`outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c07_certificate.md`
- length-3 scaled rank-one `S,u` batch certificates：`outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_su_certificates.md`
- length-3 scaled rank-one `L3C11` discriminant certificate：`outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c11_discriminant_certificate.md`
- length-3 scaled rank-one `L3C05` parity certificate：`outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c05_parity_certificate.md`
- length-3 scaled rank-one `L3C06` parity certificate：`outputs/wo5_active_set_2026-07-05/length3_scaled_rank_one_l3c06_parity_certificate.md`
- length-3 scaled rank-one `L3C09/L3C10` breakthrough certificates：`outputs/breakthrough_attempts/stage3_exterior_square/l3c09_l3c10_trace_route.md`、`outputs/breakthrough_attempts/stage3_exterior_square/l3c10_jplus_triangle_certificate.md`
- length-3 scaled rank-one `L3C04` breakthrough certificate：`outputs/breakthrough_attempts/stage3_exterior_square/l3c04_jplus_triangle_certificate.md`
- length-3 full-rank interior scaffold：`outputs/breakthrough_attempts/stage4_full_rank_interior/full_rank_interior_scaffold.md`
- length-3 mixed boundary face scaffold：`outputs/breakthrough_attempts/stage4_full_rank_interior/mixed_boundary_faces.md`
- length-3 `m_full_n_rank_one` quadratic Schur certificate：`outputs/breakthrough_attempts/stage4_full_rank_interior/m_full_n_rank_one_quadratic_schur_certificate.md`
- length-3 `m_rank_one_n_full` cubic Schur certificate：`outputs/breakthrough_attempts/stage4_full_rank_interior/m_rank_one_n_full_cubic_schur_certificate.md`
- length-3 `n_isotropic_m_rotated` cubic Schur certificate：`outputs/breakthrough_attempts/stage4_full_rank_interior/n_isotropic_m_rotated_cubic_schur_certificate.md`
- length-3 full-rank all-margin assembly：`outputs/breakthrough_attempts/stage4_full_rank_interior/full_rank_interior_all_margin_dyadic_depth1_assembly.md`
- length-3 full-rank all-margin proof review：`proof_reviews/stage4_full_rank_interior_margin_assembly/`
- arbitrary switching Stage 5 gate：`outputs/breakthrough_attempts/stage5_arbitrary_switching/arbitrary_switching_gate.md`
- arbitrary switching Stage 5 route note：`notes/breakthrough_routes/stage5_arbitrary_switching_gate.md`
- arbitrary switching AS-2 constant self-loop gate：`notes/breakthrough_routes/stage5_constant_self_loop_gate.md`
- true source-target switching correction：`notes/breakthrough_routes/stage5_true_transition_semantics.md`
- TS-2 affine edge iff proof attempt：`notes/ts2_affine_itinerary_polyhedra.md`
- TS-2 最终独立复核：`proof_reviews/ts2_affine_itinerary_polyhedra/final_verification.json`
- affine source-target transfer theorem：`notes/affine_source_target_transfer.md`
- 面向原优化问题的 quotient-Lyapunov 路线：`notes/optimization_anchored_quotient_lyapunov_route.md`
- 一步 KKT 能量恒等式与交叉项障碍：`notes/one_step_kkt_energy_identity.md`
- 一步 KKT 能量恒等式独立复核：`proof_reviews/one_step_kkt_energy_identity/verification_report.json`
- 静态耦合度量与 itinerary-cone 障碍：`notes/full_image_metric_and_cone_obstruction.md`
- 静态耦合度量与 itinerary-cone 障碍复核：`proof_reviews/full_image_metric_and_cone_obstruction/final_verification.json`
- 一阶历史度量与加强收敛门：`notes/history_metric_and_strengthened_gate.md`
- 联合逐 edge 能量证书：`notes/joint_edge_energy_certificate.md`
- 联合逐 edge 能量证书复核：`proof_reviews/joint_edge_energy_certificate/final_verification.json`
- 固定二维 QP phase-dependent Lyapunov 收敛定理：`notes/fixed_qp_phase_lyapunov_theorem.md`
- 固定二维 QP exact phase/edge 证书：`outputs/breakthrough_attempts/stage10_phase_edge_certificate/phase_edge_rational.json`
- 固定二维 QP 定理独立复核：`proof_reviews/fixed_qp_phase_lyapunov/final_verification.json`
- \(Q_1=aI,\ a\in[1,7/2]\) 参数族收敛定理：`notes/q1_scalar_phase_family_theorem.md`
- \(Q_1\) 参数族 exact Bernstein 证书：`outputs/breakthrough_attempts/stage11_q1_scalar_phase_family/q1_scalar_family.json`
- \(Q_1\) 参数族独立复核：`proof_reviews/q1_scalar_phase_family/final_verification.json`
- \(Q_2(q,r)\) 二维参数盒收敛定理：`notes/q2_box_phase_family_theorem.md`
- \(Q_2\) 二维盒 exact tensor Bernstein 证书：`outputs/breakthrough_attempts/stage12_q2_box_phase_family/q2_box_family.json`
- \(Q_2\) 二维盒独立复核：`proof_reviews/q2_box_phase_family/final_verification.json`
- \((a,q,r)\) 三参数联合盒收敛定理：`notes/joint_qp_box_phase_family_theorem.md`
- 三参数联合盒 exact tensor Bernstein 证书：`outputs/breakthrough_attempts/stage13_joint_qp_box_phase_family/joint_qp_box.json`
- 三参数联合盒独立复核：`proof_reviews/joint_qp_box_phase_family/final_verification.json`
- Reduced \(M,N\) 显式鲁棒邻域定理：`notes/reduced_mn_robust_neighborhood_theorem.md`
- Reduced 邻域基点常数证书：`outputs/breakthrough_attempts/stage14_reduced_mn_neighborhood/reduced_mn_constants.json`
- Reduced 邻域定理独立复核：`proof_reviews/reduced_mn_robust_neighborhood/final_verification.json`
- 任意矩形 (A,B) reduced small-gain 定理：`notes/general_ab_small_gain_phase_gate.md`
- Selector-IQC 全局 mask 条件：`notes/selector_iqc_global_mask_condition.md`
- Selector-IQC 独立复核：`proof_reviews/selector_iqc_global_mask_condition/final_verification.json`
- 对角 reduced 模型 Selector-IQC 无损定理：`notes/selector_iqc_diagonal_lossless.md`
- 对角 Selector-IQC 独立复核：`proof_reviews/selector_iqc_diagonal_lossless/final_verification.json`
- Stage 21 全局 LMI exact 证书：`outputs/breakthrough_attempts/stage21_selector_iqc/selector_iqc_small_gain.json`
- Stage 22 对角无损 exact 证书：`outputs/breakthrough_attempts/stage22_selector_iqc_diagonal/selector_iqc_diagonal_lossless.json`
- 非正规 Selector-IQC 鲁棒邻域定理：`notes/selector_iqc_nonnormal_robust_neighborhood.md`
- Stage 23 非正规 exact 证书：`outputs/breakthrough_attempts/stage23_selector_iqc_nonnormal/selector_iqc_nonnormal.json`
- 非正规 Selector-IQC 独立复核：`proof_reviews/selector_iqc_nonnormal_robust_neighborhood/final_verification.json`
- Phase-dependent Lyapunov 本轮暂停总结：`notes/pause_summary_phase_metric_2026-07-12.md`
- Gate 外固定 QP signed-PWA 收缩定理：`notes/fixed_qp_signed_pwa_contraction_theorem.md`
- Stage 25 signed-PWA exact 证书：`outputs/breakthrough_attempts/stage25_fixed_qp_signed_pwa/fixed_qp_signed_pwa.json`
- Signed-PWA 定理独立复核：`proof_reviews/fixed_qp_signed_pwa/final_verification.json`
- Gate 外 QP affine family 与开放邻域定理：`notes/fixed_qp_signed_pwa_affine_family_theorem.md`
- Stage 26 affine/neighborhood exact 证书：`outputs/breakthrough_attempts/stage26_fixed_qp_affine_family/fixed_qp_affine_family.json`
- Affine family 独立复核：`proof_reviews/fixed_qp_signed_pwa_affine_family/final_verification.json`
- Signed-PWA 两层闭环总入口：`notes/signed_pwa_two_layer_closure_summary.md`
- affine transfer follow-up review：`proof_reviews/affine_source_target_transfer/followup_verification.json`
- fixed rational QP exact itinerary certificate：`outputs/breakthrough_attempts/stage6_exact_admissibility/exact_periodic_itineraries.json`
- exact itinerary follow-up review：`proof_reviews/exact_periodic_itineraries/followup_verification.json`
- source-target structural review：`proof_reviews/stage5_switching_semantics/verification_report.json`
- fixed-mask exponential-exit review loop：`proof_reviews/stage5_fixed_mask_exit/`
- 实验核心代码：`experiments/slack_admm_core.py`
- smoke 输出：`outputs/random_qp_search_smoke.json`、`outputs/spectral_radius_smoke.json`

## 已知事实

- 一般直接多块 ADMM 不保证收敛。
- 常见恢复收敛路线会加入强凸性、矩阵条件、近端项或 prediction-correction 步。
- 在 slack-variable 情形中，\(z\)-update 是显式投影：

\[
z^{k+1}=\Pi_{\mathbb R^m_+}(b-Ax^{k+1}-By^{k+1}+\lambda^k/\beta).
\]

- 使用 complementarity 或 normal cone 前，必须先按 `notes/z_projection_identity.md` 检查本仓库的乘子符号约定。

## 已有实验

当前 NumPy 脚本只提供第一层筛查：

- `experiments/random_qp_search.py`：带 seed 的随机凸 QP 筛查。
- `experiments/spectral_radius_search.py`：局部 active-set 谱半径筛查。
- `experiments/search_slack_active_set_counterexample.py`：固定 active set 仿射映射筛查，支持 structured families、\(\beta\) 网格和 all-mask scan。
- `src/admm_identity/slack_projection.py`：构造 full-state \(s^{k+1}=Ts^k+c\)、effective-state \(v^{k+1}=T_Dv^k+c_D\) 和有限步 stay-in-region 检查。
- `notes/active_set_effective_recurrence.md`：fixed-active effective recurrence 的过程性推导。
- `notes/active_set_reduced_theory.md`：\(T_D\) 的块矩阵理论展开，以及 \(D=I\) 时 near-unit modes 无 \(\lambda\) 分量的解释。
- `notes/active_set_quotient_reduction.md`：全 active \(D=I\) 下的 quotient / reduced-state 谱分析。
- `notes/general_active_mask_reduction.md`：一般 \(D\ne I\) 下的 complementarity reduced map \(R_D\)，并说明 \(R_D\) 保留 \(T_D\) 的非零谱。
- `notes/multi_agent_fixed_mask_debate.md`：multi-agent argue 后形成的 fixed-mask / switching 分支裁决。
- `notes/fixed_mask_invariant_impossible_lemma.md`：fixed-mask invariant expansion impossible 的 proof attempt；已排除 visible complex/negative expansion、signed-q tangent expansion，并用 contraction argument 排除正实扩张 \(\eta>1\)。
- `notes/switching_cone_certificate.md`：active-set switching affine cone certificate 的过程性设计与当前 candidate 长度 `2..10` 非恒定 itinerary screen。
- `notes/short_cycle_switching_nonexpansion_conjecture.md`：二维短周期 switching nonexpansion 的 conjecture、证据边界和后续证明义务。
- `notes/single_full_proof_attempt.md`：`single_full` length-2 product 的 proof-attempt lemmas，汇总 rank-one、isotropic、mask-aligned angle、zero/identity boundary、mixed rank-one face、full two-angle `J+`、full two-angle `Jmid` 和 sanity margins 分析。
- `notes/length2_pair_class_consolidation.md`：`SC-1` 的 pair-class 归并边界；`single_full`、`zero_single`、`zero_full` 和 `single_single` 均已完成对应 review，四类总装已由 `proof_reviews/sc1_length2_nonconstant_pairs/` 接受为二维 length-2 局部 theorem。
- `notes/length3_switching_gate.md`：`SC-1` 之后的 length-3 / arbitrary switching gate；说明 pairwise spectral nonexpansion 不能在无 common seminorm 时直接推出 length-3，并把 length-3 非恒定 words 按 cyclic shift 与坐标交换归为 `11` 类。
- `experiments/enumerate_length3_switching_classes.py`：纯组合枚举脚本，生成 `outputs/wo5_active_set_2026-07-05/length3_switching_classes.md` 与 `outputs/wo5_active_set_2026-07-05/results/length3_switching_classes.json`；该 artifact 不是数值筛查，也不是谱半径证明。
- `experiments/symbolic_length3_switching_products.py`：exact symbolic determinant 检查；单步 determinant 只有 full mask `[1,1]` 可能非零，因此全部非恒定 length-3 products 都满足 `det(product)=0`。该结果只给零特征值，不控制剩余 cubic factor。
- `experiments/symbolic_length3_cubic_coefficients.py`：用 Newton identities 为全部 `11` 个 length-3 canonical classes 提取剩余 cubic factor 的 exact coefficients；完整 expressions 写入 `outputs/wo5_active_set_2026-07-05/results/length3_cubic_coefficients.json`，Markdown 只记录复杂度和 hash。该结果仍不是 Schur/Jury certificate。
- `experiments/symbolic_length3_jury_margins.py`：基于 `L3-1b` 系数构造全部 canonical classes 的 `J+`、`J-`、`Jmid` 和 `Jconst` margin objects；只保存长度、operation count 和 hash。该 scaffold 仍不证明 margins 非负。
- `experiments/certify_length3_coordinatewise_bernstein.py`：闭合 `L3-2b-coordinatewise` 子定理；对标量 active/inactive blocks 的全部 8 个 length-3 words，Schur margins 的 degree `(3,3)` Bernstein coefficients 全部非负。因此 simultaneous diagonalization / coordinatewise 情形下 length-3 product 满足 `rho <= 1`。
- `experiments/analyze_length3_rank_one_projector_boundary.py`：对非交换二维 `L3-2c` 的 rank-one projector boundary 生成 exact characteristic polynomial artifact。全部 `11` 类去掉零根和允许的单位根后，剩余次数为 `6` 个一次、`4` 个二次、`1` 个三次；全部 6 个一次 residual classes 已由 \(S=x^2+y^2,u=xy\) 改写、显式正项和 exact Sturm 无实根检查闭合；4 个二次 residual classes 已由 \(S,u\) half-domain split、AM-GM / square controls 与 half-line Sturm 检查闭合；唯一三次 residual `L3C08` 的五个 cubic Schur/Jury margins 已由偶次 \(U,V\) 降维、`U=rV` 系数证书和 `Jminus` 两段分组证书闭合。projective infinity 由齐次 rank-one projector 参数和谱半径连续性闭合。当前 rank-one projective boundary 已闭合 `11/11` 类。该结果只是 rank-one projector boundary 子定理，不覆盖 scaled rank-one 或 full-rank interior。
- `experiments/analyze_length3_scaled_rank_one_scaffold.py`：对 \(M=mP_x,N=nP_y,0\le m,n\le1\) 的 scaled rank-one 子族生成 exact symbolic proof-obligation scaffold。释放 `m,n` 后，`10` 个 canonical classes 为二次 residual，`L3C08` 为三次 residual；若干 projector 情形的一次 residual 升为二次 residual，因此 scaled rank-one 不能由 `m=n=1` 的 projector boundary 直接外推。该 artifact 只是 `proof_obligation_scaffold`，不是 theorem 或 counterexample。
- `experiments/certify_length3_scaled_rank_one_l3c07.py`：闭合 scaled rank-one 子族中的第一个 canonical class `L3C07=[0,0]->[1,1]->[1,1]`。去掉两个零根后 residual 为二次；三个 Schur/Jury margins 经 \(S=x^2+y^2,u=xy\) 半域分解，再对 \(m,n\in[0,1]\) 做 degree `(3,3)` Bernstein 展开。全部 Bernstein 系数在 \(a,t\ge0\) 上非负，其中唯一特殊系数由平方配方 \((9a^2-2a+4t+9)/9=(9(a-1/9)^2+4t+80/9)/9\) 闭合。该结果是 `theorem_for_l3c07_scaled_rank_one_class`，不是完整 scaled-rank-one theorem。
- `experiments/certify_length3_scaled_rank_one_su_classes.py`：把 `L3C07` 的 \(S=x^2+y^2,u=xy\) 半域 + `(m,n)` degree `(3,3)` Bernstein 模板批量用于 scaled rank-one 二次 residual classes。当前闭合 `L3C02` 与 `L3C07` 两个 \(S,u\)-symmetric classes；`L3C02` 的三个特殊 Bernstein 系数由正因子/平方配方闭合。其余 `8` 个二次类标为 `su_symmetry_unavailable`，这只是路线诊断，不是反例。
- `experiments/certify_length3_scaled_rank_one_l3c11_discriminant.py`：闭合 scaled rank-one 子族中的非对称 canonical class `L3C11=[[0,1],[1,1],[1,1]]`。去掉两个零根后 residual 为二次；三个 Schur/Jury margins 都是关于 \(x\) 的二次式 \(Ax^2+Bx+C\)。令 \(v=y^2\ge0\)，脚本在 \(m,n\in[0,1]\) 上用 Bernstein 系数证明 \(A\ge0\)、\(C\ge0\)、\(4AC-B^2\ge0\)，并用配方与 \(A=0\) 退化情形闭合 margins。该结果是 `theorem_for_l3c11_scaled_rank_one_class`，不是完整 scaled-rank-one theorem。
- `experiments/certify_length3_scaled_rank_one_l3c05_parity.py`：闭合 scaled rank-one 子族中的 canonical class `L3C05=[[0,0],[0,1],[1,1]]`。三个 Schur/Jury margins 都写成 \(E(X,Y,m,n)+xy\,O(X,Y,m,n)\)，其中 \(X=x^2,Y=y^2\)。脚本用 \(X=a/(1-a),Y=b/(1-b)\) compactification，在 \((m,n,a,b)\in[0,1]^4\) 上证明 \(E\ge0\) 与 \(E^2-XYO^2\ge0\)。`Jminus` 与 `Jconst` 直接由 Bernstein 系数闭合；`Jplus` 的 guard 通过 `m=n=1` endpoint factor \((a-b)^2(4a^2b+4ab^2+1)\ge0\) 闭合。该结果是 `theorem_for_l3c05_scaled_rank_one_class`，不是完整 scaled-rank-one theorem。
- `experiments/certify_length3_scaled_rank_one_l3c06_parity.py`：复用 `L3C05` parity 模板闭合 `L3C06=[[0,0],[1,1],[0,1]]`。三个 quadratic Schur/Jury margins 均由 \(E\ge0\)、\(E^2-XYO^2\ge0\) 的 compactified Bernstein / endpoint factor 证书闭合。该结果是 `theorem_for_l3c06_scaled_rank_one_class`，不是完整 scaled-rank-one theorem。
- `experiments/breakthrough/certify_l3c09_l3c10_trace_route.py` 与 `experiments/breakthrough/certify_l3c10_jplus_triangle_bernstein.py`：在 exterior-square rank-defect reduction 后，闭合 scaled-rank-one priority classes `L3C09` 与 `L3C10`。`L3C09` 三个 quadratic margins 直接由 parity/Bernstein gate 闭合；`L3C10` 的 trace/Jmid (`Jconst`) 与 `Jminus` 直接闭合，剩余 `Jplus` guard 通过 depth-1 dyadic subdivision 加 `a=b` 对角三角化闭合。该结果给出 `theorem_for_l3c09_scaled_rank_one_class` 与 `theorem_for_l3c10_scaled_rank_one_class`，仍不是完整 scaled-rank-one theorem。
- `experiments/breakthrough/certify_l3c04_jplus_triangle_bernstein.py`：闭合 scaled-rank-one class `L3C04=[[0,0],[0,1],[1,0]]`。`Jminus` 与 `Jconst` 由动态 degree 的一盒 exact Bernstein 直接闭合；`Jplus` 的 \(E\) 经 depth-1 dyadic 闭合，guard 在 depth-1 后只剩 `[1,1,0,0]` 与 `[1,1,1,1]` 两个坏盒，再沿 `a=b` 对角线三角化，四个 charts 全部 exact Bernstein 非负。该结果是 `theorem_for_l3c04_scaled_rank_one_class`，仍不是完整 scaled-rank-one theorem。
- `experiments/breakthrough/certify_l3c03_triangle_bernstein.py`：闭合 scaled-rank-one class `L3C03=[[0,0],[0,1],[0,1]]`。`Jconst` 一盒 exact Bernstein 闭合；`Jminus` 的 \(E\) 与 guard 经 depth-1 dyadic subdivision 闭合；`Jplus` 的 \(E\) depth-1 闭合，guard 只剩 `[1,1,0,0]` 与 `[1,1,1,1]` 两个坏盒，再沿 `a=b` 三角化闭合四个 charts。该结果是 `theorem_for_l3c03_scaled_rank_one_class`，仍不是完整 scaled-rank-one theorem。
- `experiments/breakthrough/certify_l3c01_triangle_bernstein.py`：闭合 scaled-rank-one class `L3C01=[[0,0],[0,0],[0,1]]`。`Jminus` 经 depth-1 dyadic subdivision 闭合；`Jconst` 留下一个 same-half guard 坏盒，`Jplus` 留下五个 same-half guard 坏盒，逐盒沿 `a=b` 三角化后 `12/12` 个 charts 全部 exact Bernstein 非负。该结果是 `theorem_for_l3c01_scaled_rank_one_class`；至此 10 个二次 residual scaled-rank-one classes 全部闭合，仍剩 cubic/rank-3 `L3C08`。
- `experiments/breakthrough/certify_l3c08_cubic_bernstein.py`：闭合 scaled-rank-one class `L3C08=[[0,1],[0,1],[1,0]]`。两个 `Jconst` margins 与 `Jmid` 由一盒 exact Bernstein 闭合，其中 `Jmid` guard degree 为 `(12,12,12,12)` 且负系数为 `0`；`Jminus` 经 depth-1 dyadic subdivision 闭合；`Jplus` 剩余两个 same-half top guard 坏盒，经 `a=b` 三角化后四个 charts 全部 exact Bernstein 非负。该结果是 `theorem_for_l3c08_scaled_rank_one_class`。结合此前十个二次 residual classes，`outputs/breakthrough_attempts/stage3_exterior_square/scaled_rank_one_assembly.md` 汇总为 length-3 scaled-rank-one `11/11` canonical classes closed；仍不覆盖 full-rank interior、arbitrary switching 或原始 direct ADMM 全局收敛。
- `experiments/breakthrough/analyze_length3_full_rank_interior_scaffold.py`：启动 Stage 4 full-rank interior scaffold。采用 \(N=\operatorname{diag}(\nu_1,\nu_2)\)、\(M=R(c,s)\operatorname{diag}(\mu_1,\mu_2)R(c,s)^T\)、\(c^2+s^2=1\)，对 `11` 个 length-3 canonical classes 生成未展开 trace / Schur-Jury margin metadata 和 face hierarchy。当前 closed faces 为 `coordinatewise_relative_angle_zero`、`m_isotropic_coordinatewise`、`rank_one_projector_corner`、`scaled_rank_one_corner`；open faces 为 `m_rank_one_n_full`、`m_full_n_rank_one`、`n_isotropic_m_rotated`。该 artifact 是 `proof_obligation_scaffold`，不是 full-rank interior theorem 或 counterexample。
- `experiments/breakthrough/analyze_stage4_mixed_boundary_faces.py`：推进 Stage 4A mixed boundary faces。`m_full_n_rank_one` 的 `11/11` 个 canonical words 均有 product rank upper bound `<=2`，因此 \(\wedge^2(P)\) rank upper bound `<=1`，`Jmid` 可走 exterior-square trace route；`m_rank_one_n_full` 中 `7/11` 个 canonical words 有同样 rank shortcut，剩余 `L3C08/L3C09/L3C10/L3C11` 是 hard classes。该 artifact 仍是 `proof_obligation_scaffold`，不证明 mixed-face Schur/Jury margins 非负。
- `experiments/breakthrough/certify_stage4_m_full_n_rank_one_quadratic_schur.py`：闭合 Stage 4 参数化下的 `m_full_n_rank_one` face。这里 \(N=\operatorname{diag}(\nu_1,0)\)、\(M=R(c,s)\operatorname{diag}(\mu_1,\mu_2)R(c,s)^T\)，\(0\le\mu_1,\mu_2,\nu_1\le1\)、\(c^2+s^2=1\)。product rank `<=2` 将非零 characteristic factor 降为二次，三个 quadratic Schur margins `1-e1+e2`、`1+e1+e2`、`1-e2` 均由 exact Bernstein 证书闭合；`L3C08/L3C10` 的 `quadratic_Jplus` 使用 depth-1 dyadic Bernstein，其余 margins one-box 闭合。该结果是 `theorem_for_stage4_m_full_n_rank_one_parameterized_face`，不覆盖 `m_rank_one_n_full`、`n_isotropic_m_rotated` 或 full-rank interior。
- `experiments/breakthrough/certify_stage4_m_rank_one_n_full_cubic_schur.py`：闭合 Stage 4 参数化下的 `m_rank_one_n_full` face。这里 \(M=R(c,s)\operatorname{diag}(\mu_1,0)R(c,s)^T\)、\(N=\operatorname{diag}(\nu_1,\nu_2)\)，\(0\le\mu_1,\nu_1,\nu_2\le1\)、\(c^2+s^2=1\)。`L3C08/L3C09/L3C10/L3C11` 没有 product-rank `<=2` shortcut，因此脚本用 principal minors 直接计算 \(e_1,e_2,e_3\)，再检查完整 cubic Schur/Jury margins；`11/11` 个 canonical classes 全部由 exact Bernstein 证书闭合，`L3C01/L3C03/L3C08/L3C10` 使用 depth-1 dyadic Bernstein。该结果是 `theorem_for_stage4_m_rank_one_n_full_parameterized_face`，不覆盖 `n_isotropic_m_rotated`、full-rank interior 或 arbitrary switching。
- `experiments/breakthrough/certify_stage4_n_isotropic_m_rotated_cubic_schur.py`：闭合 Stage 4 参数化下的 `n_isotropic_m_rotated` face。这里 \(N=\nu I\)、\(M=R(c,s)\operatorname{diag}(\mu_1,\mu_2)R(c,s)^T\)，\(0\le\mu_1,\mu_2,\nu\le1\)、\(c^2+s^2=1\)。虽然 \(N\) isotropic，但 active-mask signs 仍与 rotated \(M\) 交互，因此脚本保留完整 cubic factor 并用 principal minors 计算 \(e_1,e_2,e_3\)；`11/11` 个 canonical classes 全部由 exact Bernstein 证书闭合，只有 `L3C08/Jplus` 使用 depth-1 dyadic Bernstein。该结果是 `theorem_for_stage4_n_isotropic_m_rotated_parameterized_face`，不覆盖 full-rank interior 或 arbitrary switching。
- `notes/length2_pair_symmetry_reduction.md`：`PC-0` 对称性/反序谱归约，已由 `proof_reviews/length2_pair_symmetry_reduction/` 接受，将 `12` 个 ordered pairs 压到四个 canonical representatives。
- `notes/zero_full_pc1_reduction.md`：`PC-1` 的 `zero_full` canonical representative 降阶推导和 quadratic margins exact Bernstein certificate；已由 `proof_reviews/zero_full_pc1/` 接受，结合 `PC-0` 后 `zero_full` ordered class 已由 `proof_reviews/zero_full_ordered_class/` 接受。
- `notes/single_single_pc3_route.md`：`PC-3` 的 `single_single` canonical representative 路线；`Jconst_minus/Jconst_plus`、`Jminus`、`Jplus` 和 `Jmid` 均已闭合，canonical representative assembly 与 ordered class 已分别由 `proof_reviews/single_single_canonical_assembly/`、`proof_reviews/single_single_ordered_class/` 接受。
- `notes/vi_ppc_corrected_algorithm_route.md`：VI/PPA/PPC 的修正算法路线 proof plan；明确标准 He-Yuan direct-route 条件对原始 slack ADMM 失败，但 prediction-correction / proximal repair 仍是可证收敛算法的独立分支。当前已有四个 corrected-theorem accepted-by-review 节点：\(Y=\mathbb R^n\) 的 z-fixed corrected essential-variable theorem；一般 closed convex \(Y\)、\(X=\mathbb R^p\) 的 block-order \((z,x,y)\) ADM-G theorem；一般 closed convex \(Y\)、显式 invariant-\(X\) 条件 \(X-\alpha C_{xy}(Y-Y)\subseteq X\) 的 ADM-G theorem；以及 image-regular 假设下的 full-image-state H-projected corrected theorem。另有 `image_space_h_projected_fejer_gate.md` 已接受为抽象代数 Fejer gate。`closed_image_and_lift_gate.md` 经 reviewer `Dirac` 审查为 `incomplete`：arbitrary closed convex \(X,Y\) 过强。`image_regular_corrected_theorem_candidate.md` 经 reviewer `Bacon` 审查为 `incomplete_predictor_inequality_open`；`image_predictor_inequality_lemma.md` 显示当前 \(v=(c,z,\lambda)\) route 消去 \(a\)-block 后留下未控交叉项。最新 `full_image_state_convergence_theorem_candidate.md` 经 reviewer `Halley` 审查为 `correct_local`，精确覆盖 image-regular modified algorithm，不覆盖原始 direct ADMM 或 arbitrary closed convex \(X,Y\)。
- `notes/zero_single_pc2_reduction.md`：`PC-2` 的 `zero_single` canonical representative 降阶推导；已降为 quadratic，四个 margins 已由 `proof_reviews/zero_single_pc2/` 接受；结合 `PC-0` 后，`zero_single` ordered class 已由 `proof_reviews/zero_single_ordered_class/` 接受。
- `notes/zero_single_relative_angle_route.md`：`PC-2` 的相对角后续路线；记录 `Qplus D` 在 rank-one projector 边界上的 \((u-v)^2\) / \((uv-1)^2\) 因子，以及 `Qconst_minus D` 角落负单项式的 AM-GM 控制方式。
- `notes/zero_single_qconst_corner_certificate_plan.md`：记录 `Qconst_minus` 四个角点邻域的 blow-up / weighted Bernstein 证书设计，并明确批量 6D subdivision 不是下一步。
- `notes/zero_single_qconst_corner_certificate_attempt.md`：记录第一个角点 chart 的中间尝试；local chart 后只剩一个 bad Bernstein coefficient，但简单 power-basis control 会引入新负系数。该中间态已被 `certify_zero_single_qconst_minus_weighted_bernstein.py` 的 endpoint-weighted certificate supersede。
- `notes/zero_single_pc2_multi_agent_route_decision.md`：记录 multi-agent route decision，优先实现 `Qconst_minus` corner certificate，再回到 `Qplus` relative-angle / determinant-plus-square certificate。
- `experiments/search_reduced_map_abstract_expansion.py`：直接筛查 \(R_D\) 的抽象 PSD contraction 结构，避免重复普通随机 QP screen。
- `experiments/build_reduced_map_qp_candidate.py`：将抽象 \(R_D\) expansion probe 嵌入实际凸二次 slack QP，并输出 candidate pressure report。
- `experiments/analyze_candidate_invariant.py`：检查 QP candidate 的 active-region invariant 条件和长时 stay behavior。
- `experiments/search_fixed_mask_invariant_candidate.py`：搜索正实扩张射线或 signed-q 切向复扩张这两类可支持 fixed-mask 严格反例的结构。
- `experiments/search_active_set_switching_cycle.py`：搜索周期 active-mask itinerary 的渐近扩张射线。
- `experiments/search_switching_cone_certificate.py`：搜索周期 active-mask itinerary 的 affine cone certificate，包含周期 basepoint 和每段 signed-q margin。
- `experiments/optimize_switching_cone_certificate.py`：在抽象 PSD contraction 空间中直接优化短周期 switching cone certificate。
- `experiments/analyze_length2_switching_products.py`：系统检查二维 length-2 nonconstant mask-pair products 的谱半径、正实谱半径和 Schur/Jury margins。
- `experiments/symbolic_length2_switching_products.py`：用 exact symbolic algebra 固化全部 length-2 nonconstant pair product 的 determinant-zero check。
- `experiments/stress_length2_boundary_families.py`：测试 rank-one / near-projector 边界族，挑战 `SC-1` 的 Schur/Jury 路线。
- `experiments/analyze_single_full_boundary_symbolics.py`：对 `single_full` representative 的 rank-one projector boundary 给出 exact characteristic polynomial 与 `Jmid` SOS。
- `experiments/optimize_single_full_jury_margins.py`：直接最小化 `single_full` representative 的 `J+` 与 `Jmid`，检查 full-rank interior 是否有负 margin。
- `experiments/analyze_single_full_isotropic_symbolics.py`：对 `single_full` representative 的 isotropic 子族 \(M=mI,N=nI\) 给出 exact charpoly 与 Jury margin 因式分解。
- `experiments/analyze_single_full_mask_aligned_angle_symbolics.py`：对 `single_full` representative 的 mask-aligned angle 子族给出 `J+` 与 `Jmid` 因式分解，覆盖一类 \(M,N\) 不交换的切片。
- `experiments/analyze_single_full_zero_identity_boundaries.py`：对 `single_full` representative 的 zero / identity boundary faces 给出 exact symbolic certificate。
- `experiments/analyze_single_full_mixed_rank_one_reduction.py`：对 `single_full` representative 的 mixed rank-one face 给出 `J+` 闭式非负证明和 `Jmid` 多项式非负 proof obligation reduction。
- `experiments/certify_single_full_mixed_rank_one_bernstein.py`：用 exact Bernstein coefficients 证明 mixed rank-one face 中 \(J_{\rm mid}\) 的剩余多项式非负义务。
- `experiments/analyze_single_full_two_angle_reduction.py`：对 `single_full` representative 的 full two-angle/global-orientation 参数化给出 `J+` exact Bernstein certificate，并把 `Jmid` 约简成后续多项式非负义务。
- `experiments/certify_single_full_two_angle_jmid_bernstein.py`：用 sparse Bernstein coefficient conversion 证明 full two-angle/global-orientation 参数化中 \(J_{\rm mid}\) 的剩余判别式非负义务。
- `experiments/certify_single_full_two_angle_sanity_margins.py`：用 exact Bernstein coefficients 证明 full two-angle/global-orientation 参数化中 `J-`、`1-a3` 和 `1+a3` 非负，从而覆盖 `Jconst=1-|a3|`。
- `experiments/analyze_zero_single_relative_angle_symbolics.py`：将 `zero_single` relative-angle 路线固化为 exact symbolic artifact，验证 `Qplus D` 的 rank-one projector 边界因子和 `Qconst_minus D` 的 AM-GM corner controls。
- `experiments/analyze_zero_single_qconst_boundary_neighborhood.py`：对 `Qconst_minus` 的 dyadic angle boxes 做 exact Bernstein localization，深度 `3` 闭合 `60/64` boxes，剩余 `4` 个正是角点邻域。
- `experiments/analyze_zero_single_qconst_corner_eigen_localization.py`：在 `Qconst_minus` 四个角度角点坏盒内继续二分 eigenvalue variables；每个角点 `16` 个 eigenvalue 子盒中 `15` 个闭合，唯一坏盒正是匹配的 rank-one projector 子盒。
- `experiments/certify_zero_single_qconst_minus_weighted_bernstein.py`：用 AM-GM control polynomial 乘 endpoint Bernstein weight 闭合 `Qconst_minus` 的四个 rank-one projector 子盒；每个 case 都有 `F_bad=H_bad=-1/1024`、`scale=1`、remainder negative count `0`。
- `experiments/analyze_zero_single_qplus_psd_route.py`：将 `Qplus` 改写为 `det(sym(I-L)) + skew^2` 的二维代数证明路线；该路线仍需证明 `sym(I-L) >= 0` 或直接证明右端非负。
- `experiments/analyze_zero_single_qplus_psd_minors.py`：检查 `Qplus` PSD route 的 `S11`、`S22` 主子式；`A` components 经 angle bisection 闭合，但 `D` components 仍剩四个角点坏盒，说明直接主子式路线还未闭合。
- `experiments/search_zero_single_qplus_exact_obstruction.py`：对 `Qplus` PSD sufficient route 做 exact rational-grid obstruction gate，区分 `certificate_failure_only`、`sufficient_route_failure` 和 `margin_failure`；默认网格 `30625` 个有理点未发现 `S11/S22/detS/Qplus` 负 witness，classification 为 `certificate_failure_only`。
- `experiments/analyze_zero_single_qplus_relative_angle_localization.py`：对 `Qplus D` 做 dyadic Bernstein localization；深度 `1..3` 的坏盒精确匹配 `s=t` 与 `s+t=1` 两条 relative-angle strips，说明缺口不是孤立角点，而是相对角零面邻域。
- `experiments/certify_zero_single_qplus_strip_boundaries.py`：将 `Qplus` 的 `A` 与 `D` 限制到两条 relative-angle strips 本身；单盒 Bernstein 仍有负系数，但对 strip parameter `s` 二分一次即可闭合两条 strips。
- `experiments/analyze_zero_single_qplus_strip_neighborhood_charts.py`：把两条 strips 的邻域分成四个三角 chart；`A` 分量在四个 chart 上经 `(a,r)` 二分闭合，`D` 分量在 depth `2` 时每个 chart 仍剩 `5` 个坏盒，下一步需要 endpoint-weighted control 或局部 determinant-plus-square 证书。
- `experiments/analyze_zero_single_qplus_badbox_endpoint_support.py`：分析 `Qplus D` chart bad boxes 中负 Bernstein coefficients 的 endpoint support；depth `2` 下每个 chart 的 `707` 个负系数中有 `704` 个落在两个 rank-one projector endpoint slabs 上，剩余 `3` 个是相邻 endpoint index。
- `experiments/search_zero_single_qplus_endpoint_controls.py`：对 `Qplus D` 每个 chart 的一个代表 bad box 做 exact finite control search；候选族为 top negative endpoint signatures 推出的 endpoint weights 乘 `X^2+Y^2-X*Y` 型 AM-GM controls，当前四个代表 boxes 均无 feasible scale。这只排除简单单控制族，不排除多控制组合或局部 determinant-plus-square 证书。
- `experiments/search_zero_single_qplus_multicontrol_feasibility.py`：把 `Qplus D` 代表 bad boxes 写成 multi-control `F=sum_j gamma_j H_j+R` 的线性可行性检查；候选 `H_j` 包含 chart-specific rank-one slab weights、slab 外自由变量的 degree-1 residual weights 和 top negative endpoint signature weights 乘 `X^2+Y^2-X*Y`，LP 只产生候选，只有有理化 scale 后 exact Bernstein remainder 非负才算局部证书。当前代表搜索未找到 LP feasible box。
- `experiments/analyze_zero_single_qplus_det_square_badboxes.py`：在 `Qplus D` 代表 bad boxes 内做 exact rational-grid determinant-square diagnostic，检查 `Qplus=det(sym(I-L))+skew_sq`；当前四个代表 bad boxes 的 `567` 个 exact rational samples 中 `detS` 和 `Qplus` 都没有负值。这不是 nonnegativity certificate，但提示下一步优先尝试局部 exact `det(S)` certificate，而不是继续盲目扩大 AM-GM controls。
- `experiments/analyze_zero_single_qplus_local_det_square.py`：把 `det(S)` 的 parity gate 投到四个代表 `Qplus D` bad boxes 上；`detS_A` 在四个盒子全部 exact Bernstein 闭合，但 `detS_D=A0^2-u*v*B0^2` 在四个盒子均未闭合，负 Bernstein 系数分别为 `1740/1740/2797/1740`。这只说明 naive local `det(S)` parity certificate 不足，不是负值 witness。
- `experiments/analyze_zero_single_qplus_detS_support.py`：分析同一批四个代表盒中 `detS_D` 负 Bernstein support；`8017` 个负系数中 `8006` 个精确落在 rank-one endpoint slabs 上，`8007` 个落在 near-slab 上，说明下一步应按 endpoint-slab factor/residual controls 继续，而不是回到普通 numerical screen。
- `notes/zero_single_qplus_endpoint_slab_theory.md`：把 `Qplus` 的剩余义务改写为理论优先的引理链：二维 determinant-plus-square 恒等式、relative-angle 零面、strip-neighborhood normal-coordinate 展开、endpoint-slab control、`anti_lower` zero-endpoint quarantine，以及机器代数只作恒等式/分解/remainder 校验的边界。
- `notes/zero_single_qplus_square_reserve_local_lemma.md`：进一步收窄 `Qplus` 理论路线；不把 \(S\succeq0\) 或 `det(S)>=0` 作为主目标，而是保留 \(K^2\) reserve，尝试在四个代表 strip-neighborhood bad boxes 上构造显式局部分解 \(F_B=K_B^2+\sum_j\gamma_jW_jC_j+R_B\)，并用 exact Bernstein remainder 作为 proof-grade gate。
- `notes/theory_first_proof_pivot.md`：把后续工作显式改成理论优先；全局 Lyapunov 线已得到 projection gap lemma \(\langle \Delta z^{k+1},r^{k+1}\rangle\le0\)，同时确认 projection-only 仍不能控制 \(\langle B\Delta y,\Delta z\rangle\)；base-algorithm 分支应优先推进 `zero_single` 的 `Qplus` square-reserve 局部分解。
- `experiments/search_zero_single_qplus_square_reserve_local_certificate.py`：直接以 `Qplus D` 局部分子为目标的 sparse-support multi-control certificate scaffold；显式记录 `skew_square_reserve_absorbed_in_target=True`，不再把 `detS_D` 作为主目标。first-pass artifact 只跑 `diag_lower` depth-1 一个代表盒，极小控制族无 LP feasible，不能解释为反例。
- `experiments/certify_zero_single_qplus_square_reserve_local.py`：继续推进 `Qplus` square-reserve local lemma 的直接版本，在 `diag_lower` depth-2 代表盒 `(2,1)` 上加入 endpoint、strip-normal 与 residual controls；基础版 `112` 个 controls、加强版 `634` 个 controls 均 LP infeasible。该结果只排除这两个有限直接控制族，提示下一步应实现显式 \(K_B^2\) / sign-aware square split，而不是继续堆同类 controls。
- `experiments/analyze_zero_single_qplus_explicit_square_split.py`：固化 `Qplus=det(sym(I-L))+K^2` 的共同分母与 sign-aware square split。exact checks 包括 `4*C*Qplus_num = detS_num + K_num^2`、A/B parity identities、`K_num=xP(u,v)+yR(u,v)`，并导出 `diag_lower` 代表盒 `(2,1)` 的 split component summaries。该 artifact 只证明代数骨架，不证明 `Qplus>=0`。
- `experiments/certify_zero_single_qplus_partial_square_remainder.py`：把 explicit split 接入局部 sign-aware remainder gate，测试 \(Qplus_{\rm common}=\alpha K_{\rm num}^2+R_\alpha\)。当前在 `diag_lower` depth-2 代表盒 `(2,1)` 上取 `alpha=1/2`，`A_alpha` exact Bernstein 负系数为 `0`，但 `D_alpha=A_alpha^2-uvB_alpha^2` 仍有 `1738` 个负 Bernstein 系数；这只排除该 partial-square split，不是 `Qplus` 反例。
- `experiments/certify_zero_single_qplus_sign_aware_square_gate.py`：把 explicit split 改成 sign-eliminated gate：先检查 \(F_A\ge0\)，再检查 \(D_F=F_A^2-uvF_B^2\)，并固定 square source \(D_K=(uP^2-vR^2)^2\) 系数为 `1`。在 `diag_lower` depth-2 代表盒 `(2,1)` 上，`F_A` exact Bernstein 负系数为 `0`，但 `D_F-D_K` 仍有 `1738` 个负 Bernstein 系数；极小 endpoint/strip-normal 控制族 `4` controls 的 active LP infeasible。该结果只排除当前固定源 + 小控制族，不是 `Qplus` 反例。
- `proof_reviews/qplus_theory_rebalance/`：把用户指出的“实验偏多”问题转成 proof-blueprint 约束。该目录明确：全局 projection-only Lyapunov 线仍卡在 \(\langle B\Delta y,\Delta z\rangle\)，base-algorithm 分支下一步必须优先证明 `diag_lower` 代表盒的 fixed-source remainder \(G=D_F-D_K\) endpoint / strip-normal 分解；脚本只能用于恒等式、候选分解和 remainder 非负校验。`endpoint_slab_attempt.md` 记录了 predecessor \(D_\alpha\) 的端面限制尝试，`current_gate_alignment.md` 明确当前主对象已升级为 \(G=D_F-D_K\)。`experiments/analyze_zero_single_qplus_fixed_remainder_faces.py` 已确认 \(G\) 的两个 endpoint restricted faces 各有 `869` 个负 Bernstein coefficients，strip \(r=1\) faces 各有 `134` 个；两条 joint lower strip edges 含 \((3a-2)^2\)，其 quotient Bernstein 负系数为 `0`，但 simple strip-lift quotient 在 \(a=3/4,r=3/4\) 有 exact 负值 witness。
- `notes/zero_single_qplus_joint_edge_factor_lemma.md`：对当前 \(G=D_F-D_K\) 的两条二维 joint lower edges 给出 closed local sublemma。两条 edge 都满足 \(G_{\rm edge}=-(ar+5a+2r-6)^2P(a,r)/2^{28}\)，且 \(-P\) 的 exact Bernstein 负系数均为 `0`，所以 joint lower edge 已闭合。该结果不是全局 `Qplus` 证明；下一步是把这个平方因子向 single-zero edge / endpoint face lift。
- `notes/zero_single_qplus_single_zero_factor_lemma.md`：把同一平方结构提升到四条 single-zero edges。四条 edge 都满足 \(G_{\rm single}=-(ar+5a+2r-6)^2(1-\tau)^2P(a,r,\tau)/2^{28}\)，且 \(-P\) 的 exact Bernstein 负系数均为 `0`。该结果闭合三维 single-zero edge，但完整 endpoint face 仍开放。
- `notes/zero_single_qplus_endpoint_face_factor_lemma.md`：进一步闭合两个 endpoint faces。两个 face 都满足 \(G_{\rm face}=-(ar+5a+2r-6)^2P(a,r,\eta,\tau)/2^{28}\)，且 \(-P\) 的 exact Bernstein 负系数均为 `0`。完整 6D local box 不由该平方因子直接整除，所以下一步是 face-to-interior lift。
- `outputs/wo5_active_set_2026-07-05/zero_single_qplus_face_to_interior_hermite_gate.md`：检查从 endpoint face 到 interior 的简单 Hermite lift。`m2=1,n1=1` face 的两个一阶 normal quotients 在 exact grid 上有负 witness，因此 \(A,B,H\ge0\) 的直接 Hermite lift 路线受阻。该 witness 是 quotient obstruction，不是 \(G<0\) 或 `Qplus` 反例。
- `notes/zero_single_qplus_top_slice_lift_certificate.md`：用 endpoint-face top-slice lift 闭合 `diag_lower` depth-2 代表盒 `(2,1)`。具体分解为 \(G=m_1^2n_2^2C_{12}+m_2^2n_1^2C_{21}+R_2\)，其中 \(C_{12},C_{21}\) 是已闭合 endpoint faces，\(R_2\) 的 exact Bernstein 负系数为 `0`。该结果只闭合一个代表盒，不是完整 `Qplus` 证明。
- `notes/zero_single_qplus_top_slice_representative_extension.md`：将 top-slice certificate 扩展到代表 charts。`diag_lower`、`diag_upper`、`anti_upper` 的代表盒均由 \(p=2,\gamma=1\) 闭合；`anti_lower (0,0)` 仍开放，\(p=4,\gamma=1\) 最好但仍有 `21` 个负 Bernstein 系数，负 support 位于 zero-endpoint quarantine 区域。
- `experiments/search_zero_single_qplus_detS_endpoint_controls.py`：对 `detS_D` endpoint slabs 做 bounded single-control search；degree-8 baseline 与 `{7,8}` near-slab chart-geometry controls 在四个代表盒上均为 `0/4` feasible。这只排除有限 single-control 族，不是 `Qplus` 反例。
- `experiments/optimize_signed_q_tangent.py`：专门优化 signed-q tangent 条件，寻找 active inequalities 不可见的扩张模态。
- `experiments/optimize_positive_outward_ray.py`：专门优化 fixed-mask positive outward ray 条件，寻找正实 cone-compatible eigenmode。
- `experiments/search_positive_outward_ray_feasibility.py`：固定 \(\eta>1\)、枚举 support，并消去 \(y\) 后直接最小化 cone eigenpair 残差。
- `experiments/analyze_near_unit_modes.py`：分析 near-unit modes 的 \(y,z,\lambda\) 分量。
- `notes/near_unit_mode_analysis.md`：near-unit modes 的中文解释。
- `experiments/reproduce_counterexample.py`：后续手工录入文献反例的占位入口。

这些脚本只产生数值证据。`suspect_unstable` 不是 proof-grade counterexample。

## 开放证明义务

1. 推导 \([A,B,I]\) 直接三块 ADMM 的完整 KKT + lag-error 恒等式。
2. WO-3 第一轮已确认：投影 firm nonexpansiveness 是有效入口，但不能单独控制
   \(\langle B(y^{k+1}-y^k),z^{k+1}-z^k\rangle\)。
3. 候选 Lyapunov 路线当前状态为 `incomplete`，详见 `proof_reviews/identity_block_lyapunov/verification_report.json`。
4. VI/PPA framework 已按 VeryMath / AI4Math `proof-blueprint-review` 单独开 gate：
   `proof_reviews/vi_ppa_direct_admm/verification_report.json` 的 verdict 为 `incomplete`。
   最新 `q_m_h_derivation.md` 已把原始 direct slack ADMM 按 He-Yuan 2018
   实例化为 `v=(y,z,lambda)`、`Q`、`M`、`H`、`G`，并由独立 reviewer
   `Linnaeus` 接受推导。结论是 `direct_vi_ppa_condition_failure`：
   在 \(C=I\) slack 特例下，标准 VI/PPA / He-Yuan prototype convergence
   condition 仍失败；`G_slack` 对 \(\Delta v=(\Delta y,B\Delta y,0)\)
   给出负方向，不能吸收 \(\langle B\Delta y,\Delta z\rangle\)。因此 VI/PPA
   目前只能作为 direct route 诊断和 corrected-algorithm repair route，不能作为
   原始 direct ADMM 的收敛证明。这不是严格反例，也不证明 direct slack ADMM 发散。
   修正算法分支本轮推进到两个方向：`q_p_predictor_derivation.md` 已从具体
   proximalized predictor 推出 \(Q_P\)，并给出 \(P_y\succ0,P_z\succeq0\Rightarrow
   S_P\succ0\) 的本地接受推导；`restricted_y_unconstrained_theorem.md` 写出
   \(Y=\mathbb R^n\) 的 z-fixed corrected theorem candidate。Reviewer `Hume`
   初审 verdict 为 `incomplete`：局部矩阵与 feasibility 证据基本成立。最新补充
   `restricted_y_cluster_kkt_limit.md` 已把 \(x\)-block cluster/KKT bridge 写成条件性引理，
   并由 reviewer `Avicenna` 本地接受；`restricted_y_x_boundedness_sources.md` 已把
   \(x\)-boundedness gate 拆成 `x_predictor_bounded`、\(X\) compact、原约束矩阵
   \(A\) full column rank 和 \(\ker A\) coercive/recession 条件，并由 reviewer `Mencius`
   本地接受。最新 `restricted_y_essential_convergence_theorem.md` 已把 VI/PPC 黑箱改写为
   本仓库内的 essential-variable 收敛证明，并由 reviewer `Maxwell` 本地接受。当前
   第一个 `accepted_by_review` 的精确结论覆盖 \(Y=\mathbb R^n\) 的 z-fixed corrected algorithm：
   \(v^k=(y^k,z^k,\lambda^k)\) 收敛，且任意 \(x\)-predictor cluster point 与
   \(v^\infty\) 构成 KKT 点。第二个 `accepted_by_review` 结论是
   `general_y_admg_theorem_candidate.md`：block order \((z,x,y)\) 的 ADM-G modified
   algorithm 在一般 closed convex \(Y\)、\(X=\mathbb R^p\)、\(A^TA\succ0\)、\(B^TB\succ0\)
   下全序列收敛到 KKT/VI solution，reviewer `Anscombe` 已给出 `correct_local`。
   第三个 `accepted_by_review` 结论是
   `general_y_admg_invariant_x_theorem_candidate.md`：把 \(X=\mathbb R^p\) 放宽为
   \(X-\alpha C_{xy}(Y-Y)\subseteq X\)，reviewer `McClintock` 已给出 `correct_local`。
   这些结果都不是原始 direct ADMM 收敛证明；也不覆盖 arbitrary closed convex \(X,Y\)。
5. 反例方向已有 fixed-active-set affine map scaffold、effective-state recurrence、\(T_D\) 块矩阵理论分析、near-unit mode analysis、\(D=I\) quotient reduction 和一般 \(D\ne I\) 的 complementarity reduced map \(R_D\)。fixed-mask 正实扩张已由 `notes/fixed_mask_invariant_impossible_lemma.md` 与 `proof_reviews/fixed_mask_impossible/` 排除为局部模型定理；当前 QP candidate 的 switching cone screen 长度 `2..10` 未找到 expansion。二维 length-2 nonconstant switching 线已经从 screen 转为 proof chain：`PC-0` symmetry、`zero_full`、`zero_single`、`single_full`、`single_single` 均通过本地 review，最终 `proof_reviews/sc1_length2_nonconstant_pairs/verification_report.json` 接受 `SC-1` 局部 theorem。length-3 的 `L3-1a` determinant-zero lemma 已闭合：全部非恒定 length-3 products 都有零特征值；`L3-1b` 已生成全部 `11` 类剩余 cubic factor exact coefficients；`L3-2a` 已构造 Schur/Jury margin objects；`L3-2b-coordinatewise` 已证明 simultaneous diagonalization / coordinatewise 情形下 length-3 product 满足 `rho <= 1`；`L3-2c-rank-one-projector` 已生成 exact boundary artifact，并闭合 `11/11` 个 projective boundary canonical classes；`L3-2d-scaled-rank-one` 已由 single-class certificates 与 assembly artifact 闭合 `11/11` 个 canonical classes；`Stage 4 full-rank interior scaffold` 已把下一层开放面收窄为 `m_rank_one_n_full`、`m_full_n_rank_one` 和 `n_isotropic_m_rotated`；`Stage 4B` 已闭合当前参数化下的 `m_full_n_rank_one` face；`Stage 4C` 已闭合当前参数化下的 `m_rank_one_n_full` face；`Stage 4D` 已闭合当前参数化下的 `n_isotropic_m_rotated` face；`Stage 4E` 已生成 full-rank interior exact rational grid pressure failure map，`2376` 个 interior 压力点上 `negative_margin_count=0`、`zero_margin_count=0`、`determinant_zero_violations=0`；`Stage 4F` 已用稀疏 power-coefficient arithmetic 闭合 selected full-rank target margins；`Stage 4G` 已闭合全部 `11*5=55` 个 full-rank length-3 cubic Schur/Jury margins，其中 `51` 个 one-box Bernstein，`4` 个 depth-1 dyadic repair，proof review verdict 为 `correct` 且 acceptance gate 为 `accepted_by_review`。`Stage 5` 已把 arbitrary switching 改写为 length-2 memory graph proof gate：`64` 条 transitions 中 `60` 条非恒定三步窗口由 Stage 4G 覆盖，`4` 条 constant self-loops 仍需 fixed-mask cone/admissibility 或 cone-restricted path-complete 处理。`AS-2` 已进一步细化：fixed-mask positive real expansion impossible 已 accepted-by-review，可排除 constant self-loop 的 positive outward ray 反例路线，但仍不是 self-loop metric inequality。下一步若继续原算法分支，应处理 `AS-1` path-complete seminorm、`AS-2b/AS-2c` fixed-mask active-region exit 或 cone-restricted self-loop metric、`AS-3` active-cone composition lemma，或走 `AS-4` proof-grade longer-cycle / higher-dimensional counterexample route；不要回到普通 numerical screen。
> **2026-07-11 source-target 状态对齐（覆盖上段 Stage 5 解释）：**
> `proof_reviews/stage5_switching_semantics/` 已确认真实 reduced switching 使用
> \(A_{b,c}\)，而旧 \(R_D\) 只是 \(A_{D,D}\)，二者的一步矩阵不同。随后
> `proof_reviews/stage5_true_switching_transfer/` 已独立接受：任意有限 closed mask word
> 的 true source-target product 与对应 legacy \(R_D\)-product 特征多项式相同。
> 因此，在 Stage 4G 原有二维 full-rank 参数盒、nonconstant period-3 legacy 谱证书的
> 范围内，真实 closed period-3 product 恢复同谱 transfer，继承该 closed product 的
> spectral nonexpansion；这不是 arbitrary aperiodic switching coverage。`TS-1` 已由
> transfer review 关闭，唯一下一分支为 `TS-2` affine itinerary polyhedra：仍须证明
> 实际投影轨道满足 edge polyhedra、处理零坐标 tie convention，并保持 admissibility
> open。详见 `notes/breakthrough_routes/stage5_true_transition_semantics.md`。

5. `outputs/wo5_active_set_2026-07-05/zero_single_relative_angle_symbolic_sublemma.md`：`Qplus D` 的四个 rank-one quotient 均无负 power-basis 系数；`Qconst_minus D` 减去 AM-GM control polynomial 后的四个 remainder 也均无负 power-basis 系数。该结果本身只闭合 rank-one projector 边界；后续 full-chain review 已闭合完整 `Qplus` margin。
6. 本轮新增 `outputs/wo5_active_set_2026-07-05/zero_single_qconst_boundary_neighborhood.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qconst_corner_eigen_localization.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qconst_minus_weighted_bernstein_certificate.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_psd_route.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_psd_minor_diagnostics.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_exact_obstruction_gate.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_relative_angle_localization.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_strip_boundary_certificate.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_strip_neighborhood_charts.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_badbox_endpoint_support.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_endpoint_control_search.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_multicontrol_feasibility.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_slab_residual_multicontrol_feasibility.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_det_square_badbox_diagnostic.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_local_det_square.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_detS_support.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_detS_endpoint_control_search.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_detS_endpoint_geometry_control_search.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_square_reserve_local_attempt.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_square_reserve_local_attempt_stronger.md`、`outputs/wo5_active_set_2026-07-05/zero_single_qplus_explicit_square_split.md` 和 `outputs/wo5_active_set_2026-07-05/zero_single_qplus_partial_square_remainder_gate.md`：前三者把 `Qconst_minus` 从四个角度角点坏盒推进到 rank-one projector 子盒并用 weighted Bernstein certificate 闭合；`Qplus` artifacts 把证明义务改写为 PSD / determinant-plus-square 路线，exact rational-grid gate 未发现 route 或 margin 负 witness，并进一步确认 `Qplus D` 的 Bernstein 失败区域正沿 `s=t` 与 `s+t=1` 两条 relative-angle strips 收缩；两条 strips本身已由 exact Bernstein s-bisection 闭合；strip 邻域已拆成四个三角 chart，`A` 分量闭合，`D` 分量在 depth `2` 仍每个 chart 剩 `5` 个坏盒；endpoint-support 诊断显示这些坏盒的负 Bernstein coefficients 高度集中在 rank-one projector endpoint slabs 上；代表 bad boxes 的简单 endpoint-weighted AM-GM 单控制族未找到 feasible scale；加入 chart slab weights、degree-1 slab residual weights 和有限 angle controls 后，四个代表 bad boxes 仍未找到 LP feasible box；determinant-square exact-grid diagnostic 在 `567` 个代表 bad-box samples 上未发现 `detS` 或 `Qplus` 负值；local exact `det(S)` parity gate 已闭合 `detS_A`，但 `detS_D` 在四个代表 boxes 均未闭合；进一步的 `detS_D` support 诊断显示四个代表盒 `8017` 个负系数中 `8006` 个精确落在 rank-one endpoint slabs 上；degree-8 baseline 与 `{7,8}` near-slab geometry single-control 族均未命中；直接 `Qplus D` 的 endpoint/strip-normal 控制族在 `diag_lower` 代表盒 `(2,1)` 上基础版 `112` controls 和加强版 `634` controls 均 LP infeasible；explicit square split 已 exact 固化共同分母、A/B parity identities 和 \(K_{\rm num}=xP+yR\) 分解；`alpha=1/2` partial-square remainder gate 在同一代表盒上闭合了 `A_alpha`，但 `D_alpha` 仍有 `1738` 个负 Bernstein 系数。这些是历史 localization / proof-attempt artifacts；后续已由 depth-2 covering assembly 和 `notes/zero_single_qplus_full_chain_review.md` 关闭完整 `Qplus` margin。
7. 区分一般 identity-block 模型中的 \(\theta_3\) 与 slack-variable 模型中的 \(0(z)+I_{\mathbb R^m_+}(z)\)。

## 当前不能声明的结论

- 不能声称直接三块 ADMM 对所有 \([A,B,I]\) 实例收敛。
- 不能把随机数值不稳定声称为严格反例。
- 不能把 proof blueprint 称为已验证证明，除非 verifier-style review 或机器检查已经接受全部义务。
- 不能把从文献抽出的 proof pattern 直接套用到本问题，除非假设完全匹配。

## 下一阶段

当前暂停点：二维 reduced active-set length-2 主线已经闭合为局部 theorem。
`single_single` 的 `Jplus D` top-slice / corner-reserve lift 已由
`proof_reviews/single_single_jplus_top_slice_lift/verification_report.json` 接受；
`Jmid` 的 parity gate + exact Bernstein certificate 已由
`proof_reviews/single_single_jmid_bernstein/verification_report.json` 接受；
canonical representative assembly 与 ordered class 已分别由
`proof_reviews/single_single_canonical_assembly/`、
`proof_reviews/single_single_ordered_class/` 接受。随后四类 length-2 nonconstant ordered pairs 的 assembly review 已由
`proof_reviews/sc1_length2_nonconstant_pairs/verification_report.json` 接受，verdict 为
`correct`，review status 为 `accepted_by_review_for_local_sc1_length2_nonconstant_pairs`。
该局部 theorem 只覆盖二维 reduced active-set length-2 products，不等于任意 switching
或全局 direct ADMM 收敛。

VI/PPA/PPC 方向的当前结论保持分支化：标准 He-Yuan / VI-PPA prototype 对原始 direct
slack ADMM 的 `G_slack` 条件失败，不能作为原算法收敛证明；但它仍适合作为
corrected-algorithm / prediction-correction repair route。最新 proof-review 包是
`proof_reviews/vi_ppc_corrected_algorithm/`：`q_m_h_g_derivation.md` 已给出
z-fixed matrix gate，构造 \(W=H^{-1}\) 与 \(M_{\rm corr}=WQ_P\)，使
\((M_{\rm corr})_z=[0,I,0]\)，并在 \(P_y\succ0\)、\(R,E\succ0\) 足够小时用
Schur complement 得到 \(G\succeq0\)。`y_feasibility_or_image_space_gate.md` 进一步说明
该 z-fixed correction 一般移动 \(y\) 或 \(By\)，不保持任意 closed convex \(Y\)，
因此它只支持 \(Y=\mathbb R^n\)、不变 affine \(Y\) 或另行证明 image-space
executability 的限制版路线。一般 closed convex \(Y\) 已由另一条 ADM-G modified
algorithm 路线处理：`general_y_admg_theorem_candidate.md` 经 reviewer `Anscombe`
本地接受，要求 \(X=\mathbb R^p\)；`general_y_admg_invariant_x_theorem_candidate.md`
进一步经 reviewer `McClintock` 接受，允许显式 invariant-\(X\) 条件
\(X-\alpha C_{xy}(Y-Y)\subseteq X\)。arbitrary closed convex \(X,Y\) 仍开放，
`projected_admg_general_xy_theorem_candidate.md` 已降级为 proof attempt；
`image_space_h_projected_fejer_gate.md` 已由 reviewer `Confucius` 接受为抽象代数 Fejer
gate；`closed_image_and_lift_gate.md` 又经 reviewer `Dirac` 审查为 `incomplete`。
随后 `image_regular_corrected_theorem_candidate.md` 尝试 \(v=(c,z,\lambda)\) 的 scaled-\(Q_P\)
image route，但 reviewer `Bacon` 标为 `incomplete_predictor_inequality_open`。
`image_predictor_inequality_lemma.md` 已将 blocker 定位到消去 \(a\)-block 后的额外交叉项。
`full_image_state_predictor_route.md` 已改用 \(w=(a,c,z,\lambda)\)，并由 reviewer
`Chandrasekhar` 接受 predictor inequality 和 \(S_{\rm full}\succ0\) gate；完整收敛和
primal lift 仍开放。

上一阶段已完成的 `zero_single Qplus` 增量是 `notes/zero_single_qplus_depth2_covering_assembly_review.md`、
`notes/zero_single_qplus_diag_lower_depth2_covering.md`、
`notes/zero_single_qplus_diag_upper_depth2_covering.md`、
`notes/zero_single_qplus_anti_upper_depth2_covering.md`、
`notes/zero_single_qplus_anti_lower_depth2_covering.md`、
`experiments/certify_zero_single_qplus_depth2_covering.py` 与
`experiments/analyze_zero_single_qplus_diag_lower_mirrored_quarantine.py`：用户指出“实验偏多”后，
当前 WO-5 已被重新收紧为 theory-first covering lemma。四个 chart 的 depth-2 bad-box
covering 已达到 `20/20`，并通过本地 assembly review。`proof_reviews/qplus_depth2_covering/verification_report.json`
的 verdict 已升级为 `correct_for_depth2_covering_lemma`。机器脚本只能用于 identity /
rational coefficient / exact Bernstein remainder gate。不要回到普通 numerical screen。该结论
仍不是全局 ADMM 收敛证明，也没有严格反例。

按 `work_orders.md` 和 `docs/verymath_toolchain_workflow.md` 调度 VeryMath / AI4Math skills。当前已经完成 WO-3 第一轮 proof-blueprint-review，并补上 VI/PPA direct gate 的 `Q,M,H,G` 实例化与独立审查：标准 He-Yuan VI/PPA contraction condition 对原始 direct slack ADMM 失败。之后曾按 `base_algorithm_counterexample` 分支推进 WO-5 structured all-mask screen、effective-state recurrence、\(T_D\) 块矩阵理论分析、near-unit mode analysis、\(D=I\) quotient reduction、一般 \(D\ne I\) 的 \(R_D\) 约简、抽象 contraction optimization、实际 QP candidate pressure、active-region invariant analysis、fixed-mask invariant candidate screen、multi-agent debate、switching cycle screen、signed-q tangent optimization、positive outward ray targeted screens、fixed-mask impossible lemma 第二版、proof-card review、affine switching cone screen、抽象 switching cone optimization、短周期 nonexpansion conjecture、length-2 product screen、Schur/Jury 诊断、determinant symbolic artifact、boundary-family stress、`single_full` rank-one boundary exact formula、full-rank margin optimization、isotropic 子族解析闭合、mask-aligned angle 切片闭合、zero / identity boundary faces 闭合、mixed rank-one face Bernstein certificate、full two-angle `J+` Bernstein certificate、full two-angle `Jmid` Bernstein certificate、full two-angle sanity margins certificate、single_full cubic margins proof review、length-2 pair-class consolidation、`PC-0` symmetry reduction review、`PC-1` zero_full quadratic margins certificate、`PC-2` zero_single ordered class review、zero_single angle-boundary sublemma、zero_single relative-angle 路线、`Qconst_minus` 角点邻域定位、`Qconst_minus` corner eigenvalue localization、`Qconst_minus` weighted Bernstein certificate、`Qplus` PSD route、`Qplus` PSD-minor 诊断、`Qplus` exact obstruction gate、`Qplus` relative-angle localization、`Qplus` strip-boundary certificate、`Qplus` strip-neighborhood chart localization、`Qplus` bad-box endpoint-support 诊断、`Qplus` endpoint-control search、`Qplus` multicontrol feasibility search、`Qplus` determinant-square grid diagnostic、`Qplus` local det-square Bernstein diagnostic、`Qplus` detS_D support 诊断、`Qplus` endpoint-slab theory obligations、`detS_D` endpoint single-control 排除、`Qplus` square-reserve local lemma、`Qplus D` direct certificate attempts、`Qplus` explicit square split、`Qplus` partial-square remainder gate、fixed-source sign-aware square gate、top-slice 代表盒证书、`anti_lower` quarantine 证书、四个 chart 的 depth-2 covering、depth-2 covering assembly review、`Qplus` full-chain review、`Qconst_minus` proof review、`PC-2 zero_single` canonical representative review、`PC-0` symmetry review、`zero_single` ordered class review、`zero_full` ordered class review、`single_single` Jconst margins certificate、`single_single` Jminus support analysis、`single_single` Jminus rank-one boundary certificate、`single_single` Jminus full-domain certificate 和 `single_single` Jplus support analysis。下一步不要自顾自推进普通数值实验；应在 VeryMath / AI4Math route 上二选一：`base_algorithm_route` 继续寻找 He-Yuan 条件之外的 projection / active-set 理论结构，或 `corrected_algorithm_repair_route` 设计修正算法。

本暂停点的最小开放义务已经不再是 `single_single`。原算法分支已经新增
`notes/length3_switching_gate.md`：`SC-1` 不能直接推出 length-3，因为缺少共同
seminorm / Lyapunov 度量；length-3 非恒定 words 已按 cyclic shift 与坐标交换归为
`11` 类；`L3-1a` determinant-zero lemma 已把每个 canonical product 降到剩余
cubic factor，`L3-1b` 已抽取全部 exact coefficients，`L3-2a` 已构造 Schur/Jury
margin objects，`L3-2b-coordinatewise` 已闭合 commuting 子定理。下一步应处理非交换
二维耦合：当前 `outputs/wo5_active_set_2026-07-05/length3_rank_one_projector_boundary.md`
已把 rank-one projector projective boundary 压到 `6` 个一次、`4` 个二次、`1` 个三次
residual factor，并闭合 `11/11` 个 canonical classes；scaled rank-one scaffold
进一步显示释放 \(m,n\) 后为 `10` 个二次 residual 与 `1` 个三次 residual，其中
`L3C02` 与 `L3C07` 已由 degree `(3,3)` Bernstein 证书闭合，`L3C11` 已由二次
判别式 Bernstein 证书闭合，`L3C01/L3C03/L3C04/L3C05/L3C06/L3C08/L3C09/L3C10` 已由 parity、trace-route
和三角化 Bernstein 证书闭合。scaled-rank-one canonical classes 当前为 `11/11`
closed。Stage 4G 又闭合 full-rank 参数盒上的 `55/55` 个 length-3 cubic
Schur/Jury margins，并由 `proof_reviews/stage4_full_rank_interior_margin_assembly/`
接受为 `accepted_by_review`。但 `proof_reviews/stage5_switching_semantics/` 随后完成
结构纠错：Stage 4G 证明的是 self-consistent fixed-mask matrices
\(R_D=A_{D,D}\) 的抽象 products；真实 reduced switching 使用 source-target matrix
\(A_{b,c}\)。因此原 Stage 5 的 `60/60 covered` 已降级为 abstract word matching，
不能再解释为 projected-ADMM switching coverage。随后
`proof_reviews/stage5_true_switching_transfer/` 已接受任意有限 closed word 的
true/legacy characteristic-polynomial transfer，因此 `TS-1` 已关闭。正确入口仍是
`notes/breakthrough_routes/stage5_true_transition_semantics.md`。`TS-2` 已形成 affine edge
iff 与 closed-word pullback，并已由最终独立 review 接受；代码显式保存 strict/weak rows、
处理零坐标 canonical tie，并守住 proof-grade SPD 域。当前先闭合 affine homogeneous
transfer；该定理现已由 follow-up 独立 review 接受。当前进入具体有理 QP/word 的
exact/rational admissibility certificate，并以 Jordan/affine drift 作为红队靶点。
首个固定有理 QP 的长度 `1..4` 全部 `340` 个标记 words 已完成 exact certificate：
`336` 个 word 的唯一周期点违反 canonical edge row，对应 `315` 个不同 inadmissible
basepoints；`4` 个 witness 是同一个 `[1,0]` self-loop 的重复编码。该结论已由 follow-up
review 接受，不是严格反例。当前转入 unit-root/Jordan/affine-drift 与无限 admissibility gate。
该 gate 的第一轮理论节点已写入
`notes/breakthrough_routes/affine_drift_counterexample_route.md`：标量有限凸 QP 的
self-loops 与最短非恒定 closed word 已通过 exact 解析排除与独立复核；更高维则已把
full-rank 二维 contraction \(M\)、diagonal \(N\) 的 Gray word 化为 exact unit-root gate。
该 gate 已得到 `2500` 个非负五维 Bernstein 系数和 `132` 个零系数；maximal-face
枚举给出候选结构定理
\(\det(I-P)=0\iff\ker(I-M)\cap\ker(I-N)\ne\{0\}\)。所有有限 unit-root
faces 又都在共同单位方向首次被激活时违反 canonical strict row。full-rank extension
已通过独立复核。它不是一般 switching theorem。下一轮只换非等价 length-4 word，
不再扩展普通长度筛查。
第二个非等价 crossed Hamiltonian word `00->11->10->01->00` 已完成 exact 计算：
`2500` 个 Bernstein 系数仍为 `0` 个负、`132` 个零，maximal zero faces 与 Gray 完全
相同；全部 unit-root faces 又在第一条 simultaneous-activation edge 上违反 strict row。
该 exact 排除已通过独立复核。
进一步分类全部 `24` 个 ordered Hamiltonian words：cyclic shift 与 coordinate swap 下有
`3` 个 classes。第三个 reverse-crossed orientation 的 Stage 9 exact certificate 也得到
`2500/0/132` 和相同 8 个 zero faces。因此三个代表元共同给出候选全 Hamiltonian theorem：
任意此类 word 的单位根等价于 \(M,N\) 有公共单位方向，而 Hamiltonian 的
inactive-to-active edge 必违反对应 canonical strict row。该综合 theorem 已通过独立复核。
四条 constant self-loops 因 source=target 仍可复用 fixed-mask 结论。AS-2 的 fixed-mask
positive outward ray 已由 `proof_reviews/fixed_mask_impossible/` 接受为局部二次模型
排除结论，但还不是 self-loop metric inequality。下一步优先处理 `TS-2`，
随后才是基于 \(A_{b,c}\) 的 `AS-1` path-complete seminorm、`AS-2b/AS-2c`
fixed-mask active-region exit 或 cone-restricted self-loop metric、`AS-3`
active-cone composition lemma；若失败，
再走 `AS-4` exact longer-cycle / higher-dimensional proof-grade counterexample route。
VI/PPA/PPC 分支则应单独走
`notes/vi_ppc_corrected_algorithm_route.md` 和
`proof_reviews/vi_ppc_corrected_algorithm/`：当前 \(Y=\mathbb R^n\) z-fixed theorem
与一般 \(Y\)、\(X=\mathbb R^p\) 的 ADM-G theorem、一般 \(Y\) 且 invariant-\(X\) 的
ADM-G theorem 均已 accepted-by-review；image-space full \(H\)-projected Fejer gate
也已作为抽象代数 lemma 接受，但 arbitrary \(X,Y\) lift route 已由 Dirac 标为
`incomplete`。当前 full-image-state convergence theorem 已由 reviewer `Halley`
接受为 image-regular corrected theorem；下一步若继续修正算法，应处理 arbitrary
\(X,Y\) 所需的 closed value functions、closed image domains、fiber attainment 和 executable selection。
若回到原问题，则继续 original direct
ADMM 的 active-set / switching proof 或 proof-grade counterexample。

Hamiltonian length-4 theorem 完成后，主线已重新锚定到原优化问题，而不是继续枚举谱证书。
`notes/optimization_anchored_quotient_lyapunov_route.md` 记录当前 proof blueprint：固定 strict
cell 内正交象限投影只是等距反射，严格下降必须来自完整周期的 \(x/y\) 最优性与跨-cell
投影耗散；下一主关口是周期能量恒等式、零耗散到公共中性空间
\(E=\ker(I-M)\cap\ker(I-N)\) 的等号刚性，以及 quotient 收敛到原问题 residual/KKT/
目标值的桥。组合上，任意 mask 序列可分为最终真子图或 greedy first-cover blocks，但 cover
长度可无界，因此 Hamiltonian length-4 结果不能直接推出任意切换。红队当前唯一最短危险类为
`01->10->11->01`；其单块 Bernstein 证书有两个负系数但尚无零点、单位圆/Jordan 或可达
affine-drift candidate，只能记为 `exact_certificate_gap`。

原优化问题方向现已推进到 `notes/one_step_kkt_energy_identity.md`：在仅假设 proper closed
convex、子问题可解和 KKT 解存在时，三个 lag-error 最优性条件给出精确一步能量恒等式。
正项是 x-step 预测残差与三个单调性余量；唯一无定号项为
\(-2\beta\langle B(y^{k+1}-y^\star),z^{k+1}-z^k\rangle\)。闭周期离散分部积分不会消掉
该项。一维强凸 exact active-cell 例进一步证明相关增量交叉项可正可负，故
projection-only / period-telescoping 路线不能直接闭合。另一方面，residual、两个
stationarity gap 与精确 complementarity 已接回原 KKT：剩余桥只需证明
\(\Delta\lambda^k,B\Delta y^k,\Delta z^k\to0\) 及轨道有界。下一正向入口限于真实
itinerary cone control 或 full-image coupled metric。

上述节点现已通过独立逐行复核，verdict 为 `correct`。一步恒等式经独立符号展开余项为零，
闭周期分部积分和一维 exact obstruction 均复算通过；KKT/目标值部分只作为条件桥接受，
不代表原算法渐近正则性已证明。正式 review 在
`proof_reviews/one_step_kkt_energy_identity/verification_report.json`。

下一轮同时检查静态 full-image metric 与真实 itinerary-cone control。候选结果写入
`notes/full_image_metric_and_cone_obstruction.md`：一般静态 \((By,z,\lambda)\) 耦合二次型的
精确一步展开在系数恒等消项模板下要求耦合系数同时满足 \(c=0\) 与 \(c=1\)；二维强凸
唯一-KKT 的全有理 strict fixed-mask 例又使核心能量从 \(1/4\) 经两步变为
\(2777/8192\)，净上升 \(729/8192\)，排除了 cell-sign-only 下降。初版例子的 source
落在 tie boundary，已由独立复核拒绝；当前用 \(\lambda^0=(0,-1/2)\) 完成严格有理修复，
并已通过第二轮独立复核。两者都不是 ADMM 发散反例。正向加强定理的候选
Schur gate 为 \(2\mu_B\gamma_z\ge\beta^2\)；无附加假设路线则必须进入 history/phase metric
或更长 itinerary 耗散。该节点状态为 `accepted_by_independent_review`。

随后的一阶 history / strengthened gate 候选写入
`notes/history_metric_and_strengthened_gate.md`：不利用真实 recurrence 时，有限一阶历史项仍不能靠
纯系数消项去掉坏项；\(By\)-像空间强单调可由
\(G-\mu_B\|B\cdot\|^2/2\) 的凸性核查，但独立 \(\gamma_z>0\) 被一维 strict full-active
拆分方向精确排除。因此下一正向门改为联合 \((B(y-y^\star),\Delta z)\) 的逐 edge
cone-restricted 二次证书。该节点尚待独立复核。

联合逐-edge scaffold 已实现于 `src/admm_identity/edge_energy.py`，数学契约记录在
`notes/joint_edge_energy_certificate.md`。API 精确构造核心 KKT 能量差
\(Q_{b,c}=H_b-\widehat A_{b,c}^\top H_c\widehat A_{b,c}\)、TS-2 齐次 rows 与 strict flags，
并实际验证 reference point 的 quadratic KKT 条件。修复后的 strict fixed-mask obstruction
已加入回归测试，证明未修正核心能量在一个真实 self-edge 上严格增加；因此下一步必须允许
phase/history correction 或多步 block metric，再构造控制
\(\Delta\lambda,B\Delta y,\Delta z\) 的 \(C_{b,c}\)。该实现待独立复核。

上述 numerical assembly 前端现已通过三轮独立红队：补齐了 \(Q_1,Q_2\succeq0\)、finite
positive \(\beta\)、逐坐标尺度感知 normal-cone/complementarity、统一 KKT tolerance API 与
strict-margin 回归。最终 verdict 为 `ship`，见
`proof_reviews/joint_edge_energy_certificate/final_verification.json`。它仍不是 cone-positivity
证明；下一实现义务保持为 \(C_{b,c}\) 与 phase/history correction。

`edge_energy.py` 随后补上 `dissipation_map`，从同一个齐次 source state 精确输出
\((\Delta\lambda,B\Delta y,\Delta z)\)，并通过与直接 ADMM step 的定向回归。当前实现义务
只剩 phase/history correction 与 cone-restricted feasibility。

## 2026-07-12 Phase Metric 理论闭环

固定有理 QP 的四个 phase matrices 已被重写为六参数 observable ansatz。精确恒等式
\(A_{bc}=J_c\widetilde A_b\) 与 \(J_c^\top H_cJ_c=H_c\) 说明 target mask 只产生可由度量
吸收的符号作用；同一组 \(H_b\) 的耗散系数可由 \(1/20\) 提升到 \(13/180\)。该结构定理
已通过独立复核，见 `notes/phase_metric_six_parameter_ansatz.md` 和
`proof_reviews/phase_metric_six_parameter_ansatz/final_verification.json`。

红队同时构造了一个固定 SPD QP 的 exact Farkas 证书：九个正权 rank-one PSD 原子消去
四个对角 \(H_b\) 的全部 16 个变量，并得到加权 primal residual 总和 \(-1\)。独立复核确认
该证书只排除对角 phase metrics；12 个非对角 adjoint 系数仍非零，所以它不排除一般对称
度量，更不是 ADMM 发散反例。证据见 `notes/diagonal_phase_farkas_obstruction.md`。

正向分支已形成 `notes/small_gain_common_metric_theorem.md`：若 reduced blocks 的四类算子范数
满足显式界，则 common metric \(H=\operatorname{diag}(I,9I/4)\) 对任意 source-target edge
严格收缩，并给出 exact 余量 \(71391/16000000\)。独立复核已接受 recurrence、乘子符号、
比较矩阵、耗散界、tie 语义和 KKT 桥，正式状态为
`theorem_with_exact_certificate_and_independent_review`。下一理论步不是扩大数值筛查，而是
解析优化 \(K_\tau\) 的 block scaling，寻找存在 \(\tau>0\) 的精确可检验条件。

该 scaling 问题现已解析闭合。对非负比较矩阵
\(K_\tau=\begin{psmallmatrix}a&b/\tau\\\tau c&d\end{psmallmatrix}\)，存在 \(t=\tau^2>0\)
使 \(\|K_\tau\|_2<1\) 当且仅当
\(a<1,d<1,bc<(1-a)(1-d)\)。若 \(b,c>0\)，唯一最优 scaling 是 \(t=b/c\)；三个
退化情形也有显式严格可行选择。该结果与 ADMM 耗散/KKT 桥已通过独立复核和 1296 组
额外有理参数检查，见 `notes/optimized_small_gain_scaling_theorem.md`。下一正向推论是将
此门槛消元到 \(Q_1=q_1I,Q_2=q_2I\) 的显式二维参数区域。

该消元现已闭合：任意维数的各向同性族 \(Q_1=q_1I,Q_2=q_2I\) 满足 optimized gate
当且仅当 \((1+q_1)(1+q_2)>2\)，且最优 scaling 为 \(t=q_1/q_2\)。每个固定有理内点
都有严格 rational \(\gamma,\rho,\varepsilon\) 见证，但靠近边界时 margin 趋零，不能声称
全开区域统一收缩。该定理已通过独立复核，见 `notes/isotropic_small_gain_family_theorem.md`。

红队则已把一般对称 phase-metric 排除问题建模为完整 Farkas 优化，见
`notes/full_symmetric_phase_farkas_optimization.md`。该设计禁止给 primal \(H_b\) 加任意
trace cap，并要求完整 40 个 adjoint 系数、exact PSD、正有理 gap 和独立复核。当前只是
经独立红队接受的 `research_design`，尚未找到 full-symmetric obstruction，更不是 ADMM
反例。普通 dual 只覆盖严格 Farkas 分离；weak infeasibility 必须另走 facial reduction、
extended dual 或 hyper-feasible partition。

small-gain 之外的真实-region 路线进一步闭合了标量全参数定理。对任意
\(q_1,q_2>0\)，inactive 一步将 canonical state 重置到正/负两条射线；负射线以
\(mn+(1-m)(1-n)<1\) 不变收缩，正射线随后永久 active，而 active 驻留矩阵的特征值
恰为 \(m,n\in(0,1)\)。任意轨道至多改变一次 mask。两名独立 reviewer 已接受解析分类、
tie 与原变量 KKT 桥，并完成大规模 exact rational 红队检查。正式定理见
`notes/scalar_all_parameter_convergence_theorem.md`。该结果覆盖标量 small-gain 遗漏区，
但不能外推到非交换高维 \(M,N\)。

## 2026-07-12 Reduced block gate 与边界红队

本轮把 phase metric 的结构来源从 (A=B=I) 推广到任意有限维 (A,B) 的强凸二次
slack QP（仍取 (b=0)）。由 canonical state (r=(y,u))、source mask (D) 和
target sign (S_C) 得到精确 reduced recurrence

\[
R_{D,C}=\begin{pmatrix}
PMB&-P(I-M)\\
S_C(I-N)MB&S_C\{N+(I-N)M-(I-D)\}
\end{pmatrix},
\]

其中 (M=\beta AH_x^{-1}A^T)、(N=\beta BH_y^{-1}B^T)、
(P=\beta H_y^{-1}B^T)。目标 mask 只通过正交符号 (S_C) 出现，source mask 只进入
最后的 signed block。由

\[
a=\|PMB\|,\quad b_0=\|P(I-M)\|,\quad c=\|(I-N)MB\|,\quad
d=\max_D\|N+(I-N)M-(I-D)\|
\]

和精确二维条件

\[
a<1,\quad d<1,\quad b_0c<(1-a)(1-d)
\]

可取 (t=b_0/c)（正耦合时），构造 (H=\operatorname{diag}(I,tI)) 的 common metric，
并得到所有 source-target edges 的严格收缩。这是一个可检验充分条件，不是一般模型
收敛定理。完整定理见 `notes/general_ab_small_gain_phase_gate.md`，非方阵 (B) 的有理
exact 见证见 `outputs/breakthrough_attempts/stage20_general_ab_small_gain/`。

本轮测试为 `tests/test_general_ab_small_gain.py` 的 `4 passed`；证书由原始有理
\(A,B,Q_1,Q_2\) 重建，未使用 solver 或浮点谱值。边界红队也已写入定理卡：标量
\(q_1=1/3,q_2=1/2\) 使 comparison gate 精确出现单位根，但由标量全参数定理仍收敛；
因此 gate 失败不能称为严格反例。一般非交换高维模型、非零 (b)、非二次目标和 gate
之外的 phase/cone 度量仍开放。

## 2026-07-12 Selector-IQC 全局条件

上一节的唯一指数级部分是

\[
d=\max_D\|D-(I-N)(I-M)\|_2.
\]

令 (G=(I-N)(I-M))、(p=Du)。binary selector 对任意对角 (W) 满足精确恒等式

\[
p^TW(u-p)=0.
\]

因此若存在对角 (W) 和 (0<\bar d<1)，使

\[
\begin{pmatrix}
\bar d^2I-G^TG&G^T-W\\
G-W&2W-I
\end{pmatrix}\succ0,
\]

则一次 (2m\times2m) LMI 即推出全部 masks 的
(|D-G|_2<\bar d)。结合 optimized small-gain 条件即可构造
(H=\operatorname{diag}(I,tI)) 的解析 common metric。该结论已完成 exact witness、边界
attaining direction 和两名独立 reviewer 的“初审 needs_fix -> 修复 -> follow-up correct”
闭环，正式记录见 `proof_reviews/selector_iqc_global_mask_condition/`。

边界红队精确确认：非方阵 (B) 见证的真实最大 mask norm 为 (9/10)，严格 LMI 必须取
更大的有理 bound（当前取 (91/100)）；在等号边界上 quadratic gap 为零。这个等号只排除
严格证书，不是 ADMM 发散反例。

进一步，对角 (G=\operatorname{diag}(g_i))、(0<g_i<1) 情形已得到无损定理：

\[
d_*=\max_i\max\{g_i,1-g_i\},
\]

且对角 multiplier LMI 严格可行当且仅当 (\bar d>d_*)。三个分支
(g_i<1/2)、(g_i=1/2)、(g_i>1/2) 都有显式 (w_i)。Stage 22 exact 证书已通过
定向测试和独立复核，最终 verdict 为 `correct`。该无损性只适用于固定 orthant 坐标中的对角 (G)，不能由
一般正交对角化外推到非交换高维模型。

## 2026-07-12 Selector-IQC 非正规鲁棒扩张

对任意严格基点 \(\mathcal R_d(G_0,W)\succeq\mu I\)，若
\(\|G-G_0\|_2\leq\varepsilon\) 且

\[
(2\|G_0\|_2+1)\varepsilon+\varepsilon^2<\mu,
\]

则同一对角乘子 \(W\) 仍使 \(\mathcal R_d(G,W)\succ0\)。这是从对角 phase metric
到非正规耦合的解析稳定性来源，不依赖 SDP synthesis。

Stage 23 用非交换对称收缩矩阵
\(M=\operatorname{diag}(1/2,1/10)\)、
\(N=\bigl(\begin{smallmatrix}1/2&1/100\\1/100&1/6\end{smallmatrix}\bigr)\)
给出可由强凸二次 QP 精确实现的非正规见证。鲁棒余量为 \(7419/10^6\)，small-gain
余量为 \(389/5000\)；独立 reviewer 最终 verdict 为 `correct`。这仍是充分条件，既不覆盖
任意非交换 \(M,N\)，也不把门失败解释为发散。

## 2026-07-12 Gate 外固定 QP 的 Signed-PWA 闭环

固定

\[
Q_1=3I,\qquad
Q_2=\frac1{779}\begin{pmatrix}4421&2500\\2500&1921\end{pmatrix},
\qquad A=B=I,\ b=0,\ \beta=1.
\]

该实例对旧 small-gain gate 的 \(a\leq1/6\)、\(b\leq1/2\) 两项均以 exact negative
Gram determinant 失败，但 signed state \(s=(y,q)\)、\(q=z+\lambda\) 的四个 PWA
分支全部满足

\[
B_D^THB_D\prec(99/100)^2H,
\qquad H=\operatorname{diag}(I,9I/4).
\]

原 ADMM 消元、facet 连续性、16 条 edge conjugacy、跨 orthant 全局增量收缩、fixed
point 与 KKT 双向等价均已闭合并独立复核。因此该 gate 外 QP 对任意有限初值全局几何
收敛到唯一零 KKT 点。这是固定 QP 正式定理，不是一般模型结论。

## 2026-07-12 Affine Family 与开放邻域闭环

对 Stage 25 的 fixed Hessians，任意 rhs \(b\) 和目标一次项 \(c_1,c_2\) 只在 signed-PWA
映射中产生与 orthant 无关的共同 offset

\[
k=\binom{Nr}{(I-N)r+c_2},\qquad r=(I-M)b+Mc_1-c_2.
\]

因此全局增量收缩常数仍为 \(99/100\)。Fixed point 与 affine KKT 双向等价，并已有非零
rhs、非零一次项的 exact 有理见证。

更进一步，对任意实对称 \(M,N\) 满足
\(\|M-M_0\|_2,\|N-N_0\|_2\le1/100\)，同一 \(H\) 和 \(\gamma=99/100\)
仍严格有效。统一 signed-branch 扰动界为 \(34/625\)，最终 residual 余量为
\(405667/3125000>0\)。所以整个 reduced Hessian 邻域、任意 rhs 与任意一次项均对任意
有限初值全局几何收敛到各自唯一 KKT 点。两条独立 reviewer verdict 均为 `correct`。

本轮 proof-grade 审计又补齐：独立原 ADMM oracle、任意 affine 数据的逐 mask 符号恒等式、
四个扰动块及 residual 常数的机器重构、Weyl domain margins，以及机器证书与外部复核 provenance
分离。两个 review 目录均有 `review_manifest.json`，Hubble 最终 verdict 为 `correct`，Helmholtz
为 `RELEASE`；P0/P1 定向测试为 `14 passed`。

全量 pytest 运行得到 `209 passed, 2 SIGKILL`；两个 SIGKILL 都发生在子进程启动阶段，分别是
历史高内存 Bernstein gate 和 Stage 25 CLI。隔离复跑二者均通过（99.47 秒与 0.44 秒），因此
当前证据记录为资源峰值而非测试断言回归，不能写成“全量一次运行全绿”。

## 2026-07-12 任意维 Common-Metric 与 Exact 周期门

`notes/arbitrary_dimension_signed_pwa_common_metric_theorem.md` 已由独立 reviewer 接受。对任意维
\(A=B=I\) 强凸二次 slack QP，它证明全部 signed branches 的 common LMI
\(B_D^THB_D\preceq\gamma^2H\) 与全局同一 \(H\)-Lipschitz 性等价；当 \(\gamma<1\) 时，
任意 rhs、一次项和有限初值全局几何收敛到唯一 KKT 点。Stage 28 给出 \(n=3\) exact witness，
并用 \(\beta=7/3\) 的独立原 ADMM oracle、affine KKT fixed point 和 facet tangent checks
交叉验证。该结论是任意维条件定理，不声称所有 \(M,N\) 都存在 common metric。

`notes/singular_periodic_itinerary_exact_lp_gate.md` 也已由独立 reviewer 接受。对
\(\det(I-P)=0\) 的有理 closed word，checker 现在总是输出正 strict-margin witness、
zero-margin dual 排除或 Farkas 不可行证书，不再留下 parametric-LP 占位。scalar boundary
长度不超过 4 的 30 个奇异 words 中，8 个恒定 words 可行，22 个非恒定 words 被 exact
zero-margin dual 排除。

反例端直接优化 canonical periodic-cell 最小 margin，而非谱半径。二维 length 2--5 共
\(15+37+105=157\) 个 canonical 非恒定 words 没有正候选；length 2--3 最佳值约
\(2.78\times10^{-17}\)，length 4/5 最佳值为数值零，危险 word
\(01\to10\to11\to01\) 最佳值约 \(-6.02\times10^{-3}\)。这些只能标为 deterministic
optimization failure map，不证明不存在非恒定周期轨道。中文边界记录见
`notes/nonconstant_periodic_margin_failure_map.md`。旧版 inactive-row margin 语义已修正，全部
157 个 words 已重新优化；奇异周期仍由 exact LP/Farkas gate 处理。零边界理论进一步约简为
`notes/nested_mask_fractional_selector_route.md` 的 fractional-selector 端点正性义务，并已闭合
最短 nested-mask 二周期：对 $D=\operatorname{diag}(0,1)$，Cayley 分解与 PSD contraction
下界给出

\[
\det(I+B_D)\ge\frac5{16}\det(I+M)\det(I+N)>0.
\]

rank-one selector 插值继而严格排除 canonical `01 -> 11 -> 01` 及坐标交换后的
`10 -> 11 -> 10` 二周期。该定理已有 exact symbolic identity certificate、26 项联合回归和
独立 reviewer 的 `correct` verdict；它不排除更长周期。

更长嵌套周期的下一理论入口已写入 `notes/nested_mask_long_cycle_obligations.md`。任意长度可由
两个端点的共同 averagedness LMI 条件性排除；最短未覆盖的三周期进一步缩为四个 exact
端点 $\det(I+B_T+B_jB_T)$ 的同号非零义务。当前尚未证明这些条件对任意
$0\prec M,N\prec I$ 成立，不能声称一般 `01`/`11` 无周期。当前仍没有严格反例。

## 2026-07-13 嵌套三周期与 Averagedness 障碍

`notes/nested_mask_long_cycle_obligations.md` 已新增两个独立复核通过的 exact 节点。第一，若
$M,N$ 在固定 orthant 投影坐标中对角，则四个三周期端点
$\det(I+B_T+B_jB_T)$ 均至少为 1；证明由 exact factorization 和 $g_{Tj}-1$ 的二阶
tensor Bernstein 非负系数给出。因此该 coordinatewise 子族不存在仅经过 `01`/`11` 的
非恒定三周期。该结论不能由任意共同正交对角化外推，因为 orthant selector 不保持。

第二，共同 averagedness LMI 虽然条件性排除任意长度嵌套周期，但不具有普适性。Stage 31
给出严格有理 $0\prec M,N\prec I$，使 $B_{01}$ 的 cubic Jury margin

\[
J_{\rm mid}
=-\frac{433775258062294638209}{40047143579101562500000000}<0,
\]

故 $\rho(B_{01})>1$，全空间 common averagedness 对该实例不可能成立。扩张方向没有被证明
留在 `01` active cell，因此这不是 ADMM 发散反例。一般主线现在只剩：证明非交换四端点
$\det(I+B_T+B_jB_T)>0$，或加入 itinerary cone/phase metric 构造真实可达证书。

## 2026-07-13 三周期 Cayley 完整端点定理

`notes/nested_three_cycle_cayley_reduction.md` 已通过独立复核。对一般非交换
$0\prec M,N\prec I$，四个端点具有统一 Cayley 表示

\[
E_{Tj}=
\frac{\det(3I+Q_j-Q_T+Q_jQ_T)}
{\det(I+Q_j)\det(I+Q_T)}.
\]

其中 $E_{11}>0$ 由 block-triangular factorization 直接得到；$E_{01}>0$ 由 rank-one
determinant lemma、Cayley resolvents 和二维 PSD 乘积下界得到显式正余量
$(13-4\sqrt7)/96$。Stage 33 进一步以函数演算和 PSD 乘积界证明
$\sigma_{10}\ge37/144$，从而闭合 $E_{10}>0$。Stage 34 对最后的 $E_{00}$ 端点把假设零点
$\pm i\sqrt3\in\sigma(Q_0)$ 化为必要条件 $L-r=3/14$，再由 resolvent 分解、函数演算与
维数无关 PSD 乘积界得到

$$
L-r\ge\frac7{32}=\frac3{14}+\frac1{224},
$$

故 $E_{00}>0$。四个端点现已全部严格为正，并经独立 proof-obligation audit 接受；因此一般
非交换 $0\prec M,N\prec I$ 下仅经过 `01`/`11` 的非恒定三周期被严格排除。Stage 32--34
的 exact rational regression 只核对代数与常数，不替代一般证明。下一 blocker 已后移到
length $\ge4$ 的 fractional-selector products、真实 itinerary cone 或 phase metric；当前仍
没有严格 ADMM 发散反例。四周期的精确起点现记录在
`notes/nested_mask_length4_frontier.md`：非零四增量周期等价于零和算子 $S_4$ 与闭合算子
$P_4-I$ 具有非零共同核。进一步的独立复核把 binary itinerary 压到六个循环类，给出交替类
$r_0r_2=r_1r_3$ 的 selector 充要约束，并把 $P_4-B_1^4$ 的像限制在四维 Krylov 通道。
这些 reduction 已通过独立复核，但共同核与真实 itinerary cone 仍未关闭，因此不是四周期
排除定理。

## 2026-07-14 四周期总装与严格 66 周期反例

四周期端点线已经闭合。`notes/nested_length4_all_endpoint_assembly.md` 将
multi-affine determinant reduction 与 $S_{000},\ldots,S_{111}$ 八个严格正端点总装，得到

$$
\det\{I+B_a+B_bB_a+B_cB_bB_a\}>0,
\qquad(a,b,c)\in[0,1]^3.
$$

因此 nested one-coordinate rank-one 模型不存在非平凡 length-4 zero-sum increment
sequence。总装审计补上了两个 proof-critical 符号点：
$\det(I+Q_0)/\det(I+Q)=2/(1+3t)>0$，以及 $S_{110}$ 的非交换余项应写成
$C\,p(C,A)\,A$。Stage 41 exact guard 与 7 个端点/总装定向测试通过。
`notes/nested_any_length_zero_sum_scalar_collapse.md` 还把任意闭合长度的零和条件精确降为
$\sum_j\rho_jz_j=0$；该引理只降维，不排除长周期。

一般收敛主线随后得到决定性反方结果。Stage 43 将 exact expanding mixed branch 嵌入一个
strict-complementary KKT 点，严格否定任何在 KKT 邻域逐步单调且局部控制范数的 static 或
finite-history quadratic Lyapunov。沿该失败方向做真实 ReLU itinerary 搜索后，Stage 44 找到并
exact rational 化一个 66 周期：

$$
\mathcal W=(00,00,\underbrace{01,\ldots,01}_{64\text{ 次}}).
$$

反例满足 $A=B=I_2$、$\beta=1$、$Q_1,Q_2\succ0$，并可通过精确平移写成
$c_1=c_2=0$ 的纯强凸二次目标。66 步 closure、唯一 KKT、原始 $x/y/z/\lambda$ updates、
132 个 orthant inequalities 和最小周期全部由 SymPy 有理算术重验；uniform strict margin
大于 $1/1000$。当前论文冻结的短参数实例
`identity_slack_p66_short_v1` 使用 $\mu=8957/10000$、$\nu=999/1000$，实际最小值为
$0.0037105246944352910173\ldots$；早期八位参数实例的
$0.004341079684406849\ldots$ margin 仅作为 legacy provenance 保留，不得与投稿实例混用。
证书状态为
`proof_grade_strict_rational_66_cycle_counterexample`。

因此原始 direct slack 三块 ADMM 的无条件全局收敛命题为假，即使两个目标都是纯强凸二次函数。
这是 bounded periodic nonconvergence，不声称 iterates 无界。已有 small-gain、common-metric、
scalar/diagonal/nested-short-cycle 等条件定理仍有效；后续正向工作应改为刻画排除该 66-cycle
机制的最小附加条件，或研究 corrected algorithm，而不是继续追求不存在的一般定理。

主要 artifacts：

- `notes/strict_rational_66_cycle_counterexample.md`
- `experiments/breakthrough/certify_strict_rational_66_cycle.py`
- `outputs/breakthrough_attempts/stage44_strict_rational_66_cycle/certificate.json`
- `proof_reviews/strict_rational_66_cycle/adversarial_risk_register.md`

Provenance 边界：当前是 Codex adversarial audit + exact rational guard，尚未取得外部独立 reviewer；
不得改写为 external-independent review。

## 2026-07-14 Full-state 第二实现与最终报告

为降低 Stage 44 周期构造和原 ADMM 回代共享 signed recurrence 所产生的 common-mode 风险，
Stage 45 新增了不导入原 checker 的六维 raw-state 复算。它从
(u=(y,z,\lambda)) 和原始两个强凸子问题出发，用 exact basis evaluation 重建 target-selector
affine maps，独立求解 (T_0\circ T_1^{64}\circ T_0) 的 period fixed point。线性项与零线性项
两个 QP 的 66 步闭合、source/target mask、(x/y) 最优性、投影、乘子更新、严格余量和平移
共轭全部为 true；还检查了 phase 1--65 均不提前返回。

该结果是 implementation-independent cross-check，不是外部独立 reviewer。当前投稿实例的统一
source of truth 为 `report/latex/arxiv/instance_manifest.json`；其中 raw 6D 与 signed 4D
certificates 必须共享 instance、initial-state、orbit、word 与 minimum-margin hashes。
`report/final_resolution_2026-07-14.md` 现标记为八位参数 legacy 记录；Stage 44 与 Stage 45
历史 certificate 仍需保留用于 provenance。

## 2026-07-14 VI/PPA 与先例审计

文献审计已把“已有一般非收敛”与“当前结构化反例”分离。Chen--He--Ye--Yuan (2016)
已经包含一般系数矩阵下的 direct 三块发散以及三块目标均强凸的扩展，因此不能把“三块不收敛”
或“强凸仍不收敛”写成新结果。He--Xu--Yuan (2023) 的式 (1.7) 则明确写出了与本项目等价的
slack-last EADMM，并指出无附加限制时没有收敛保证、应加入 correction；但该文没有给出
identity-slack 子类内的严格反例。

当前检索未发现同时匹配以下指纹的先例：\([I_2,I_2,I_2]\)、正象限 slack、
\(x\to y\to z\to\lambda\) 原始顺序、前两块纯强凸有理二次、严格有界精确有限周期。
因此可使用“据本次检索所知，首个 identity-slack 子类的严格有界周期反例”，但必须保留
`to the best of our knowledge` 限定，不能声称数据库检索证明绝对优先权。

VI/PPA 正向结果主要针对两块 Douglas--Rachford/PPA，或把 direct sweep 当 predictor 后加入
correction、Gaussian back substitution、proximal/metric projection。仓库内 direct specialization
的 \(G_{\rm slack}\) 负方向说明标准收缩门不适用；只有 Stage 44/45 的 66 周期才把路线失败
提升为真正反例。Lin--Ma--Zhang (2015) 对不等式模型的正向结果采用 slack-first 顺序并要求
小罚参数；对当前 Hessian 的显示充分上界约为 \(0.00116635\)，不覆盖 slack-last 的
\(\beta=1\)。完整出处、匹配表和检索边界见上述先例审计 artifacts。

## 2026-07-16 乘子松弛的局部区间与有限前缀捕获

固定 Stage 44/45 的同一个有理 QP，把乘子更新改成

$$
\lambda^{k+1}=\lambda^k-\tau
(x^{k+1}+y^{k+1}+z^{k+1}-\bar b).
$$

`notes/relaxed_multiplier_interval_theory.md` 已把原先仅在 $\tau=1/2$ 的固定轨道证书提升为
三层定理：严格 KKT 分支的局部收敛、共同 Lyapunov 步长区间、有限严格前缀捕获。对当前
实例，原有理矩阵 $H$ 在

$$
49/100\le\tau\le51/100
$$

上给出共同局部收缩；证明使用两个端点的 exact Sylvester 主子式和
$F(\tau)=H-T(\tau)^THT(\tau)$ 的 Loewner 凹性。对原 66 周期初值，232 步逐坐标有理敏感度
包络进一步认证非退化区间

$$
\frac{4999999999}{10000000000}
\le\tau\le
\frac{5000000001}{10000000000}
$$

内的真实轨道统一进入同一个投影安全椭球，故整段步长都收敛到唯一 KKT 点。该区间很窄是
当前 componentwise wrapping bound 的保守性，不是最大稳定区间。

严格 `01` 分支的 6 阶特征多项式还精确分解为 $z(z+\tau-1)$ 与一个四次因子。Schur 递推和
Sturm 根计数把局部稳定边界定义为显式整数三次多项式 $G(\tau)$ 在 $(0,1)$ 中的唯一根，且

$$
0.9366061114<\tau_c<0.9366061115.
$$

因此 $0<\tau<1$ 内，固定 `01` 分支 Schur 稳定当且仅当 $\tau<\tau_c$。这仍只是局部谱边界，
不能改写为任意初值全局收敛阈值。exact 证书、8 个定向测试和内部 verifier-style review 均已
通过；provenance 不是外部同行复核，也不是 proof-assistant formalization。

主要 artifacts：

- `notes/relaxed_multiplier_interval_theory.md`
- `experiments/breakthrough/certify_relaxed_multiplier_interval_theory.py`
- `outputs/tau_relaxation_theory_2026-07-16/results/certificate.json`
- `proof_reviews/relaxed_multiplier_interval_theory/`
- `tests/test_relaxed_multiplier_interval_theory.py`
