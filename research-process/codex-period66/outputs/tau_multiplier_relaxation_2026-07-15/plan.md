# Reproduction Plan

## Goal

在严格 66 周期反例的同一有理 QP 和同一周期初值上，将乘子更新改为

\[
\lambda^{k+1}=\lambda^k-\tau
\bigl(x^{k+1}+y^{k+1}+z^{k+1}-\bar b\bigr),
\qquad 0<\tau\le 1,
\]

并数值检查减小乘子步长是否破坏周期、是否使轨道趋向唯一 KKT 点。

## Selected Source

- `deliverables/strict_66_cycle_minimal/Python/verify_cycle.py`
- `notes/z_projection_identity.md`
- `report/latex/slack_admm_66_cycle_short_paper.tex`

## Minimal Commands To Run

1. 运行现有精确验证器，确认 `tau=1` 的 66 周期基线。
2. 运行新增的完整状态 `(y,z,lambda)` 松弛乘子实验脚本。
3. 运行定向 pytest，检查 `tau=1` 回归、更新恒等式和输出结构。

## Expected Outputs

- `results/tau_sweep.csv`：每个 `tau` 的末端残差、KKT 距离和分类。
- `results/summary.json`：基线、扫描范围和关键观察。
- `figures/tau_convergence.svg`：代表性步长的收敛曲线。
- `logs/run.log`：命令和运行输出。
- `RUN_SUMMARY.md`：数值结论、证据边界与下一步。

## Risks

- 有限迭代内的衰减不能证明全局收敛。
- `tau<1` 时不再有 `lambda=q_-`，必须直接运行完整状态，不能复用四维约化周期公式。
- 很慢的衰减、长暂态和高周期可能被误判；因此同时记录窗口最大值、尾部比率与周期距离。

## Timeout

定向实验总预算不超过 10 分钟；单次轨道最多 200000 步。

## Approval Scope

用户已明确要求“测试一下”，授权本次新增实验脚本、定向测试和本地输出；不修改原反例证书，
不据数值结果宣称一般收敛定理。
