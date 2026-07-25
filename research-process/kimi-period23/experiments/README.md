# experiments/ 复现指南

环境：Python 3.13.5 + numpy 2.1.3 + scipy 1.15.3（系统环境，无额外安装；未使用任何付费/凭据服务）。
所有脚本种子固定（见各文件头部），结果摘要写入 `results/*.json`。

| 脚本 | 用途 | 约耗时 |
|---|---|---|
| `admm_core.py` | 核心迭代库（齐次等式/松弛步、模式矩阵、谱扫描） | — |
| `test_t_reduction.py` | t-化简与直接迭代轨迹一致性 | <2s |
| `exp1_chyy.py` | 复现 CHYY 2016 发散反例（ρ=1.0278393033） | <2s |
| `exp2_spectral_search.py` | （v1）谱搜索——矩阵笔误，结果作废 | — |
| `exp2b_verify_thmH.py` | （v1）定理 H 双射核验——同上作废 | — |
| `exp4_verify_thmQ.py` | （v1）定理 Q 核验——同上作废 | — |
| `exp3_practical.py` | 96 个带已知 KKT 解的实际问题收敛行为 | ~6s |
| `exp3b_v_increases.py` | Lyapunov 候选 V 的增量形态分析（导入时会先跑 exp3 套件） | ~12s |
| `exp5_jsr.py / exp5_jsr_lite.py` | 切换层面 JSR 估计（修正矩阵后） | ~2s |
| `exp6_jsr_deep.py` | JSR 深探（长 4000 随机乘积 + 束搜索） | ~8s |
| `exp7_realizable_cycles.py` | 可实现扩张周期轨道穷举（m=2 序列≤8，m=3 ≤5） | ~400s |
| `exp8_adversarial.py` | 对抗轨道增长 + ℓ1 目标 + b≠0 搜索 | ~260s |
| `exp9_consistent_search.py` | 实 μ>1 / 自洽扩张方向大规模搜索（74 万模式） | ~30s |
| `exp10_complex_eigenplane.py` | 复特征平面定向发散搜索 | ~60s |
| `exp11_cqlf.py` | 共同二次 Lyapunov SDP（用 `../.venv/bin/python` 运行） | ~5s |
| `exp12_repelling_kkt.py` | 随机 KKT 锥复模调查 | ~5s |
| `exp13_deep_cycles.py` | 加深周期束搜索（深度 14） | ~10s |
| `exp14_targeted_repellent.py` | 定向构造排斥 KKT 实例 | ~60s |
| `exp16_trapping.py` | 捕获区域认证尝试（盒法，失败记录） | ~30s |
| `exp17c_selfcontained.py` | **周期锁频窗口搜索与浮点认证（8 个吸引周期轨道）** | ~90s |
| `exp19b_exact_yt.py` | **反例的精确有理算术认证（Jury 判据，(y,t) 6×6 形式）** | ~2s |
| `exp19_exact_certify.py` | （9×9 形式的认证脚本，慢，已被 exp19b 取代） | 长 |
| `exp18_periodic_points.py` | 可实现周期点 DFS（被 exp17c 超越，可选） | 长 |

建议顺序：test_t_reduction → exp1 → exp9 → exp17c → exp19（核心结果链）。
完整历程见 RESEARCH_LOG.md 与报告 §6。
