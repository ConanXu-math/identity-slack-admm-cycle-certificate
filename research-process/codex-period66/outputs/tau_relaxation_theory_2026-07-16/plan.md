# Tau-Relaxation Theory Plan

状态：`completed_and_accepted_by_internal_verifier_style_review`

## 目标

把当前 `tau=1/2` 的固定实例证书整理为一条可审查的理论链：

1. 严格活动分支上的局部收敛定理；
2. 共同 Lyapunov 矩阵给出的乘子步长区间定理；
3. 有限严格前缀进入不变椭球的捕获定理；
4. 对严格 66 周期见证的同一初值，认证一个非退化有理 `tau` 区间；
5. 用精确特征多项式与 Schur/Jury 条件认证局部稳定边界的有理夹逼。

## 执行入口

- 精确数据：`deliverables/strict_66_cycle_minimal/Python/verify_cycle.py`
- 已有半步证书：`experiments/breakthrough/certify_relaxed_multiplier_half_convergence.py`
- 新证书：`experiments/breakthrough/certify_relaxed_multiplier_interval_theory.py`
- 新测试：`tests/test_relaxed_multiplier_interval_theory.py`

## 证据规则

- 浮点扫描只用于定位区间和边界；
- 正式区间只使用有理端点、精确矩阵恒等式、Sylvester 判据、严格投影不等式与精确多项式符号；
- 局部 Schur 稳定不自动推出原周期初值收敛，必须另行关闭有限前缀进入义务；
- 不声称任意初值或整个 identity-slack 模型类全局收敛。

## 预算与输出

- 单次精确运行目标：小于 10 分钟；
- 日志：`logs/run.log`；
- 机器证书：`results/certificate.json`；
- 总结：`RUN_SUMMARY.md`；
- proof review：`proof_reviews/relaxed_multiplier_interval_theory/`。
