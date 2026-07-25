# VI/PPA 文献版图与严格 66 周期的先例审计

状态：`prior_art_audit_completed_with_search_limits`
日期：2026-07-14

## 1. 结论先行

截至本次对本地全文库、主要原始论文、OpenAlex 前向引用链和公开网页检索的审计，结论分三层：

1. **“一般 direct 三块 ADMM 不一定收敛”不是新结果。** Chen--He--Ye--Yuan 已给出一般系数矩阵下的发散反例，且其第 4.1 节包含三个目标都强凸而仍发散的例子。
2. **“VI/PPA 可以产生很多收敛算法”是正确的。** 但这些结果大多证明两块 ADMM、prediction--correction、Gaussian back substitution、proximal/metric projection 或小 dual step 的算法；它们不等于原始 slack-last 的 \(x\to y\to z\to\lambda\) 迭代。
3. **当前未发现与本项目精确同型的已发表结果：**

   > 系数块为 \([I_2,I_2,I_2]\)、第三块为非负正象限 slack、按 slack-last 顺序更新、前两块为纯强凸有理二次函数，并具有严格可达且有界的精确有限周期。

因此，当前最稳妥的学术定位是：

> 据本次检索所知，本文给出了 identity-slack 子类中首个严格、有界、精确有限周期型的 direct-ADMM 反例；一般多块 ADMM 的非收敛和强凸反例本身均为已有结果。

这是一项强但并非绝对优先权证明的检索结论。投稿前仍应做 MathSciNet、Scopus、Web of Science 补检并请外部同行复核。

## 2. 当前结果的精确算法指纹

任何先例只有同时匹配下表，才构成真正的优先权冲突。

| 维度 | 当前结果 |
| --- | --- |
| 问题 | \(\min \frac12x^\top Q_1x+\frac12y^\top Q_2y\)，\(x+y+z=\bar b\)，\(z\ge0\) |
| 系数块 | \(A=B=I_2\)，slack 系数也是 \(I_2\) |
| 块顺序 | \(x\to y\to z\to\lambda\)，slack 最后更新 |
| 算法修改 | 无近端项、无回代、无 correction、无 relaxation |
| 罚参数 | \(\beta=1\) |
| 目标 | \(Q_1,Q_2\in\mathbb Q^{2\times2}\) 且严格正定；精确平移后无一次项 |
| 解结构 | 唯一 KKT 点 |
| 非收敛方式 | 有界、非 KKT、最小周期 \(66\) |
| itinerary | \(00,00,01^{64}\)；全部 132 个符号不等式严格 |
| 证明强度 | 有理闭合；统一余量 \(>1/1000\)；signed-state 与 raw 6D 两套实现交叉检查 |

“一般三块”“目标强凸”或“出现数值振荡”只匹配其中少数维度，不能替代这个精确指纹。

## 3. 最接近的同模型先例：He--Xu--Yuan

[He, Xu, Yuan (2023)](https://doi.org/10.1016/bs.hna.2022.08.002) 从两块线性不等式约束问题出发，引入 \(z\in\mathbb R_+^m\)，并在式 (1.7) 明确写出按 \(x\to y\to z\to\lambda\) 更新的 EADMM。其不等式方向采用 \(Ax+By\ge b\)、等式写作 \(Ax+By-z=b\)；与本文的 \(Ax+By\le b\)、\(Ax+By+z=b\) 只差整体符号约定。

该文指出：这个 direct EADMM 在无附加限制时没有收敛保证，随后转向 prediction--correction；但文中没有给出 \([A,B,I]\) 与正象限投影子类内的严格反例。这篇文献一方面确认当前研究对象是已有文献明确写出的自然算法，另一方面留下了 slack-specific counterexample 的缺口。

本次还筛查了该书章在 OpenAlex 中列出的 10 篇前向引用。相关论文研究 PDMM、prox-Lagrangian、算法设计框架和 prediction--correction proximal method；未发现 direct EADMM 的有限周期反例。

## 4. 已知反例与条件收敛边界

### 4.1 一般 direct 三块 ADMM 发散

[Chen, He, Ye, Yuan (2016)](https://doi.org/10.1007/s10107-014-0826-5) 对一般三列系数矩阵构造线性递推并证明谱半径大于 \(1\)。其第 4.1 节进一步在三个目标都强凸且 \(\beta=1\) 时得到谱半径约 \(1.0087\)。所以以下两句话不能作为本文的新颖性声明：

- “三块 ADMM 可能不收敛”；
- “即使各块强凸也可能不收敛”。

该反例与当前结果仍有四个本质差别：系数不是 \([I,I,I]\)；没有正象限 slack；没有 active-set switching；其非收敛由不稳定谱驱动，而不是严格有界有限周期。

### 4.2 强凸块与罚参数限制

[Cai, Han, Yuan (2017)](https://doi.org/10.1007/s10589-016-9860-y) 的 direct 三块收敛定理要求第三函数强凸、\(A_2,A_3\) 满列秩，并且

\[
0<\beta<\frac{6\mu_3}{13\lVert A_3^\top A_3\rVert}.
\]

本文 slack-last 的第三函数是 \(\iota_{\mathbb R_+^2}\)，既不光滑也不强凸，因此该定理不适用。前两块 \(Q_1,Q_2\succ0\) 不能替代“最后一块强凸”这一有顺序的信息。

[Tao, Yuan (2018)](https://doi.org/10.1007/s10444-017-9560-x) 把 \(m-2\) 个强凸块和受限罚参数的结论推广到多块，同时说明移除相应限制后仍可能发散。

### 4.3 slack-first 的正向结果与块顺序

[Lin, Ma, Zhang (2015)](https://doi.org/10.1137/140971178) 的 Remark 3.6 明确讨论不等式约束：引入非负 slack \(x_0\) 后先更新 \(x_0\)，再依次更新原变量。若原目标都强凸、最后一个原变量的梯度 Lipschitz、相应矩阵满行秩，并且罚参数满足式 (2.18) 的小参数限制，则 slack-first ADMM 全局线性收敛。

这不是当前 slack-last 算法。对本文具体 Hessian，

\[
\lambda_{\min}(Q_1)=\frac{2604621}{22395379}\approx0.11630,\qquad
\lambda_{\min}(Q_2)=\frac{116499}{99883501}\approx0.00116635.
\]

把 slack 放在第一块后，该文的显示充分条件至多允许

\[
\beta<\min\{\lambda_{\min}(Q_1),\lambda_{\min}(Q_2)\}\approx0.00116635,
\]

而本文周期使用 \(\beta=1\)。所以该定理既没有覆盖同一更新顺序，也没有覆盖同一参数点。block order 是算法动力学的一部分，不是纯记号重排。

其他正向边界也保留各自的附加条件：[Lin, Ma, Zhang (2018)](https://doi.org/10.1007/s10915-017-0612-7) 的 unmodified 三块定理要求第三函数光滑强凸；[Hong, Luo (2017)](https://doi.org/10.1007/s10107-016-1034-2) 使用误差界并要求足够小的 dual step。二者均不直接覆盖本文参数点。

## 5. 为什么 VI/PPA 文献很多，却不推出原 direct 算法收敛

### 5.1 两块 ADMM 的 PPA 根基

[Eckstein--Bertsekas (1992)](https://doi.org/10.1007/BF01581204) 把 Douglas--Rachford splitting 与 proximal point algorithm 联系起来，奠定两块 ADMM 的最大单调算子解释。这个框架的关键对象是两算子 resolvent/splitting。直接插入第三个 Gauss--Seidel 块后，所得复合映射一般不再自动是同一个 PPA resolvent。

### 5.2 prediction--correction 的共同模板

[He--Yuan (2018)](https://doi.org/10.1007/s10589-018-9994-1) 把 direct 三块 sweep 当作 predictor，再显式校正 predictor。其抽象充分条件寻找 \(H\succ0\)，使

\[
HM=Q,\qquad G=Q^\top+Q-M^\top HM\succ0,
\]

由此得到 \(H\)-范数收缩。类似路线还包括：

- [He--Tao--Yuan (2012)](https://doi.org/10.1137/110822347) 的 Gaussian back substitution；
- [Chang--Liu--Zhao--Li (2018)](https://doi.org/10.1016/j.cam.2017.11.033) 的 prediction--correction-based ADMM；
- He--Xu--Yuan 对等式与不等式问题的统一 VI correction framework。

这些论文的结论是真正的收敛定理，但收敛的是 corrected iterate，而不是把 predictor 原样作为下一步的 direct EADMM。

仓库内对 direct slack specialization 的独立推导还给出一个具体障碍：若 \(C=I\)，则对

\[
\Delta v=(\Delta y,B\Delta y,0)
\]

有

\[
\Delta v^\top G_{\rm slack}\Delta v
=-\beta\lVert B\Delta y\rVert^2<0.
\]

这只说明标准 VI/PPA 收缩门在原 direct map 上失败；它本身不是反例。本文的 66 周期才把“证明路线失败”提升为“全称收敛命题为假”。

## 6. active-set、slack 与近期论文

[Ghadimi--Teixeira--Shames--Johansson (2015)](https://doi.org/10.1109/TAC.2014.2354892) 对标准两块 ADMM 求解 QP 的 active-set 线性时变表示进行了系统分析。这是本文 signed-state/PWA 方法的重要技术先例；但其算法仍是两块 splitting，不包含 direct 三块的非平凡有限周期。

[Lew--Greiff--Subosits--Plancher (2026)](https://arxiv.org/abs/2511.08451) 是本次检索中最新且标题最接近的 slack-ADMM 论文。阅读全文可见，它顺序更新 \(x\) 与联合块 \((z,\xi)\)，并消去显式 slack；本质是标准两块 ADMM 的另一种 splitting。它与分别更新 \(x,y,z\) 的 direct 三块算法不同，也没有有限周期反例。

[Heusdens--Zhang (2024)](https://arxiv.org/abs/2309.12897) 则避免 primal slack，通过 dual nonnegativity 和 reflection operator 扩展 PDMM。相关近期论文整体上更常绕开或修正 direct slack-last sweep，而不是证明它无条件收敛。

## 7. 逐项匹配表

| 文献 | 同一 slack 模型 | slack-last direct | \([I,I,I]\) | 强凸二次 | 严格有界有限周期 | 判定 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Chen--He--Ye--Yuan 2016 | 否 | 一般三块 direct | 否 | 有强凸扩展 | 否 | 一般非收敛先例 |
| He--Xu--Yuan 2023 | 是 | 是 | 允许但未专门分析 | 允许 | 否 | 最接近的同算法 gap statement |
| Cai--Han--Yuan 2017 | 一般三块 | 是 | 可取 | 要求第三块强凸 | 否 | 不适用 slack-last indicator |
| Lin--Ma--Zhang 2015 | 是 | 否，slack-first | 可取 | 原目标强凸 | 否 | 小罚参数正向结果 |
| Ghadimi et al. 2015 | QP 投影 | 否，两块 | 不对应 | 是 | 否 | active-set 技术先例 |
| Lew et al. 2026 | feasibility slack QP | 否，联合成两块 | 不对应 | 是 | 否 | 近期但算法不同 |
| 本项目 | 是 | 是 | 是 | 前两块纯强凸 | 是，period 66 | 当前未发现同型先例 |

## 8. 检索过程与覆盖边界

本次检索包括：

- 本仓库已下载全文中的 direct ADMM、VI/PPA、PPC、ADM-G、small-step 和 active-set 论文；
- Chen--He--Ye--Yuan 的 OpenAlex 前向引用集合（756 项）按 `slack`、`periodic`、`cycle`、`orthant`、`inequality`、`identity`、`projection` 等词筛查；
- He--Xu--Yuan 的全部 10 项 OpenAlex 前向引用逐题名和摘要筛查；
- 公开网页对 `periodic orbit ADMM`、`bounded cycle three-block ADMM`、`nonnegative slack direct extension ADMM counterexample` 等组合检索；
- 2025--2026 年公开的 slack-QP ADMM 和三算子 splitting 论文。

没有覆盖：

- 付费数据库的全文级检索；
- 逐篇阅读全文 756 项前向引用；
- 未公开、未索引或非英文手稿。

所以“未发现”是审计事实，“绝对没人做过”不是当前证据能够证明的命题。

## 9. 建议用于论文的表述

推荐中文：

> 一般 direct 多块 ADMM 的发散及强凸反例均已有先例。本文的新内容不是重复该一般事实，而是在由两块线性不等式模型自然产生的 identity-slack 子类内，给出一个严格可达、完全有理、有界且周期有限的原始 slack-last EADMM 反例。据本次文献审计所知，尚未发现同型结果。

不应使用：

- “我们首次证明三块 ADMM 不收敛”；
- “这是首个强凸 ADMM 反例”；
- “文献已经证明这个 slack 算法必然收敛”；
- “数据库没搜到，所以绝对没人做过”。

## 10. 下一步的优先权加固

1. 请熟悉 operator splitting/ADMM 的外部研究者核对算法等价性和文献边界。
2. 用 MathSciNet、Scopus、Web of Science 对 exact phrases 及 Chen、He--Xu--Yuan 引用链补检。
3. 把 exact certificate、参数和一页可人工核查的定理陈述公开为预印本附件，建立时间戳。
4. 论文题目和摘要写全 `identity-slack`、`slack-last`、`bounded periodic orbit`、`exact rational certificate` 四个限定词。

## 11. 可复核产物

- 检索配置：`outputs/prior_art_audit_2026_07_14/research_profile.json`
- 候选论文：`outputs/prior_art_audit_2026_07_14/candidate_papers.json`
- 检索报告：`outputs/prior_art_audit_2026_07_14/retrieval_report.md`
- 创新线索：`outputs/prior_art_audit_2026_07_14/innovation_candidates.json`
- 创新报告：`outputs/prior_art_audit_2026_07_14/innovation_report.md`
