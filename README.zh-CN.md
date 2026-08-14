# Identity-Slack 三块 ADMM 的精确周期不收敛证书

[English](README.md) | **简体中文**

[![精确证书](https://github.com/ConanXu-math/identity-slack-admm-cycle-certificate/actions/workflows/certificate.yml/badge.svg)](https://github.com/ConanXu-math/identity-slack-admm-cycle-certificate/actions/workflows/certificate.yml)

本仓库对应论文 **“A Counterexample to the Convergence of Three-Block ADMM
with an Identity Third Constraint Block”**。仓库为两个固定凸二次规划实例提供
可精确重放的证据：虽然问题具有唯一 KKT 点，未经修正的直接三块 ADMM
仍可产生有界、非 KKT 的周期序列。

## 从这里开始

| 你的目的 | 建议入口 |
| --- | --- |
| 阅读数学论证 | [编译后的论文](paper/slack_admm_arxiv.pdf) |
| 复现两个反例 | [五分钟验证](#五分钟验证) |
| 查看精确机器证书 | [`certificates/`](certificates/) |
| 了解每个检查器究竟证明什么 | [复现与证书契约](docs/REPRODUCIBILITY.md) |
| 追踪 Codex 与 Kimi 的发现过程 | [研究阶段索引](research-process/INDEX.md) |
| 查看时间、token 与 agent 统计 | [计算过程说明](provenance/README.md) |
| 运行独立 MATLAB 检查 | [MATLAB 说明](matlab/README.md) |

根目录中的证书与检查器是正式验收层。`research-process/` 是“这些结果如何被
找到”的历史证据，不构成第二套验收标准。

## 已认证结果

| 证书 ID | 固定实例 | 精确结论 | 主要证据 |
| --- | --- | --- | --- |
| `identity_slack_p66_short_v1` | `m = 2`，`A = B = I_2`，`beta = 1` | 一个指定初始点产生最小周期 66 的有界非 KKT 轨道 | 两种独立 Python 状态表示与一套 MATLAB 实现 |
| `identity_slack_p23_rational_v1` | `m = 3`，有理 QP 数据，`beta = 1` | 一组开集中的降维初始点按相位收敛到最小周期 23 的非 KKT 轨道 | 精确有理数重放与 Lyapunov 证书 |

### 周期 66

- 投影词为 `(00)^2(01)^64`；
- 精确闭合，最小周期为 `66`；
- `132/132` 个严格投影条件全部通过；
- 最小符号裕量为
  `0.0037105246944352910173... > 1/1000`；
- 轨道有界且非 KKT，而该 QP 的 KKT 点唯一；
- 证书针对一个特意构造的指定初始点，不声称该周期具有吸引性、序列无界发散，
  也不否定带校正步骤或附加条件的 ADMM 变体。

### 周期 23

- 所有原始 QP 系数都是最简分数，分子绝对值和分母均不超过 `100`；
- 冻结证书包含完整的精确相位零状态 `(x^0,y^0,z^0,lambda^0)`；
- 精确闭合，最小周期为 `23`；
- `69/69` 个投影条件均严格成立，最小裕量大于 `1/250`；
- 有理矩阵 `P` 精确满足
  `P - M_per^T P M_per > 0`；
- 在规范降维状态 `(y,t)` 中，椭球 `e^T P e < 1/4000` 是返回不变集，
  其中每个初始点都按相位收敛到周期 23 序列；
- 这是一个固定 QP 的初始点邻域，不是 QP 数据扰动结论，也不是全局吸引定理。

Kimi Code K3 路线最初得到的是周期 23 的精确 dyadic 重放以及基于精确 Jury
判据的局部吸引证书。上面的小分母有理实例和显式不变椭球属于后续发布强化；详见
[`路线核验记录`](provenance/routes/kimi-period23/run_attestation.json)。

### 周期 66 QP 的乘子松弛

精确松弛证书分别证明：

1. 对所有 `tau in [49/100, 51/100]`，严格 KKT 分支共享一个有理 Lyapunov
   矩阵；
2. 对所有 `tau in [1/2 - 10^-10, 1/2 + 10^-10]`，原周期初值保持严格分支
   232 步后进入不变椭球；
3. 严格 KKT 分支存在唯一 Schur 边界，并满足
   `0.9366061114 < tau_c < 0.9366061115`。

这些是局部或固定初始点结论，不证明任意初始点的全局收敛。

## 五分钟验证

冻结 Python 环境为 3.13.5，依赖 SymPy 1.13.3、NumPy 2.1.3 和
pytest 8.3.4。

```bash
git clone https://github.com/ConanXu-math/identity-slack-admm-cycle-certificate.git
cd identity-slack-admm-cycle-certificate
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python python/verify_all.py
python python/verify_research_process_archive.py
```

证书命令应以以下结果结束：

```json
{"checks": [{"name": "period66", "returncode": 0, "status": "passed"}, {"name": "period23", "returncode": 0, "status": "passed"}], "valid": true}
```

与 GitHub Actions 一致的完整发布检查为：

```bash
python python/verify_all.py
python python/verify_research_process_archive.py
python python/export_orbit_66.py
python python/certify_relaxed_multiplier_interval_theory.py
python python/verify_universal_step_obstruction.py --check
python -m pytest -q python/tests/test_relaxed_multiplier_interval_theory.py
python -m unittest discover -s tests -p "test_*.py"
python python/verify_matlab_certificate.py
git diff --exit-code -- certificates/
```

最后一条也是验收条件：重新生成后，仓库中冻结的证书必须逐字节保持不变。

## 证据如何组织

| 层级 | 作用 | 权威入口 |
| --- | --- | --- |
| 精确验收 | 重建固定 QP 并检查全部有限证明义务 | [`python/verify_all.py`](python/verify_all.py) |
| 冻结数据 | 规范输入、精确轨道、判定结果、哈希和 Lyapunov 数据 | [`certificates/`](certificates/) |
| 实现交叉检查 | 周期 66 的 signed-state、full-state 与 MATLAB 独立实现 | [`python/README.md`](python/README.md)、[`matlab/README.md`](matlab/README.md) |
| 研究过程 | 精选理论、实验、失败路线、状态文件和内部复核 | [`research-process/INDEX.md`](research-process/INDEX.md) |
| 路线统计 | Codex/Kimi 比较的统计定义与适用边界 | [`provenance/README.md`](provenance/README.md) |
| 持续集成 | 在干净环境中重建证书并检查产物稳定性 | [精确证书 workflow](.github/workflows/certificate.yml) |

多套实现的一致性属于内部复现交叉检查，不等于外部同行评审。

## 如何阅读研究过程

不要按文件夹顺序盲目浏览，建议从
[`research-process/INDEX.md`](research-process/INDEX.md) 进入：

- **Codex / 周期 66：**先看持续任务状态和代数降维，再沿 Stage 43–46 阅读
  “障碍识别—数值发现—有理化—精确重放—精度审计”的路径；
- **Kimi Code K3 / 周期 23：**先看 `START_GOAL.txt` 和 `RESEARCH_LOG.md`，
  再看撤回路线、定向不稳定性实验、周期锁定与最终精确证书。

阅读时应区分证据标签：

- `numerical_screen` 与 `proof_attempt` 只是探索；
- `withdrawn` 表示该路线已被否定；
- `theorem` 与 `exact_certificate` 只在其明示范围内成立；
- `review` 表示内部检查，不是外部同行评审。

仓库有意排除了原始聊天、凭据、私人配置、本机绝对路径、缓存与重复的大批量输出。
保留的 168 个过程文件由
[`research-process/manifest.json`](research-process/manifest.json) 记录哈希，并由
CI 检查。

## MATLAB 复现

MATLAB 检查器只覆盖周期 66 实例，需要 MATLAB R2025a、Symbolic Math
Toolbox 和有效许可证：

```matlab
addpath("matlab")
result = verify_exact_cycle_matlab();
assert(result.valid)
```

随后比较 MATLAB JSON 与冻结 Python 字段：

```bash
python python/verify_matlab_certificate.py
```

基于类的测试与需许可证的 GitHub Actions 说明见
[`matlab/README.md`](matlab/README.md)。

## 仓库结构

```text
.
├── python/             Python 精确检查器与比较入口
├── matlab/             独立的周期 66 MATLAB 检查器与测试
├── certificates/       冻结输入与机器可读证书
├── research-process/   精选 Codex 与 Kimi 发现过程
├── provenance/         比较范围、统计定义与证据边界
├── docs/               详细复现与证书契约
├── paper/              编译后的论文 PDF
└── .github/            CI 与仓库规则
```

脚本级说明见 [`python/README.md`](python/README.md)；精确谓词、产物含义、运行
环境与发布检查见 [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)。

## Codex–Kimi 比较边界

两条路线分别得到了针对同一拟议收敛原则的精确反例，但它们没有求解同一个 QP，
也未对计算量、工具、遥测、停止规则或人工干预进行匹配。因此，该比较只能描述
两次已实现的研究过程及其共同证据终点，不能用于因果性地排序模型速度、成本或能力。

## 发布与引用状态

仓库目前为私人版本，尚未提供公开软件许可证。正式公开前，需要确定最终作者与
添加 `CITATION.cff`，选择许可证，建立不可变 release tag 与归档，取得 DOI，并确保
论文和代码可用性声明共同指向该版本。

仓库维护者：[ConanXu-math](https://github.com/ConanXu-math)。
