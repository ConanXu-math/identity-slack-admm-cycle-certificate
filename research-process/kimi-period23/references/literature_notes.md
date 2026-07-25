# 文献档案（第一手来源，访问日期均为 2026-07-22）

每条标注核验级别：[PDF]=取得并阅读全文；[ABS]=摘要页；[META]=仅元数据；[2ND]=经其他已取文献转引。

## 核心问题文献

1. **[CHYY]** C. Chen, B. He, Y. Ye, X. Yuan. The direct extension of ADMM for multi-block
   convex minimization problems is not necessarily convergent. *Math. Program.* 155 (2016) 57–79.
   DOI 10.1007/s10107-014-0826-5. [PDF]（作者主页开放版：maths.nju.edu.cn/~hebma/paper/ADMM-m-Paper/2016-MP-CHYY.pdf；不在 arXiv）
   - §3 反例：min 0 s.t. A1x+A2y+A3z=0，A=[[1,1,1],[1,1,2],[1,2,2]]（无单位阵块），
     迭代矩阵 M=(1/162)[[144,−9,−9,−9,18],[8,157,−5,13,−8],[64,122,122,−58,−64],[56,−35,−35,91,−56],[−88,−26,−26,−62,88]]，
     特征值 0.9836±0.2984i, 0.8744±0.2310i, 0；ρ(M)=1.0278>1。对任意 β>0 与一个连续稠密
     半空间中的任意起点发散（Thm 3.1）。Remark 3.2：非单点可行集版本同谱半径。
   - §2 正面结果：任两块系数矩阵正交 ⇒ 收敛（相邻正交退化为两块；A1^TA3=0 时 Thm 2.4
     H-范数收缩 + 满秩条件）；Thm 2.5 遍历 O(1/t)。
   - §4 Thm 4.1：即使所有 θ_i 强凸（0.05‖x‖²，同一 A），ρ=1.0087>1，仍可能发散（β=1）。
   → 本工作区 experiments/exp1_chyy.py 独立复现：同一 M，ρ=1.0278393033，仿真几何发散。✔
2. **[HXY21]** B. He, X. Xu, X. Yuan. Extensions of ADMM for Separable Convex Optimization
   Problems with Linear Equality or Inequality Constraints. arXiv:2107.01897；
   出版于 *Handbook of Numerical Analysis* 24 (2023) 511–557. DOI 10.1016/bs.hna.2022.08.002. [PDF/ABS]
   - 精确处理本问题模型（min θ1+θ2 s.t. Ax+By≥b ⇒ 松弛 (1.5)；直接推广 (1.7) 即本研究的迭代，
     仅 z 号约定不同）。摘要原话："it remains unknown whether or not the ADMM can be extended
     to separable convex optimization problems with linear inequality constraints"。
   - 只给出预测-校正型修正算法（(4.2),(5.1),(7.1),(8.1)），不证裸直接迭代。
3. **何炳生报告 "交替方向法(ADMM)20年"**（教师幻灯片原始出处）：
   maths.nju.edu.cn/~hebma/Talk/ADMM-20C.pdf，slide 49 与本工作区 image-3.png 一致：
   "直接推广的ADMM处理上面这种问题…至今既没有证明收敛性，也没有举出反例！"。[PDF]
4. 何炳生《我和乘子交替方向法20年》，运筹学学报 22 (2018) 1–31.
   DOI 10.15960/j.cnki.issn.1007-6093.2018.01.001. [ABS]
5. **Han 综述**：D. Han. A Survey on Some Recent Developments of ADMM.
   *J. Oper. Res. Soc. China* 2022. DOI 10.1007/s40305-021-00368-3. [全文]
   §5 复述 CHYY 反例；未来工作列表未提及 [A,B,I]/不等式猜想 → 佐证仍开放。
6. 检索覆盖面与负面结论：CHYY 全部 771 篇施引（Semantic Scholar）、HXY21 全部 18 篇施引、
   arXiv 2015–2026 多组关键词（"nonnegative orthant"+ADMM、"identity matrix"+multi-block 等）、
   何主页文章/讲义列表（2017–2023）——均无本猜想的证明或反例（截至 2026-07-22）。
   盲点声明：中文期刊全文库（CNKI 等）未检索。

## 直接法的充分条件（均不覆盖 θ3=δ_{R^m_+}, C=I）

7. Lin, Ma, Zhang. arXiv:1408.4265; *J. Oper. Res. Soc. China* 3:251–274 (2015). [PDF]
   f2,f3 强凸 + β 受限 ⇒ 遍历 O(1/t)。δ_+ 非强凸。
8. Lin, Ma, Zhang. arXiv:1408.4266; *SIAM J. Optim.* 25(3):1478–1497 (2015). [PDF] 多块线性速率，需强凸。
9. Han, Yuan. A Note on the ADMM. *JOTA* 155(1):227–238 (2012). [META/2ND] 全强凸 + β 小。
10. Cai, Han, Yuan. *Comput. Optim. Appl.* 66(1):39–73 (2017). [PDF 预印本]
    θ3（最后更新块）强凸 + A2,A3 满列秩 + β∈(0,6μ3/(13‖A3^TA3‖))。δ_+ 不满足。
11. Li, Sun, Toh. arXiv:1410.7933; *Asia-Pac. J. Oper. Res.* 32(4):1550024 (2015). [PDF]
    中间块强凸的半邻近 3 块直接法；其动机例即 δ_{R^m_+} 型但位置不符。
12. Tao, Yuan. arXiv:1609.07221; *Adv. Comput. Math.* 44:773–813 (2018). [PDF]
    m−2 个函数强凸 + 全满列秩 + β 区间。
13. Lin, Ma, Zhang. arXiv:1504.03087; *J. Sci. Comput.* 69:52–81 (2016). [PDF]
    A_N=I 但要求该块函数光滑（KL 框架）。δ_+ 不光滑。
14. Lin, Ma, Zhang. *J. Sci. Comput.* 76:69–88 (2018)（RLSD）. [PDF]
    A3=I + f3 光滑强凸且条件数 <1.0798 ⇒ 未修正 3 块收敛。δ_+ 不满足。
15. Sun, Toh, Yang. arXiv:1404.5378; *SIAM J. Optim.* 25(2):882–915 (2015). [PDF]
    sPADMM3c：修正算法（1→3→2→3 循环 + 半邻近 + 步长），第三块要求线性。
16. Li, Sun, Toh. arXiv:1409.2679; *Math. Program.* 155:333–373 (2016). [PDF] SCB-SPADMM（修正）。
17. Chen, Sun, Toh. arXiv:1506.00741; *Math. Program.* 161:237–270 (2017). [PDF] sGS 不精确主化（修正）。
18. Davis, Yin. arXiv:1504.01032; *Set-Valued Var. Anal.* 25:829–858 (2017). [PDF]
    三算子分裂需一个余强制算子；其 Algorithm 8 非裸直接 3 块（第一块无 prox 罚 + 强凸 + 小步长）。
19. Anshika, Li, Ghosh, Zhang. arXiv:2411.00166; *Optim. Eng.* (2025). [ABS]
    三块 ADMM 派生三算子分裂；仅正交域情形证 1/2-平均。

## 等价视角与不精确准则（L3 回报）

20. slack-ADMM = 两块 ADMM 对联合 (x,y) 块做一次前向 GS 扫 = 不等式约束 ALM 的一次 GS 原始扫。
21. Rockafellar. *Math. Oper. Res.* 1 (1976) 97–116. [META] 不精确 PPA 可和误差准则 (a)(b)(c)。
22. Eckstein, Silva. *Math. Program.* 141:319–348 (2013). [META] 相对误差 ALM 准则；
    后续 Eckstein–Yu arXiv:2503.11809 [PDF] 给出 ρ_k 推广形式 (14)-(16)。单次裸 GS 扫不满足。
23. Solodov–Svaiter HPE 系；Eckstein–Yao *Math. Program.* 170 (2018)；
    Alves–Geremia arXiv:2409.10311 [PDF] σ-相对误差不精确 ADMM。
24. He, Liao, Han, Yang. *Math. Program.* 92:103–118 (2002). [ABS+作者信] 误差平方可和；
    Yuan *Math. Comput. Modelling* 42:1225–1236 (2005) 相对误差改进。
25. Li, Sun, Toh. *Math. Program.* 175:395–418 (2019)（sGS 分解定理）；
    Chen, Li, Sun, Toh. *Math. Program.* 185:111–161 (2021)（sGS-不精确 ALM=ADMM 等价）。
    → 只覆盖对称 GS 全循环；前向单扫不被覆盖。
26. Rockafellar 不等式乘子法：*JOTA* 12:555–562 (1973) [META]；SIAM J. Control 12 (1974) [META]。
    z/λ 更新正是其乘子更新的分裂版。
27. OSQP：Stellato et al. arXiv:1711.08013; *Math. Program. Comput.* 12:637–672 (2020). [ABS]
    通过盒约束投影化为真两块回避三块问题。
28. Fortin–Glowinski (1983)；Glowinski–Le Tallec (1989)；Gabay–Mercier (1976)；
    Glowinski–Marrocco (1975). [META/2ND] Uzawa/ALG3 传统；无松弛结构特异结论。
