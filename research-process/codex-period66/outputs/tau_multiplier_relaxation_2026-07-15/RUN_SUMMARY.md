# Run Summary

## Status

`numerical_screen_completed_plus_exact_tau_half_fixed_orbit_certificate`

在严格 66 周期反例的同一有理 QP 和同一周期初值上，缩小乘子步长确实可以使轨道转而
趋向唯一 KKT 点。不过修复不是在 `tau=1` 附近立即发生；该固定 QP 的 KKT 点所在 `01`
投影分支在

\[
\tau_c^{\mathrm{loc}}\approx 0.9366061114814712
\]

附近发生局部稳定性变化。

在此数值筛查之后，已对固定有理步长 \(\tau=1/2\) 完成一个更强的精确结论：对原反例
的同一个有理 QP 和同一个周期初值，松弛后的完整状态收敛到唯一 KKT 点。该结论由
`exact_half_convergence_certificate.json` 支撑，不依赖有限精度轨道的渐近判断。

## Source

- 原始精确见证：`deliverables/strict_66_cycle_minimal/Python/verify_cycle.py`
- 松弛实验：`experiments/breakthrough/analyze_relaxed_multiplier_66_cycle.py`
- 定向测试：`tests/test_relaxed_multiplier_66_cycle.py`
- 精确收敛证书：`experiments/breakthrough/certify_relaxed_multiplier_half_convergence.py`
- 精确证书测试：`tests/test_relaxed_multiplier_half_convergence_exact.py`

## Changed Update

原算法使用

\[
\lambda^{k+1}=\lambda^k-r^{k+1}.
\]

实验只把这一行改为

\[
\lambda^{k+1}=\lambda^k-\tau r^{k+1},
\qquad 0<\tau\le1,
\]

其中 `x`、`y`、`z` 三个更新、QP 数据和初值均保持不变。由于 `tau<1` 时不再有
`lambda=q_-`，所有轨道均直接使用完整状态 `(y,z,lambda)` 生成。

## Commands Run

```text
/opt/anaconda3/bin/python deliverables/strict_66_cycle_minimal/Python/verify_cycle.py \
  --steps 66 \
  --output-dir outputs/tau_multiplier_relaxation_2026-07-15/results/baseline_exact

/opt/anaconda3/bin/python -m pytest -q \
  tests/test_relaxed_multiplier_66_cycle.py \
  tests/test_strict_66_cycle_minimal_fixed_decimal.py

/opt/anaconda3/bin/python \
  experiments/breakthrough/analyze_relaxed_multiplier_66_cycle.py \
  --output-dir outputs/tau_multiplier_relaxation_2026-07-15 \
  --max-steps 200000 --tolerance 0.0000000001

/opt/anaconda3/bin/python \
  experiments/breakthrough/analyze_relaxed_multiplier_66_cycle.py \
  --output-dir outputs/tau_multiplier_relaxation_2026-07-15/refinement \
  --taus 0.900,0.905,0.910,0.915,0.920,0.925,0.930,0.935,0.940,0.945,0.950 \
  --max-steps 500000 --tolerance 0.0000000001
```

## Evidence

- `tau=1` 的精确有理基线仍为最小周期 66，全部 132 个投影不等式严格成立。
- 新增更新的回归测试、KKT 固定点测试及局部谱穿越测试合计 `6 passed`。
- `tau=1` 的局部 `01` 分支谱半径为
  `1.000183721838148`，与原反例的近 66 步旋转模态一致。
- 二分局部六维分支矩阵得到
  `tau_c = 0.9366061114814712`：在该值以下谱半径小于 1，在该值以上大于 1。

## Results

| `tau` | 运行结果 | 步数 | 末端到 KKT 距离 | 局部谱半径 |
|---:|---|---:|---:|---:|
| 1.000 | 检出 66 周期 | 132 | 1.2782631859055780 | 1.000183721838148 |
| 0.940 | 500000 步后仍为量级 1 的振荡 | 500000 | 1.2508520558948735 | 1.000010151807035 |
| 0.935 | 很慢地衰减，尚未到停止阈值 | 500000 | 0.1083758473985516 | 0.999995182949034 |
| 0.930 | 很慢地衰减，尚未到停止阈值 | 500000 | 0.0000544875065942 | 0.999980133851693 |
| 0.925 | 很慢地衰减，尚未到停止阈值 | 500000 | 0.0000000290696656 | 0.999965003936374 |
| 0.920 | 收敛到 KKT 停止阈值 | 463822 | 0.0000000000979920 | 0.999949792618138 |
| 0.900 | 收敛到 KKT 停止阈值 | 208225 | 0.0000000000975930 | 0.999888121391214 |
| 0.800 | 收敛到 KKT 停止阈值 | 52844 | 0.0000000000834717 | 0.999558658705756 |
| 0.500 | 收敛到 KKT 停止阈值 | 13795 | 0.0000000000654843 | 0.998302572340647 |

因此，对这个固定反例和固定初值，`tau=0.9`、`0.8`、`0.5` 等都修复了观察到的不收敛；
`tau=0.94` 则没有修复，而且 KKT 点在局部已经不稳定。`tau=0.925`--`0.935` 没有在
500000 步内达到严格停止阈值，但轨迹衰减方向与局部谱半径小于 1 完全一致。

## Figures

- `figures/critical_region_convergence.svg`：`tau=0.90`--`0.94` 的 KKT 距离。
- `figures/local_01_spectral_radius.svg`：局部谱半径穿过 1 的位置。
- `figures/tau_convergence.svg`：第一轮代表步长的全局对比。

## Interpretation

乘子收缩并没有从公式中删除三块交叉项，但它改变了交叉项、残差反馈和旋转模态共同形成的
迭代矩阵。本例中，主导复特征值在 `tau` 降到约 `0.9366061114814712` 以下后进入单位圆，
所以 KKT 点由局部不稳定变成局部稳定。这为后续构造含 `tau` 的 Lyapunov 不等式提供了
明确目标，但当前结果本身不是该不等式的证明。

## Exact Fixed-Orbit Theorem At `tau=1/2`

对同一 QP 和同一周期初值，精确证书在完整状态 \(w=(y,z,\lambda)\) 上构造 `01` 分支矩阵
\(T_{01}\in\mathbb Q^{6\times6}\)，并在 \(\mathbb Q\) 上解出

\[
H=H^\top\succ0,\qquad H-T_{01}^\top H T_{01}=I.
\]

证书进一步构造完全位于真实 `01` 投影区域内的不变椭球，并以真实正部投影精确回放有限
前缀：第 1、2 步为 `00`，第 3 至 208 步为 `01`，第 208 步严格进入该椭球。因而从此以后
分支保持 `01`，Lyapunov 能量几何下降，完整状态收敛到唯一 KKT 点。

该结果只证明固定 QP、固定初值和 \(\tau=1/2\)；它不证明任意初值或整个模型类的收敛。

## Limitations

- 结论只针对当前固定有理 QP 和当前固定初值，不是所有 slack-variable 三块 ADMM 的全局定理。
- `tau_c` 来自双精度局部分支矩阵；若写入正式论文，应进一步用有理特征多项式和 Schur/Jury
  条件将阈值结论升级为精确证书。
- `tau=0.94` 的 500000 步振荡和局部不稳定性不是“存在严格周期”的有理证明。
- 有限步轨迹不能单独证明全局收敛；它只回答导师提出的修复实验是否值得继续。

## Next Option

最有价值的下一步是把 `01` 分支的六维特征多项式写成 `tau` 的有理多项式，用 Schur/Jury
条件精确证明局部稳定区间；之后再尝试含 `tau` 的全局能量不等式，检查原来的交叉项能否在
某个更保守的步长范围内被吸收。
