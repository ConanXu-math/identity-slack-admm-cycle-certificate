# Identity-Slack 三块 ADMM 的精确周期不收敛证书

> **当前状态：私人、投稿前版本。** 数学命题和程序接口已冻结用于内部核查，
> 但公开归档 DOI、最终作者列表、引用信息和开源许可证尚未确定。

本仓库是论文 **“Direct Three-Block ADMM Can Cycle with an Identity Slack
Block”** 的精确证书包。它验证两个显式实例：原始、未经修正的直接三块 ADMM
存在有界、严格可容许、非 KKT 的周期序列，而对应优化问题仍有唯一 KKT 点。

仓库分为两层：根目录保存冻结实例、精确检查器和机器证书；
`research-process/` 保存两条 agent 路线中重要的研究状态、理论推导、失败路线、
数值实验、结果文件和复核材料，用于回答“结果是怎样找到的”。

## 证书结论

| 证书 ID | 维数 | 严格结论 | 验证方式 |
| --- | ---: | --- | --- |
| `identity_slack_p66_short_v1` | 2 | 最小周期 66 的有界非 KKT 序列 | reduced Python、full-state Python、MATLAB |
| `identity_slack_p23_dyadic_v1` | 3 | canonical `(y,t)` 状态中局部吸引的最小周期 23 非 KKT 轨道 | 精确 dyadic replay 与 Jury 判据 |

### Period 66

- `A = B = I_2`，第三块为非负 identity slack，`beta = 1`；
- mask word 为 `(00)^2(01)^64`；
- `132/132` 个严格符号条件全部通过；
- 最小符号裕量为 `0.0037105246944352910173... > 1/1000`；
- 该严格 primitive word 及周期 66 轨道在有理参数的一个开邻域内保持；
- 只证明有界周期不收敛，不声称无界发散。

### Period 23

- 三维强凸二次实例，第三块为非负 identity slack，`beta = 1`；
- binary64 数据逐项解释为精确 dyadic rational；
- 最小周期为 `23`，共 `69` 个投影输入严格远离零，最小裕量大于
  `7/1000`；
- 精确 23 步返回矩阵通过 Jury 稳定性判据，因此周期轨道在 canonical
  `(y,t)` 状态中局部吸引；上述符号裕量不是显式吸引域半径，也不是参数区间；
- 论文中的显式有理不变邻域是在 Kimi 终局运行之后补充的 companion
  certificate；它不能混写成 Kimi 原始终局产物，本证书包也暂未收录。

### Period-66 实例的乘子松弛

在同一个有理 QP 上，把乘子步长改为 `tau`，精确证书证明：

- 对所有 `tau in [49/100, 51/100]`，严格 KKT 分支共享同一个有理 Lyapunov
  矩阵；
- 对所有 `tau in [1/2 - 10^-10, 1/2 + 10^-10]`，原周期初值按严格分支运行
  232 步后进入不变 Lyapunov 椭球；
- 严格 KKT 分支在 `(0,1)` 内有唯一 Schur 边界，并满足
  `0.9366061114 < tau_c < 0.9366061115`。

这些结论不等于任意初值的全局收敛，也不是对所有 identity-slack 问题的统一
收敛定理。

> **比较边界：** `provenance/` 中的 Codex 与 Kimi Code K3 记录是两条已实现
> 科研路线的描述性、终点对齐比较，不是计算量、工具、遥测或人工干预受控的
> 模型能力 benchmark。

## 验证架构

### Period-66 的三套实现与交叉检查

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

`python/export_orbit_66.py` 将 66 个循环相位完整写入
`certificates/orbit_66.json`。该文件是精确数据导出，不是额外证明。

`python/certify_relaxed_multiplier_interval_theory.py` 从原始 ADMM 更新重建含
`tau` 的六维分支映射，并用精确代数验证 Lyapunov 区间、有限步捕获和 Schur
边界。

### Period-23 精确检查

`python/verify_period23_certificate.py` 读取冻结 NPZ，将每个 binary64 数解释为
精确 dyadic rational，并检查问题合法性、唯一 KKT 点及其原始最优性条件、严格
投影符号、23 步精确闭合、最小周期、与 KKT 点分离以及精确 Jury 稳定性。它
确定性生成：

- `certificates/period23_certificate.json`；
- `certificates/period23_instance_manifest.json`。

manifest 同时记录数组 shape、dtype、binary64 bit pattern、精确 dyadic 数值以及
输入和 verifier 的 SHA-256；运行时间不进入冻结证书。

## 一键复现

冻结环境为 Python 3.13.5、SymPy 1.13.3 和 NumPy 2.1.3：

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python python/verify_all.py
python python/export_orbit_66.py
python python/certify_relaxed_multiplier_interval_theory.py
python -m pytest -q python/tests/test_relaxed_multiplier_interval_theory.py
```

成功输出必须包含：

```json
{"checks": [{"name": "period66", "returncode": 0, "status": "passed"}, {"name": "period23", "returncode": 0, "status": "passed"}], "valid": true}
```

如需检查生成文件与仓库冻结版本完全一致：

```bash
python python/verify_all.py
python python/export_orbit_66.py
python python/certify_relaxed_multiplier_interval_theory.py
python -m pytest -q python/tests/test_relaxed_multiplier_interval_theory.py
python -m unittest discover -s tests -p "test_*.py"
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
├── certificates/  # 冻结输入与机器可读证书
├── provenance/    # 路线级统计与证据边界
├── research-process/ # 精选的 agent 状态、理论、实验、结果和复核档案
├── docs/          # 复现与发布文档
├── paper/         # 编译后的论文 PDF
└── .github/       # 持续集成与仓库规则
```

| 文件 | 作用 |
| --- | --- |
| `python/` | Python 精确检查器与比较入口 |
| `python/strict_cycle_certificate.py` | 六维原变量 Markov 状态的精确检查器 |
| `python/signed_cycle_certificate.py` | 四维 signed-state 精确检查器 |
| `python/verify_certificate_pair.py` | 重新生成、比较并哈希两套 Python 证书 |
| `python/verify_period23_certificate.py` | Period-23 精确 dyadic replay 与 Jury 检查 |
| `python/verify_all.py` | 顺序运行两条证书路径并透传失败 |
| `python/export_orbit_66.py` | 导出全部 66 个精确循环相位 |
| `python/certify_relaxed_multiplier_interval_theory.py` | 验证局部乘子松弛区间与 Schur 边界 |
| `python/tests/test_relaxed_multiplier_interval_theory.py` | 松弛证书的直接重放与代数回归测试 |
| `matlab/verify_exact_cycle_matlab.m` | 六维状态的独立 MATLAB 精确检查器 |
| `matlab/tests/VerifyExactCycleMatlabTest.m` | MATLAB class-based 回归测试 |
| `python/verify_matlab_certificate.py` | 比较 MATLAB 与 Python 证书公共字段 |
| `certificates/` | 稳定输入与机器可读证书 |
| `provenance/` | 描述性路线记录，不构成受控 benchmark |
| `research-process/` | Codex/Kimi 过程性研究档案及哈希清单 |
| `paper/slack_admm_arxiv.pdf` | 编译后的论文；不包含排版工作文件 |
| `docs/REPRODUCIBILITY.md` | 证明义务和发布契约 |

## 公开发布前

当前私人审阅版本为 `v0.3.0-private`。正式公开前还需：

1. 建立永久归档并取得 DOI；
2. 确认最终作者和引用信息；
3. 确定并加入软件许可证；
4. 关联公开论文版本；
5. 确保公开 release tag、归档代码和论文记录指向同一 commit。

在完成这些事项前，本仓库不作为公开引用记录，也不授予公开使用许可证。
