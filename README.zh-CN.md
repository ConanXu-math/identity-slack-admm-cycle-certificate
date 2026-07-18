# Identity-Slack 三块 ADMM 的精确周期证书

> **当前状态：私人、投稿前版本。** 数学命题和程序接口已冻结用于内部核查，
> 但公开归档 DOI、最终作者列表、引用信息和开源许可证尚未确定。

本仓库是论文 **“Direct Three-Block ADMM Can Cycle with an Identity Slack
Block”** 的精确证书包。它验证一个显式有理实例：原始、未经修正的直接
三块 ADMM 存在一个有界、严格可容许、非 KKT 的最小周期 66 轨道，而对应优化
问题仍有唯一 KKT 点。论文还证明该严格 primitive 周期轨道在参数开邻域内保持，
并给出一组范围明确的精确证书，说明乘子松弛在 `tau = 1/2` 附近如何稳定这一
冻结实例。

## 证书结论

- 冻结实例：`identity_slack_p66_short_v1`
- 模型：`A = B = I_2`，第三块为非负 identity slack，`beta = 1`
- mask word：`(00)^2(01)^64`
- 最小周期：`66`
- 严格符号检查：`132/132` 通过
- 最小符号裕量：`0.0037105246944352910173... > 1/1000`
- 严格 primitive word 及其周期 66 轨道在有理参数的一个开邻域内保持
- 结论边界：证明有界周期不收敛，不声称无界发散，也不否定所有修正 ADMM

## 乘子松弛的精确结论

在同一个有理 QP 上，把乘子步长从 `1` 改成 `tau`，证书证明：

- 对所有 `tau in [49/100, 51/100]`，严格 KKT 分支共享同一个有理 Lyapunov
  矩阵；
- 对所有 `tau in [1/2 - 10^-10, 1/2 + 10^-10]`，原周期初值按严格分支运行
  232 步后进入不变 Lyapunov 椭球；
- 严格 KKT 分支在 `(0,1)` 内有唯一 Schur 边界，并满足
  `0.9366061114 < tau_c < 0.9366061115`。

这些结论不等于任意初值的全局收敛，也不是对所有 identity-slack 问题的统一
收敛定理。

## 三套实现与交叉检查

1. `python/signed_cycle_certificate.py`：使用四维 signed state `s = (y,q)`；
2. `python/strict_cycle_certificate.py`：不调用上一实现，直接在六维 unreduced
   essential state `(y,z,lambda)` 上由原始 ADMM 更新重建仿射分支。

`python/verify_certificate_pair.py` 会重新生成两份 JSON，并逐项比较实例、初值、完整
轨道、mask word、KKT 点、最小裕量和规范化哈希。两套程序的吻合是内部软件
交叉检查，不等同于第二份数学证明或外部同行评审。

仓库还包含第三套、独立编写的 MATLAB 实现
`matlab/verify_exact_cycle_matlab.m`。它使用 MATLAB R2025a 和 Symbolic Math
Toolbox，在六维 `(y,z,lambda)` 状态上重新解精确周期方程，再用真实逐坐标正部
投影重跑全部 66 步；它不调用 Python。`python/verify_matlab_certificate.py` 只负责比较
MATLAB 输出与冻结 Python 证书的公共字段。

`python/certify_relaxed_multiplier_interval_theory.py` 从四个原始 ADMM 更新重新
构造含 `tau` 的六维分支映射，并通过精确 Sylvester 判据、有理有限前缀包络、
Schur 递推和 Sturm 根计数完成上述松弛证书。定向测试还会直接重放捕获区间的
两个端点。

`python/export_orbit_66.py` 把全部 66 个循环相位写入
`certificates/orbit_66.json`。它是完整数据导出，不是额外证明或独立实现。

## 一键复现

冻结环境为 Python 3.13.5、SymPy 1.13.3 和 pytest 8.3.4：

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python python/verify_certificate_pair.py
python python/export_orbit_66.py
python python/certify_relaxed_multiplier_interval_theory.py
python -m pytest -q python/tests/test_relaxed_multiplier_interval_theory.py
```

成功输出必须包含：

```json
{"instance_id": "identity_slack_p66_short_v1", "valid": true}
```

如需检查生成文件与仓库冻结版本完全一致：

```bash
python python/verify_certificate_pair.py
python python/verify_matlab_certificate.py
git diff --exit-code -- certificates/
```

GitHub Actions 会在每次 push 和 pull request 上执行同一验证流程。

### MATLAB 复现

需要 MATLAB R2025a、Symbolic Math Toolbox 和有效许可证。在仓库根目录运行：

```matlab
addpath("matlab")
result = verify_exact_cycle_matlab();
assert(result.valid)
```

该命令生成 `certificates/certificate_matlab.json`。随后运行跨语言精确比较：

```bash
python python/verify_matlab_certificate.py
```

MATLAB 单元测试命令为：

```matlab
results = runtests("matlab/tests/VerifyExactCycleMatlabTest.m");
assert(all([results.Passed]))
```

由于仓库目前是私有项目，MathWorks 的 GitHub Actions 运行需要 batch licensing
token。先把 token 保存为仓库 secret `MLM_LICENSE_TOKEN`，再手动运行
`MATLAB exact certificate` workflow。仓库公开后可把该 workflow 改为每次 push
自动运行。

## 文件说明

```text
.
├── python/        # Python 精确实现与比较入口
├── matlab/        # MATLAB 实现、测试和说明
├── certificates/  # 冻结证书、摘要与完整轨道数据
├── docs/          # 复现与发布文档
├── paper/         # 仅保留编译后的论文 PDF
└── .github/       # 持续集成与仓库规则
```

| 文件 | 作用 |
| --- | --- |
| `python/` | Python 精确检查器与比较入口 |
| `python/strict_cycle_certificate.py` | 六维原变量 Markov 状态的精确检查器 |
| `python/signed_cycle_certificate.py` | 四维 signed-state 精确检查器 |
| `python/verify_certificate_pair.py` | 重新生成、比较并哈希两套 Python 证书 |
| `python/export_orbit_66.py` | 导出 66 个相位的完整精确轨道数据 |
| `python/certify_relaxed_multiplier_interval_theory.py` | 验证松弛局部区间与 Schur 边界 |
| `python/tests/test_relaxed_multiplier_interval_theory.py` | 松弛证书的直接重放与代数回归测试 |
| `matlab/verify_exact_cycle_matlab.m` | 六维状态的独立 MATLAB 精确检查器 |
| `matlab/tests/VerifyExactCycleMatlabTest.m` | MATLAB class-based 回归测试 |
| `python/verify_matlab_certificate.py` | 比较 MATLAB 与 Python 证书公共字段 |
| `certificates/` | 稳定的机器可读证书与完整轨道数据 |
| `paper/slack_admm_arxiv.pdf` | 编译后的论文；本仓库不分发排版源码 |
| `docs/REPRODUCIBILITY.md` | 证明义务和发布契约 |

## 公开发布前

当前私人审阅版本为 `v0.3.0-private`。正式公开前还需：

1. 建立永久归档并取得 DOI；
2. 确认最终作者和引用信息；
3. 确定并加入软件许可证；
4. 关联公开论文版本；
5. 确保公开 release tag、归档代码和论文记录指向同一 commit。

在完成这些事项前，本仓库不作为公开引用记录，也不授予公开使用许可证。
