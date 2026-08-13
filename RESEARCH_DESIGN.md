# 修订后的研究设计与研究问题

## 一、核心研究问题

修订后的实验不再用 Part 1 创造同一对参与者之间的关系历史。Part 1 测量每个人在进入重复互动之前的两类行为倾向：作为 Player 1 时的信任投入，以及作为 Player 2 时的条件互惠。Part 2 的角色、搭档和 treatment block 均随机分配，不使用 Part 1 回答进行分层。

核心研究问题变为：**资本再投入机会和结果噪音如何决定重复信任关系的形成、维持和崩塌？Part 1 行为能否预测这种动态？**

这可以拆分为六组问题：

1. **Part 1 行为是否具有跨阶段预测力？** Part 1 中更愿意发送的参与者，在 Part 2 成为 Player 1 后是否持续发送更多、建立更大暴露，并在允许时投入更多账户资金？Part 1 中条件返还比例更高的参与者，在 Part 2 成为 Player 2 后是否持续返还更高比例？
2. **Reinvestment 是否放大经济暴露？** 当 Player 1 可以把账户资金再次暴露给同一 Player 2 时，合作关系是否积累更大的峰值暴露，并在信任破裂后出现更大的撤资？
3. **Noise 是否改变行为更新？** 当 realized return 可能偏离 Player 2 的 intended return 时，Player 1 是否减少对单次坏结果的反应，使信任表现出更强的粘性？
4. **合作如何崩塌？** Noise 是缓冲一次坏结果，还是仅仅延迟信任崩塌，并使之后的下降更加集中和剧烈？Reinvestment 是否进一步放大这种崩塌？

## 二、Part 1：一次性 strategy method

所有参与者在不知道最终报酬身份的情况下完成两项决策：

- **Player 1 决策：** 从10点禀赋中选择发送0至10之间的一个整数。
- **Player 2 策略：** 分别说明当 Player 1 发送1至10点时愿意返还多少。发送额乘以2，因此每个条件下的返还上限为收到的金额。

所有人完成决策后，系统随机匹配两人，并随机决定谁的 proposer 决策和谁的 responder 策略用于 Part 1 报酬。只有与实际发送额对应的 responder 条件选择会被执行。

Part 1 的作用是获得有真实金钱激励的、处理前行为测量，而不是建立关系历史。Part 1 收益与 Part 2 账户分开，不进入 Part 2 的 reinvestment 资金。

## 三、Part 1 预处理行为测量

Part 1 回答不用于随机化。数据库保留两个连续指标：Player 1 发送额，以及十个条件返还比例的平均值

\[
R_i=\frac{1}{10}\sum_{x=1}^{10}\frac{r_i(x)}{2x}.
\]

这些指标可用于检验跨阶段预测力、提高回归精度以及探索 treatment effect heterogeneity，但不能解释为随机处理。正式设计不再生成 High/Low 分类，也不再构造 HH、HL、LH、LL 配对。

## 四、Part 2 配对和 treatment 随机化

Part 2 仍包含原来的2×2处理：

| 维度 | 水平 |
|---|---|
| Reinvestment | 不可使用账户 / 可以使用账户 |
| Noise | 无电脑调整 / 对return进行均值保持调整（×0、×1、×2；概率分别为20%、60%、20%） |

Noise 只调整最终到达 truster 的返还额，并且只影响 truster 的收益。Trustee 的收益始终等于其收到的金额减去其主动选择的返还额，不受电脑调整影响。

Official session 使用24名参与者。系统在所有 Part 1 回答锁定后：

1. 随机指定12名 Player 1和12名 Player 2；
2. 在两种角色之间随机配对，形成12对；
3. 将12对随机分入四个 treatment cell，并强制每个 cell 恰好包含3对。

除每个 cell 的样本量配额外，不根据 Part 1 回答、行为类型或其他协变量限制随机化。研究数据中必须保留随机化记录和随机种子，以便复核。

Part 1 与 Part 2 采用相同兑换率：每点 USD 0.50。每位参与者另获固定 USD 5.00 show-up fee。

## 五、主要结果变量

### Truster 行为

- 当前禀赋发送额；
- reinvestment 金额及其占可用账户的比例；
- 总 relationship exposure；
- 负面 realized return 后的发送下降；
- 大规模撤资或停止投入；
- 对 trustee intended return 的事前与事后信念及误差。

### Trustee 行为

- intended return；
- intended return 占收到金额的比例；
- 对 truster 发送额的信念及误差；
- 对不同历史发送和账户规模的条件反应。

### Pair-level dynamics

- 总剩余和双方账户轨迹；
- 合作持续时间；
- 关系进入高合作状态的速度；
- 负面信号后的恢复或崩塌；
- 行为波动和路径依赖。

## 六、识别和解释

Reinvestment、Noise、角色和具体搭档均随机分配，因此四个 treatment cell 的比较具有因果解释。Part 1 发送和条件返还指标是预处理测量，可以作为控制变量或 moderator；它们与后续行为的关系属于预测性或异质性分析，而不是这些指标自身的因果效应。主要标准误应在固定 pair 层级聚类，并在适当时加入 session fixed effects。

## 七、与旧设计的区别

旧设计把 Part 1 定义为三轮固定搭档互动，并将其解释为关系历史。新设计中 Part 1 只有一次 strategy-method elicitation，Part 2 使用新的角色和搭档。因此新设计识别的是**预先行为类型、搭档构成和制度处理之间的交互**，而不是“与同一个人共同经历的历史如何改变后续信任”。涉及 relationship memory、the north remembers 或同一关系历史缓冲噪音的旧假设，需要相应重写或放弃。
