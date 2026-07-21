# 智能体
https://chatgpt.com/g/g-p-68d536a5d2508191b87182af5929a762-ke-yan/c/69230cc3-66ac-832b-b6c8-af33fcd54c7a
## 测试/表征方法参考

【实验方法整理agent】
比较全面的可以参考2023相关度较高的这篇EST，基本要用的方法全都有。
[[【SI】（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.pdf]]

#日志20251010 
### 买药品：
- preview具体自己的制备方法，详细到步骤和数字，列出来
	- 查验数字在【文献中找到对应的范围】，确定浓度。
- 把里面【需要购买的药品】的下表列出来，尤其要注意的CAS号（一个化学品对应一种）
- 去查询每种试剂+每种试剂配置出来的溶液。
	- 一次用量，及可以用多长时间/保质期——对应一次要买的量
	- 如果是标比样品，确定测试方法是否标样和产物的一样要买。
	- 样品的形态——固体or液体？优先固体，如果是液体最好查清楚液体保存原因是什么？
	- 。
- 

| 中文名+英文名                                                                           | 英文简称  | 化学式                               | CAS       | 规格示例     | 商家           | ChemicalBook 链接 |
| --------------------------------------------------------------------------------- | ----- | --------------------------------- | --------- | -------- | ------------ | --------------- |
| 甲基苯基亚砜/Methyl phenyl sulfoxide!![[Pasted image 20251010173501.png]]               | PMSO  | C7H8OS                            | 1193-82-4 | <br>5g/瓶 | 阿拉丁(Aladdin) |                 |
| 苯甲砜/PMSO2（甲基苯基砜）<br>\|Methyl phenyl sulfone\|![[Pasted image 20251010173541.png]] | PMSO2 | \|   \|<br>\|---\|<br>\|C7H8O2S\| | 3112-85-4 | 5g/瓶     |              |                 |

- 






### 一、化学物质分析方法

1. **ClO₂的鉴定与定量**：采用N,N-二乙基对苯二胺（DPD）法，通过测定515nm处的吸光度，结合甘氨酸淬灭游离氯以排除干扰（Text S3）。
2. **有机污染物分析**：使用高效液相色谱（HPLC），针对不同污染物（如头孢氨苄CPX、苯酚、PMSO等）优化流动相、波长和流速（Table S1）。
3. **阴离子分析**：采用高效离子色谱（HPIC），以碳酸钠/碳酸氢钠为淋洗液，检测Cl⁻、ClO₂⁻、ClO₃⁻等离子（Table S2）。
4. **18O标记PMSO₂分析**：使用超高效液相色谱-四极杆飞行时间质谱（UPLC-Q-TOF MS），优化流动相梯度和鞘气参数（Table S3）。
5. **氯化副产物分析**：
    - **三卤甲烷（THMs）**：气相色谱（GC）配Rtx-1毛细管柱，程序升温35°C（22 min）→145°C（10°C/min）。
    - **卤乙酸（HAAs）**：GC配DB-1701毛细管柱，多段程序升温（40°C→205°C）（Text S4）。

### 二、活性物种检测方法

1. **·OH检测**：以香豆素为探针，通过荧光光谱（λEx=332 nm，λEm=460 nm）测定7-羟基香豆素（7-HOC）生成（Text S5）。
2. **Co(IV)检测**：
    - **电子顺磁共振（EPR）**：原位冷冻（77 K）记录Co₃O₄催化亚氯酸盐过程中的时间分辨EPR光谱（Text S6）。
    - **PMSO转化法**：通过HPLC检测PMSO氧化为PMSO₂的转化率（η(PMSO₂)），间接表征Co(IV)浓度（Figures S13-S15）。
3. **HClO检测**：以罗丹明6G肼（RB6G）为探针，通过荧光光谱（λEx=500 nm，λEm=550 nm）测定其开环产物（Text S7）。

### 高价金属-PMSO（本身就是OAT反应+18O定位直接定性）
| 中文名+英文名                        | 英文简称 | 化学式    | CAS       | 规格示例     | 商家           | ChemicalBook 链接                                                                                  |
| ------------------------------ | ---- | ------ | --------- | -------- | ------------ | ------------------------------------------------------------------------------------------------ |
| 甲基苯基亚砜/Methyl phenyl sulfoxide | PMSO | C7H8OS | 1193-82-4 | <br>5g/瓶 | 阿拉丁(Aladdin) | [锐竞科研采购平台—科研试剂耗材采购管理平台](https://www.rjmart.cn/productDetail?productId=200481622396&suppId=82275) |


https://chatgpt.com/c/68de7850-b5e8-8323-bfd3-038618f2b438

source:[[※【SI】2024-PNAS-Co-SAC+Co(IV)=O+PMS.pdf]]的Text3

prompt：Co(IV)=O的测试方法附带原文的有逻辑得分点，要可以看着操作的

### Co(IV)=O的测试方法（基于原文可操作步骤）

#日志20251010 
## 药品购买
-


#### 一、核心原理 通过探针化合物甲基苯基亚砜（PMSO）与Co(IV)=O的特异性氧化反应生成甲基苯基亚砜（PMSO₂），结合动力学分析计算Co(IV)=O的稳态浓度及贡献。 
#### 二、实验材料与条件 
1. **试剂**： 
- 催化剂：Co-OCN（或Co-CN，0.03 g/L）
- 氧化剂：PMS（0.1 mM） 
- **探针化合物：PMSO（1 μM）** 
- 目标污染物：APAP（2 mg/L，可选） 
- 溶剂：超纯水（pH=4.24，298 K） 
2. **仪器**： 
- 高效液相色谱（HPLC，配备紫外检测器或质谱） 
- 恒温反应装置 
- #### 三、操作步骤
>体系不变化，只是在最后一步加入PMSO（浓度确定：1μM for PMSO)）
>同样是淬灭
>液相测试PMSO和PMSO2（测试看看浓度对应，以及四价Co和PMSO的定量关系）
>-  没有定量【高价金属】，基本上只是测试PMSO减少和PMSO2的增加，以及对应产物ClO2的增加量
>- 这俩都是OAT机制。
>- OAT机制就可以做O同位素标记，
>次氯酸盐金属氧化：确定O原子是从【氧化剂】转移到【低价金属活性位点】。
>1. **氯ite活化阶段**  
    ClO₂⁻在OV-Co₃O₄表面氧空位（OV）处发生O-Cl键均裂，解离的氧原子（O*）被低配位Co原子捕获，形成高自旋态≡Co(IV)=O（式2）。  
    _关键过程_：OV通过“氧原子捕获效应”定向锚定ClO₂⁻，促进O*转移至Co活性位点。
>另外可以反证PMSO方法的准确度，也就是PMSO→PMSO2的氧原子转移是一起的。
>-1. **PMSO氧化阶段**  
    ≡Co(IV)=O作为氧供体，将O*转移至PMSO的S原子上，实现亚砜（S=O）向砜（O=S=O）的转化：  
    **PMSO + ≡Co(IV)=O → PMSO₂ + ≡Co(II)**  
    该过程遵循协同OAT机制，≡Co(IV)=O的高氧化电位（>1.95 V）确保反应不可逆。
    

### 3. 与研究的
![[Pasted image 20251009120810.png]]
![[Pasted image 20251009120834.png]]
1. **反应体系搭建**： 在反应器中依次加入Co-OCN催化剂、PMS和PMSO，磁力搅拌混合，反应体积根据实验需求确定（建议50 mL或100 mL）。 
2. **样品采集与检测**： 
- 定时取样（0、5、10、20、30、60 min），立即加入过量淬灭剂（如DMSO，根据表S4，其与Co(IV)=O反应速率常数为2.4×10⁶ M⁻¹s⁻¹）终止反应。 
- 通过HPLC检测PMSO和PMSO₂浓度，色谱条件见表S8（流动相：30%乙腈+70%水，检测波长233 nm（PMSO）和217 nm（PMSO₂），流速1.0 mL/min）。
2. **同位素标记验证（可选，原文图S12-S14）**：
- 使用H₂¹⁸O替代超纯水，重复上述实验，通过质谱检测PMSO₂的¹⁸O标记比例，确认Co(IV)=O中氧原子来源。
- #### 四、数据分析与计算 
2. **转化率（η）计算**：

3. **氧化贡献计算**： 根据公式S20-S21，结合APAP降解动力学，计算Co(IV)=O对污染物去除的贡献百分比。 
- #### 五、关键验证实验 
2. **淬灭实验**：加入特异性淬灭剂（如NaN₃，表S4），观察PMSO₂生成量变化，排除其他活性物种（如•OH、SO₄•⁻）干扰。 
3. **对照实验**： - 无催化剂对照组：仅PMS+PMSO，验证Co(IV)=O由催化剂活化PMS产生。 - 溶剂同位素效应：对比H₂O和D₂O中反应速率（原文图S10），排除¹O₂干扰（¹O₂在D₂O中寿命延长，若反应速率无显著变化，证明非¹O₂主导）。 #### 六、注意事项 1. **淬灭剂选择**：避免使用同时淬灭多种活性物种的试剂（如甲醇），优先选择对Co(IV)=O特异性高的淬灭剂（如DMSO）。 
4. **探针浓度**：PMSO浓度需低至不影响APAP降解（原文图S15，0.2 mg/L探针不干扰反应）。 
5. **数据重复性**：建议至少3次平行实验，误差范围控制在±5%以内。 #### 七、原文依据 - 原理与公式：Text S3（公式S9-S13） 
- 实验条件：Fig. S16、Table S5、Table S8 - 验证方法：Fig. S10（溶剂效应）、Fig. S12-S14（同位素标记）、Table S6（稳态浓度计算结果） 通过以上步骤，可定量检测Co(IV)=O的生成速率、稳态浓度及氧化贡献，操作流程严格遵循原文方法，结果可直接用于催化剂性能评价。
![[Pasted image 20251002215806.png]]


source：
[[（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响]]

>两种方法结合解决了Co(IV)稳定性低、难以直接表征的问题，
>-文献明确讨论四价钴（Co(IV)）的两种测试方法。 **两种方法的区别** 
>1. **原理不同** 
>- ==**PMSO探针法**：基于Co(IV)与苯甲基亚砜（PMSO）的氧原子转移（OAT）反应==，生成特征产物苯甲基砜（PMSO₂）。
>通过检测PMSO₂的生成量可间接定量Co(IV)，反应式为： \[ \text{PMSO} + \text{Co(IV)} \rightarrow \text{PMSO}_2 + \text{Co(III)} \] 该方法利用Co(IV)的强氧化能力，仅特异性氧化PMSO生成PMSO₂，而ClO₂等其他氧化剂不干扰检测（图S13）。 
>- **¹⁸O同位素标记法**：利用Co(IV)与H₂¹⁸O的氧原子交换（OAE）特性。在H₂¹⁸O基质中，Co(IV)的氧原子可与水中¹⁸O交换，导致PMSO₂产物中出现¹⁸O标记（如PMS¹⁶O¹⁸O），通过质谱检测¹⁸O标记产物直接证明Co(IV)存在（图2a）。 
>2. **检测维度不同** - PMSO探针法为**间接定量法**，通过产物PMSO₂的浓度推算Co(IV)生成量（图S14-S15）。 - ¹⁸O同位素标记法为**直接定性法**，通过同位素标记产物的分子质量偏移（如m/z=156.9960对应PMS¹⁶O¹⁸O）直接验证Co(IV)的存在。 
>3. **两种方法的联系** 1. **互补验证Co(IV)的生成** PMSO探针法证明Co(IV)的氧化活性，¹⁸O标记法则从原子层面提供Co(IV)存在的直接证据，二者共同支持Co₃O₄/亚氯酸盐体系中Co(IV)的生成（图2a、S17）。 2. **均基于Co(IV)的氧转移特性** 两种方法均依赖Co(IV)的氧原子转移能力：前者通过氧转移生成产物，后者通过氧交换实现同位素标记，均体现Co(IV)作为高价金属物种的独特化学行为。 **研究意义** 两种方法结合解决了Co(IV)稳定性低、难以直接表征的问题，为复杂体系中高价金属物种的识别提供了可靠手段，也为揭示质子增强效应（图2e）和pH依赖的氧化机制（图2f）奠定了方法学基础。
![[Pasted image 20251002211058.png]]





#### 1. **实验方法（Experimental Method）**

采用**非原位程序**（ex-situ procedure）在电子顺磁共振仪（Bruker EMXnano）上记录Co₃O₄活化亚氯酸盐过程中的时间依赖性EPR光谱。具体步骤如下：

- 将Co₃O₄和亚氯酸盐加入密封反应池中，在预设条件下（[Co₃O₄]₀=1.0 g/L，[亚氯酸盐]₀=0.1 mM，初始pH=6.5）磁力搅拌反应。
- 在特定时间间隔分离Co₃O₄催化剂，装入石英EPR管，用液氮（77 K）冷冻后采集数据。分离与冷冻间隔10分钟。

_关键仪器参数_：

- 调制幅度（modulation amplitude）：1.0 G
- 调制频率（modulation frequency）：100.0 kHz
- 时间常数（time constant）：1.28 ms
- 扫描时间（sweep time）：120.07 s
- 扫描宽度（sweep width）：1000–3996.67 G
- 磁场吸收峰g值与自旋态S的关系：_gₑ=2S+1_

#### 2. **核心目的（Core Objective）**

通过EPR光谱的时间演变，**直接捕捉Co₃O₄活化亚氯酸盐过程中高价钴物种（Co(IV)）的生成与转化**，为该体系中Co(IV)的存在提供实验证据。

#### 3. **结果关联（Result Relevance）**

结合原文图S17（时间依赖性EPR光谱），可分析Co(IV)物种的动态变化规律，进一步阐明质子增强效应下Co(IV)的生成机制及其在污染物降解中的作用（如cephalexin（CPX）的氧化）。


### ClO2-N,N-二乙基对苯二胺（DPD）法
source:
[[【SI】2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.pdf]]

| 中文名+英文名                                                                        | 英文简称     | 化学式                | CAS      | 规格示例                                        | 商家      | ChemicalBook 链接                                                                                                                  |
| ------------------------------------------------------------------------------ | -------- | ------------------ | -------- | ------------------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------- |
| N,N-二乙基对苯二胺/N,N-Diethyl-p-phenylenediamine![[Pasted image 20251010160106.png]] | DPD      | C10H16N2           | 93-05-0  | 5 g——实验250ml溶液需要1.1g，配置后棕色瓶子避光保存            | Macklin | [锐竞科研采购平台—科研试剂耗材采购管理平台](https://www.rjmart.cn/productDetail?productId=200464662892&suppId=82275)                                 |
| 乙二胺四乙酸二钠/EDTA disodium salt                                                    | EDTA-2Na | C10H14N2Na2O8·2H2O | 139-33-3 | 50g/L,实验需要8g/L——直接10ml母液+52.5ml水即可（10→62.5） | Macklin | [锐竞科研采购平台—科研试剂耗材采购管理平台](https://www.rjmart.cn/productDetail?productId=200333844050&suppId=2559&source=1&eId=1029051389550006274) |
| ClO2                                                                           |          |                    |          | ——实验需要几十个微摩尔每升                              |         | 【淘宝】https://e.tb.cn/h.ShmK9uCElpTy6zS?tk=Vh4Mf0c0RE8 CZ057 「消毒剂CLO2含量检验用,二氧化氯标准溶液/二氧化氯储备标准溶液」<br>点击链接直接打开 或者 淘宝搜索直接打开            |
#### 实验前（Pre-experiment）

1. 制备新鲜 ClO₂ 储备液：
- 150 mL 200 mM HCl 以 7.5–10 mL min⁻¹ 注入 100 mL 400 mM NaClO₂，
- 密封磁力搅拌 60 min；
- 生成的 ClO₂ 由压缩空气吹出，经沾有NaClO₂固体 玻璃管除 Cl₂ 后，通入 100 mL 水溶解ClO2，2–4 °C 避光储存。  
    (Before determining the concentration of the generated ClO₂ in the Co₃O₄/chlorite process, the fresh ClO₂ stock solution was prepared by a modified hydrochloric acid-chlorite method. First, 150 mL of dilute hydrochloric acid (200 mM) was injected into 100 mL of NaClO₂ solution (400 mM) with a rate of 7.5-10 mL min⁻¹. The mixed solution is stirred magnetically under a sealed bottle for 60 min. Meanwhile, the generated ClO₂ is blown out of the bottle with compressed air and passes through a glass tube filled with solid NaClO₂ to remove undesirable Cl₂. Finally, the purified ClO₂ was blown into a brown bottle filled with 100 mL of water and stored at 2-4°C.)
    
1. 使用前以标准碘量滴定法校准该ClO2储备液浓度。  
    (The concentration of the obtained ClO₂ stock solution is calibrated by the standard iodometric titration method before every use.)
#日志20251010
决定直接买ClO2标液（CAS：10049-04-4）
这是标液的制备原理，来自国标。

![[c7578c8283ebae6091b2ade5462a3d25 1.png]]

2. 配制 DPD 指示剂：
	- 药品名称：**N, N-diethyl-p-phenylenediamine (DPD)** ——二乙基对苯二胺（CAS：93-05-0）
	- 药品名称： 乙二胺四乙酸二钠 （EDTA-2Na）（CAS：139-33-3）
-  1.1 g DPD 溶于 250 mL 混合液（223ml水+2.0 mL H₂SO₄ + 25 mL EDTA-2Na 8.0 g L⁻¹），4 °C 储存。  
- (The DPD solution was prepared by dosing 1.1 g DPD into a 250 mL mixed solution of 2.0 mL of H₂SO₄ and 25 mL of EDTA-2Na (8.0 g L⁻¹) and stored at 4°C.)
#日志20251010 
[决定把250ml的DPD指示剂，等比例缩放至100ml]([Kimi - 更强大的 AI 助手](https://www.kimi.com/chat/d3kb25a1ol7rjnb7tnq0))

### DPD显色剂配置

| 组分                   | 计算           | 用量          |
| -------------------- | ------------ | ----------- |
| **DPD**              | 1.1 g × 0.4  | **0.44 g**  |
| **水**                | 223 mL × 0.4 | **89.2 mL** |
| **H₂SO₄**            | 2.0 mL × 0.4 | **0.80 mL** |
| **EDTA-2Na 8 g L⁻¹** | 25 mL × 0.4  | **10 mL**   |
1. 称取 **0.44 g DPD** 溶于约 70 mL 纯水。
    
2. 加入 **0.80 mL 浓 H₂SO₄**（缓慢加入并混匀）。
    
3. 加入 **10 mL 已配好的 ==8 g/L EDTA-2Na 溶液==**。
	- 10ml母液+52.5ml的水——100ml，避光冷藏
	- 需购买100ml棕色玻璃瓶
    
4. 补足纯水至 **100 mL**。（+19.2ml=）
    
5. ==过滤（0.45 µm）后 4 °C 避光保存，建议 **1 周内用完**。==
	- 100ml棕色试剂瓶，和edta-2na一起放在冰箱，如果有问题就等比例缩小

### 【混入其中】EDTA-2NA

800mg in 100ml

### 【反应时用】ph=0.65 磷酸缓冲液——xhs搜索得到

磷酸二氢钾（7778-77-0,, 1柜子）0.68g
15ml+ 200uL 0.1 NaOH
84.8ml= 80ml + 4.8ml

![[27623ba888c764065d3fd424951f8196.jpg]]

![[d2fc7e04c59c8c424371fa65d8288503.png]]
    
    

---

#### 实验中（During experiment）

- 应该会分为两种情况
- - 

4. 在指定时间从 Co₃O₄/亚氯酸盐体系采集 5 mL 样品。  
	1. 应该是在反应结束时间60min的时候取样一次还是？，如果一次取样的话那对DPD显色剂的消耗其实很小。
    (First, 5 mL of samples were collected from the Co₃O₄/chlorite process at specific times.)
    
5. 依次加入 0.75 mL 磷酸盐缓冲液 (pH = 6.5)、0.25 mL DPD 指示剂、0.05 g KI。
	1. 这些都可以在反应的时候提前配好
    (Then, 0.75 mL of phosphate buffer (pH = 6.5), 0.25 mL of DPD indicator, and 0.05 g KI were added to the collected samples in sequence.)

- 取 **5.00 mL 样品**
    
- 加 **0.75 mL pH 6.5 磷酸盐缓冲液**
    
- 加 **0.25 mL DPD 指示剂溶液**
    
- 最后加 **0.60 mL KI 溶液**（浓度是0.5M, 4.15g in 50ml）——反应启动关键
    
- 混匀后 **约 1 min** 在 **515 nm** 测吸光度——标线和样品在同一窗口读数
    
7. 立即在 515 nm 处用 UV-vis 分光光度计 (UV-2450, Shimadzu) 测定混合液吸光度。  
    (The absorbance of the mixed solution was determined at 515 nm on a UV-vis spectrophotometer (UV-2450, Shimadzu).)


## 标液配置：

母液浓度10mg/L
0-200 uM
0 5 10 20 50 100 200
可以。把单位换成 **mg/L** 后，只要把 100 µM 换算成 mg/L，再在这附近选 3–5 个点就行。

---

## 1) 先把 100 µM 换成 mg/L

ClO₂ 分子量 67.45 g/mol

[  
100\ \mu M = 100\times10^{-6}\ \text{mol/L}\times67.45\ \text{g/mol}  
= 0.006745\ \text{g/L}  
= \mathbf{6.745\ mg/L}  
]

所以你要覆盖的范围核心就是 **到 6.745 mg/L 左右**。

同时记一个好用换算：

- **1 mg/L ClO₂ ≈ 14.826 µM**
    
- **1 µM ≈ 0.06745 mg/L**
    

---

## 2) 给你两套 3–5 点的 mg/L 标线建议

### 方案 A 5 点，覆盖更均匀（推荐）

**0, 1, 2.5, 5, 7.5 mg/L**

- 7.5 mg/L ≈ 111 µM，略高于 100 µM，覆盖更稳
    
- 5 mg/L ≈ 74 µM
    
- 2.5 mg/L ≈ 37 µM
    

### 方案 B 4 点，更省事

**0, 1, 3, 7 mg/L**

- 7 mg/L ≈ 104 µM，刚好卡住 100 µM 附近
    
- 3 mg/L ≈ 44.5 µM
    
- 1 mg/L ≈ 14.8 µM
    

### 方案 C 3 点，最省事

**0, 3.5, 7 mg/L**

- 3.5 mg/L ≈ 52 µM
    
- 7 mg/L ≈ 104 µM
    

---

## 3) 用你当前母液 10 mg/L（=10 µg/mL）来配最方便

你母液就是 **10 mg/L**。如果每个标准点配 **10.00 mL**，稀释超简单：

[  
V_\text{母液} = \frac{C_\text{目标}}{10}\times 10.00 = C_\text{目标}\ (\text{mL})  
]

也就是：

> **目标是多少 mg/L，就取多少 mL 的 10 mg/L 母液，再加水补到 10 mL**

==举例按“方案 A 5 点”每点 10 mL：==

|目标浓度 (mg/L)|对应浓度 (µM)|取 10 mg/L 母液 (mL)|加水 (mL)|总体积 (mL)|
|---|---|---|---|---|
|0.0|0|0.00|10.00|10.00|
|1.0|14.8|1.00|9.00|10.00|
|2.5|37.1|2.50|7.50|10.00|
|5.0|74.1|5.00|5.00|10.00|
|7.5|111.2|7.50|2.50|10.00|

然后每个点取 5.00 mL 进入显色体系即可。

---

如果你告诉我你希望每个点配 **10 mL** 还是 **20 mL**，我可以把你选的那套 3–5 点直接给成一张“母液多少 + 水多少”的最终表。1. 先配置

# ClO2的测样sop
# Ce–Co₃O₄ / ClO₂⁻ 体系

## ClO₂ 测定 · 无脑操作卡（DPD–KI 法）

**KI 条件：600 µL · 0.5 M（固定）**  
**测定波长：515 nm**

---

## 一、反应体系（先确认）

- 溶剂：去离子水
    
- 反应物：NaClO₂
    
- 催化剂：Ce–Co₃O₄（0.5 mmol Ce 掺杂样）
    
- 不加污染物
    
- 不加任何淬灭剂
    

---

## 二、反应启动

1. 将 Ce–Co₃O₄ 加入水中，搅拌或超声分散 5–10 min
    
2. **一次性加入 NaClO₂**
    
3. 立即开始计时  
    → 此刻为 **t = 0**
    

---

## 三、取样时间点

**0 / 5 / 10 / 20 / 30 / 40 / 50 / 60 min**

提前准备并标记 8 支显色管：

t0, t5, t10, t20, t30, t40, t50, t60

---

## 四、每个时间点的“无脑显色流程”

到时间点后，**严格按顺序做，不要跳步**：

1. 取 **5.00 mL** 反应液 → 加入对应显色管
    
2. 加 **0.75 mL pH 6.5 磷酸盐缓冲液**，轻轻混匀
    
3. 加 **0.25 mL DPD 指示剂溶液**，轻轻混匀
    
4. **最后一步**：加 **600 µL 0.5 M KI 溶液**，立即混匀  
    → 以此刻作为显色起点
    
5. **加 KI 后 1.0 ± 0.1 min**，在 **515 nm** 读取吸光度
    

---

## 五、必须遵守的固定条件

- KI **永远最后加**
    
- 所有样品和标线 **KI 都是 600 µL · 0.5 M**
    
- 加 KI 后的读数时间 **必须一致**
    
- 不使用 Na₂S₂O₃
    
- 不存样，不延迟显色
    

---

## 六、标线对应规则（提醒）

- 标线用纯水 + ClO₂ 配制
    
- 标线显色步骤 **与样品完全一致**
    
- 标线与样品 **同批测定**
    

---

## 七、体系总体积参考（不用算）

- 样品：5.00 mL
    
- 缓冲：0.75 mL
    
- DPD：0.25 mL
    
- KI：0.60 mL  
    **总计 ≈ 6.60 mL**
    

---

## 八、一句话自检（做之前看一眼）

> 反应不是纯水  
> 不加淬灭剂  
> 取样即显色  
> KI 最后加  
> 1 分钟测 515 nm