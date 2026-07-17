# Identity-Slack 三块 ADMM 的精确周期证书

> **当前状态：私人、投稿前版本。** 数学命题和程序接口已冻结用于内部核查，
> 但公开归档 DOI、最终作者列表、引用信息和开源许可证尚未确定。

本仓库是论文 **“Direct Three-Block ADMM Can Cycle with an Identity Slack
Block”** 的独立精确证书包。它验证一个显式有理实例：原始、未经修正的直接
三块 ADMM 存在一个有界、严格可容许、非 KKT 的最小周期 66 轨道，而对应优化
问题仍有唯一 KKT 点。

## 证书结论

- 冻结实例：`identity_slack_p66_short_v1`
- 模型：`A = B = I_2`，第三块为非负 identity slack，`beta = 1`
- mask word：`(00)^2(01)^64`
- 最小周期：`66`
- 严格符号检查：`132/132` 通过
- 最小符号裕量：`0.0037105246944352910173... > 1/1000`
- 结论边界：证明有界周期不收敛，不声称无界发散，也不否定带附加条件或修正
  步骤的 ADMM 收敛定理

## 两层独立实现

1. `signed_cycle_certificate.py`：使用四维 signed state `s = (y,q)`；
2. `strict_cycle_certificate.py`：不调用上一实现，直接在六维 unreduced
   essential state `(y,z,lambda)` 上由原始 ADMM 更新重建仿射分支。

`verify_certificate_pair.py` 会重新生成两份 JSON，并逐项比较实例、初值、完整
轨道、mask word、KKT 点、最小裕量和规范化哈希。两套程序的吻合是内部软件
交叉检查，不等同于第二份数学证明或外部同行评审。

## 一键复现

冻结环境为 Python 3.13.5 和 SymPy 1.13.3：

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python verify_certificate_pair.py
```

成功输出必须包含：

```json
{"instance_id": "identity_slack_p66_short_v1", "valid": true}
```

如需检查生成文件与仓库冻结版本完全一致：

```bash
python verify_certificate_pair.py
git diff --exit-code -- certificate_raw.json certificate_signed.json instance_manifest.json
```

GitHub Actions 会在每次 push 和 pull request 上执行同一验证流程。

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `strict_cycle_certificate.py` | 六维原变量 Markov 状态的精确检查器 |
| `signed_cycle_certificate.py` | 四维 signed-state 精确检查器 |
| `verify_certificate_pair.py` | 重新生成、比较并哈希两套证书 |
| `certificate_raw.json` | 六维检查器的稳定机器可读输出 |
| `certificate_signed.json` | signed-state 检查器的稳定机器可读输出 |
| `instance_manifest.json` | 公共结论、运行环境、比较结果和文件哈希 |
| `REPRODUCIBILITY.md` | 证明义务和发布契约 |

## 公开发布前

当前私人审阅标签为 `v0.1.0-private`。正式公开前还需：

1. 建立永久归档并取得 DOI；
2. 确认最终作者和引用信息；
3. 确定并加入软件许可证；
4. 关联公开论文版本；
5. 确保公开 release tag、归档代码和论文记录指向同一 commit。

在完成这些事项前，本仓库不作为公开引用记录，也不授予公开使用许可证。
