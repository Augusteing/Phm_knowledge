# 《航空动力学报》网络首发论文

题目：基于Caps- BiGRU- Attention的直升机涡轮发动机健康管理方法  作者：张振良，毕俊喜，何荣荣，崔哲，周相志  DOI: 10.13224/j.cnki.jasp.20240775  收稿日期：2024- 11- 17  网络首发日期：2025- 04- 21  引用格式：张振良，毕俊喜，何荣荣，崔哲，周相志．基于Caps- BiGRU- Attention的直升机涡轮发动机健康管理方法[J/OL]．航空动力学报. https://doi.org/10.13224/j.cnki.jasp.20240775

网络首发：在编辑部工作流程中，稿件从录用到出版要经历录用定稿、排版定稿、整期汇编定稿等阶段。录用定稿指内容已经确定，且通过同行评议、主编终审同意刊用的稿件。排版定稿指录用定稿按照期刊特定版式（包括网络呈现版式）排版后的稿件，可暂不确定出版年、卷、期和页码。整期汇编定稿指出版年、卷、期、页码均已确定的印刷或数字出版的整期汇编稿件。录用定稿网络首发稿件内容必须符合《出版管理条例》和《期刊出版管理规定》的有关规定；学术研究成果具有创新性、科学性和先进性，符合编辑部对刊文的录用要求，不存在学术不端行为及其他侵权行为；稿件内容应基本符合国家有关书刊编辑、出版的技术标准，正确使用和统一规范语言文字、符号、数字、外文字母、法定计量单位及地图标注等。为确保录用定稿网络首发的严肃性，录用定稿一经发布，不得修改论文题目、作者、机构名称和学术内容，只可基于编辑规范进行少量文字的修改。

出版确认：纸质期刊编辑部通过与《中国学术期刊（光盘版）》电子杂志社有限公司签约，在《中国学术期刊（网络版）》出版传播平台上创办与纸质期刊内容一致的网络版，以单篇或整期出版形式，在印刷出版之前刊发论文的录用定稿、排版定稿、整期汇编定稿。因为《中国学术期刊（网络版）》是国家新闻出版广电总局批准的网络连续型出版物（ISSN2096- 4188，CN11- 6037/Z），所以签约期刊的网络版上网络首发论文视为正式出版。

# 基于Caps-BiGRU-Attention的直升机涡轮发动机健康管理方法

张振良 $^{1,2}$ ，毕俊喜 $^{3}$ ，何荣荣 $^{1}$ ，崔哲 $^{1}$ ，周相志 $^{1}$ ，

（1. 鄂尔多斯应用技术学院大飞机学院，鄂尔多斯市017000；2. 内蒙古工业大学理学院，呼和浩特市0100513. 内蒙古工业大学航空学院，呼和浩特市010051）

摘要：针对直升机涡轮发动机故障难以识别、健康状况难以量化的问题，提出了基于注意力机制的胶囊网络- 双向门控循环单元模型(Caps- BiGRU- Attention)来进行涡轮发动机的故障模式识别以及扭矩裕度预测。该模型由三个主要部分构成：胶囊层用于捕捉输入数据的内在关系，BiGRU层用于提取时间序列特征并输出结果，SE注意力机制对特征加权以突出重要信息。通过直升机涡轮发动机数据集进行实验验证，模型在故障诊断中准确率超过 $99.7\%$ ，并将扭矩裕度预测中的平均绝对误差降低至0.027；其次对诊断和预测过程进行特征分析，寻找有利于发动机健康状态的特征取值范围。最后针对扭矩裕度的分布进行了概率分布拟合，确定在发动机严重失效、轻微失效和健康状态的最佳分布为贝塔分布，为直升机涡轮发动机的健康管理提供了重要参考。

关键词：健康管理；直升机发动机；扭矩裕度；胶囊网络；特征分析；概率分布中图分类号：V240.2 文献标志码：A

# The Health Management Method of Helicopter Turbine Engine Based on Caps-BiGRU-Attention

ZHANG Zhenliang $^{1,2}$ ，BI Junxi $^{3}$ ，HE Rongrong $^{1}$ ，CUI Zhe $^{1}$ ，ZHOU Xiangzhi $^{1}$

(1. Ordos Institute of Technology, Comac Aviation College, Ordos, 017000, China;2. Inner Mongolia University of Technology, College of Science, Hohhot, 010051, China3. Inner Mongolia University of Technology, College of Aeronautics, Hohhot, 010051, China)

Abstract: In response to the issues of difficulties in identifying faults and quantifying the health status of helicopter turbo engines, this study proposes a Caps- BiGRU- Attention model based on the attention mechanism for fault mode recognition and torque margin prediction of turbo engines. The model consists of three main components: the capsule layer captures the intrinsic relationships of the input data, the BiGRU layer extracts time series features and outputs results, and the SE attention mechanism weights the features to highlight important information. Experimental validation on a helicopter turbo engine dataset demonstrated that the model achieved an accuracy exceeding  $99.7\%$  in fault diagnosis and reduced the mean absolute error in torque margin prediction to 0.027. Additionally, a feature analysis was conducted during the diagnosis and prediction processes to identify favorable ranges of feature values for the engine's health status. Finally, probability distribution fitting was performed on the distribution of torque margin, determining that the optimal distributions for severe failure, minor failure, and healthy states of the engine

are beta distributions, providing important references for the health management of helicopter turbo engines.

Key words: Health management; Helicopter engine; Torque margin; Capsule network; Feature analysis; Probability density distribution

通用航空作为航空产业的重要组成部分，近年来在全球范围内得到了迅速发展。在紧急医疗救援、搜索与救援、运输与巡逻任务中，直升机由于其独特的垂直起降能力和灵活的机动性能，在其中扮演着不可或缺的角色。

直升机的可靠运行在很大程度上依赖于其发动机的健康状态。发动机作为直升机的核心部件之一，其故障不仅会影响飞行任务的完成，还可能对飞行安全构成威胁。特别是发动机扭矩的异常变化，常常预示着潜在的机械问题。因此，对直升机发动机进行故障诊断与健康管理，是确保其高效运行的关键。

通过先进的传感技术和数据分析手段，提升对发动机状态的实时监控和全寿命健康管理，已经成为当前通用航空领域的一项重要研究课题。在直升机故障分析方面，侯波等针对某型直升机桨叶疲劳断裂、压力传感器未报警故障，通过故障树分析法开展桨叶失效分析、压力信号器故障模式分析，在此基础上探明故障机理。JessicaLeoni等针对直升机的机械退化，使用卷积自动编码器和基于距离和密度的无监督分类器，采用自动编码器重建误差信息来推断每个检测到的故障的最可能的原因，并制定处理过滤策略，有效地减少误报的数量。Mironov等研究了直升机在飞行中的结构健康监测技术，特别是旋转桨叶的结构健康监测，并验证了模态分析方法在健康管理中的可行性。万安平等提出一种结合变分模态分解与多尺度卷积神经网络融合的故障诊断方法，在直升机附件齿轮箱振动故障诊断中平均准确率为  $97.25\%$  。Kuangchi Sun等提出了一种基于对抗自适应域分布变分学习的直升机传动系统故障诊断方法。在开集域适应过程中，通过对抗训练来度量部分共享类的分布差异，并提出了一种基于伪标签和权值归一化的自监督学习框架，用于挖掘未知标签下目标数据的潜在分布特征。最后用仿真直升机传动系统的算例验证了算法的有效性。Aleksey Mironov等讨论了振动诊断技

术在直升机故障诊断上的应用，并对直升机的关键机械、机构和结构进行了分类讨论，利用振动诊断技术开发直升机状态维修管理系统，以及应用状态维修管理系统为直升机提供基于状态的维修方案，以提高直升机寿命周期的可靠性及费用效率。

在深度学习方面的模型优化上，Lei OuYang等采用注意块和残差结构相结合的方法优化胶囊网络前端结构，采用初始块优化网络中间结构，并创新性地改变了原有胶囊网络的后端结构，使其能够同时处理流型分类和表观速度预测任务。Moudgi以及Aditi提出了一个带有长短时记忆网络的胶囊网络，来处理文字识别中的时间依赖性。Li Xingqiu等提出了一种基于门控循环单元的高级特征融合模块，取代了传统的全连通层，并利用强大的时态特征学习进行特征融合，以某涡扇发动机仿真数据为例，验证了该网络的高效性。Fen Lyu等使用胶囊网络- 双向长短期记忆模型预测进行3D应力预测，该模型综合了胶囊网络的空间关系建模能力和双向长短期记忆的时间建模能力，较好地反映了岩储层的各向异性特征和时间序列信息。Shanu Nizarudeen等研究了残差网络融合SE注意力机制在脑出血预测领域的有效性。管智峰提出了一种基于特征优选和改进学生心理学算法优化混合核极限学习机的变压器故障诊断方法，遍历变压器故障数据属性比，并采用沙普利加法解释（Shapley Additive Explanations，SHAP）模型提取对数据分类影响重要的特征参量。Hajija Wen等比较了四种模型在滑坡模拟上的预测性能，并将SHAP模型引入XGBoost模型，解释了同震滑坡的发生主要受触发因素的影响，因素之间的相互作用也会影响滑坡的发生。

为了将故障分析的结果用于直升机的健康管理方面，Yonghui Lu等采用双向长短期记忆网络和概率分布模型重构响应数据，建立健康状态下传感器之间的响应相关性模型，从而应用于检

测和定位损伤，并基于损伤敏感特征的概率分布模型，得到稳定的损伤量化结果，最后通过一个数值钢梁模型和一座大跨度斜拉桥的实测数据验证了该方法的有效性。张雄等提出一种基于小波包散布与均值漂移概率密度估计的诊断方法，通过计算每个子带的散布构建特征矩阵，采用均值漂移无参估计得到训练样本的概率密度最大位置作为聚类中心。Guangyao Zhang等提出了一种基于信号概率分布测度的健康监测模型，基于机械性能退化数据初步估计出α稳定分布的特征参数，并通过假设检验和参数校准策略定量评价和优化特征参数的一致性。在此基础上，建立了相应的信号分布模型来描述机械设备退化数据的统计特性。

上述文献表明直升机涡轮发动机健康管理领域及基于深度学习的诊断和预测方法研究一直在不断深入，但普遍采用卷积神经进行提取特征，常常忽视特征的姿态和变换对信息的影响，也未重视特征的权重分配，这在一定程度上影响了后续的网络训练。同时，虽然很多人都尝试了使用概率分布密度模型来优化算法，但没有对直升机涡轮发动机健康管理的影响因素进行分析与拟合。研究也缺乏对涡轮发动机健康的特征分析，不能量化参数对发动机的健康影响程度，对直升机涡轮发动机缺乏成熟的健康状态评估方案，导致难以指导具体的运行及维修方案。

基于此，本文通过Caps- BiGRU- Attention模型进行涡轮发动机的故障模式识别以及扭矩裕度预测，寻找有利于发动机健康状态的的特征取值范围，量化参数对发动机的健康影响程度，并针对扭矩裕度的分布进行了概率分布拟合，确定在发动机的扭矩裕度分布并与健康状况确定对应关系，为直升机涡轮发动机的健康管理提供参考。

# 1 模型基础

# 1.1 Capsule Network

胶囊网络（Capsule Network，Caps）用于解决传统卷积神经网络在图像处理中的局限性[18]，尤其是在物体识别和空间变换方面。

胶囊网络通常由多个胶囊层构成。每一层的胶囊负责处理特征并传递信息到上层胶囊。通过

这种结构，胶囊能够捕捉到更复杂的特征组合，从而提高模型性能。在胶囊网络中，信息通过动态路由算法在胶囊之间传递。这个过程确保了高层胶囊能够接收来自低层胶囊的相关信息，从而有效地组合特征。动态路由的机制允许网络自动学习特征之间的关系，增强了模型的表达能力。

# 1.2 BiGRU

门控循环单元（Gated Recurrent Unit，GRU）通过引入更新门和重置门来控制信息的流动。这些门的设计使得模型能够选择性地保留或遗忘信息，从而有效地捕捉长期依赖关系：更新门决定了先前的状态在当前状态中有多少保留。重置门控制如何结合先前状态与当前输入以生成新状态。

双向门控循环单元（Bidirectional Gated Recurrent Unit，BiGRU）的核心思想是通过双向处理来捕捉序列的上下文信息，从而增强模型对时间序列数据的理解能力。

# 1.3 注意力机制

注意力机制的基本思想[20]是：根据输入序列中的每个元素，计算它与其他所有元素之间的相关性，并根据这些权重对输入序列进行加权求和，从而得到一个新的表示。

压缩激活注意力机制（Squeeze- and- Excitation Attention Mechanism，SE）是一种用于增强特征表达能力的有效方法。SE注意力机制主要分为两个步骤：压缩（Squeeze）和激活（Excitation）。

# 2 基于注意力机制的胶囊网络-双向门控循环单元模型

# 2.1 模型结构

Caps- BiGRU- Attention模型由三个主要部分组成：胶囊层、BiGRU层以及SE注意力机制部分。模型示意图如图1所示，在胶囊层中，首先定义胶囊的数量和维度，并通过动态路由机制（用于在胶囊之间传递信息）来处理输入特征。胶囊层的主要目标是捕捉输入数据中的空间关系，尤其适合于处理具有复杂结构的特征。通过对输入特征的加权计算，胶囊层能够生成更具区分性的特征向量，为后续的时间序列处理提供丰富的上下文信息。

BiGRU层用于提取特征并训练。通过双向处理，模型同时考虑前后文信息，从而增强对序列数据的理解。这一层的输出不仅包含当前时刻的

信息，还结合了前后时刻的信息，有助于捕捉长短期依赖关系，尤其在处理具有发动机数据这类时序特性的任务中显得尤为重要。

SE注意力层在网络中的作用是对特征进行加权，从而突出对分类结果影响较大的重要特征。在这一层中，首先通过全局平均池化操作生成通道特征，这一操作能够有效地汇聚全局信息。接着，通道特征经过一系列全连接层的变换，生成用于加权的权重系数。最后，这些权重与BiGRU层的输出相乘，从而在特征层面上实现加权，突出模型在任务中最为重要的特征。这样一来，模型在进行决策时能够更关注于对分类结果影响较大的特征，从而有效提升性能。另外还有输入层接收输入数据，以及输出层输出最终的结果。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/403bd32b457943c7424882a3518e5d20458e849cf4710cac36145ede73499713.jpg)  
图1 Caps-BiGRU-Attention模型结构示意图 Fig.1 Schematic diagram of the Caps-BiGRU-Attention model structure

# 2.2 模型实现步骤

模型运行的具体步骤如下：

2.2 模型实现步骤模型运行的具体步骤如下：首先构建基本的胶囊网络结构：定义胶囊层的构造函数，包括层中的胶囊数量  $N$ ，每个胶囊的维度  $L$  以及动态路由的次数  $R$ ，输入特征维度  $T$ ，注意力通道数  $D$ ，并调用super函数来初始化父类。在build方法中，为胶囊层添加权重  $W$ 。权重形状为  $[N, T, L]$ ，使用glorot_uniform初始化方法以确保权重的有效性和稳定性。

下一步通过动态路由机制来处理输入特征：首先获取输入数据的批处理数量  $B$ ，将输入数据的维度扩展到三维，以便于后续计算。然后，使用K.tile函数复制扩展后的输入，使其适应每个胶囊的数量，最终形状为  $[B, N, T, 1]$ 。

然后对输入特征的加权计算，使胶囊层能够生成更具区分性的特征向量：通过K.map_fn函数对每个扩展后的输入进行加权计算，使用K.batch_dot函数进行批量点乘，从而生成了每个

胶囊的预测输出，形状为  $[B,N,1,L]$

动态路由：初始化路由权重  $\pmb{b}$  ，其形状为  $[B$ $N,1,1]$  。然后进行动态路由，通过循环实现动态调整。在每次迭代中，使用K.softmax函数计算路由权重  $\pmb{c}$  ，并利用加权和K.sum计算输出。如果当前迭代不是最后一次，则更新路由权重b。

最后BiGRU层提取时间序列特征并训练，通过双向处理，模型同时考虑前后文信息，从而增强对序列数据的理解：使用K.squeeze函数去除多余的维度，以便得到形状为[B，1，L]的输出，便于后续处理。最后，利对输出进行L2正则化，以确保输出向量的归一化，便于后续的处理。在此步骤中，使用双向封装器调用双向门控循环单元，设置隐藏单元数量，并指定返回每个时间步的输出。

# 3 实验验证

# 3.1 数据集

数据集包括7个直升机涡轮发动机的运行数据，所有发动机的品牌和型号相同。原始数据共分为训练集、验证集以及测试集三个部分，每个数据部分都设置相同的传感器来测量数据，验证集以及测试集分别有另外3台发动机的21437条特征数据。原始数据集中的验证集和测试集不包含目标值数据，只有特征数据，因此不能进行验证以及测试；此处沿用了原始数据集中的验证集以及测试集名称，但其不同于一般机器学习中的验证机和测试集。训练集包含742624条特征数据以及目标值数据，可将其拆分并用于模型验证。

数据集描述具体可见表1，训练集的特征数据是7个传感器在其中4个发动机的测量数据，目标值数据分为两部分：第一部分是故障目标值，取值为0或1，分别代表无故障和有故障；第二部分是扭矩裕度，两个部分需要分别进行分类以及预测。

表1故障数据集描述

Table 1 Description of fault dataset  

<table><tr><td>数据代码</td><td>测量值</td><td>数据类别</td><td>标准单位</td></tr><tr><td>1</td><td>外部空气温度</td><td>特征</td><td>℃</td></tr><tr><td>2</td><td>平均气体温度</td><td>特征</td><td>℃</td></tr></table>

<table><tr><td>3</td><td>可用功率</td><td>特征</td><td>kW</td></tr><tr><td>4</td><td>指示空速</td><td>特征</td><td>km/h</td></tr><tr><td>5</td><td>净功率</td><td>特征</td><td>kW</td></tr><tr><td>6</td><td>压缩机转速</td><td>特征</td><td>r/min</td></tr><tr><td>7</td><td>测量扭矩</td><td>特征</td><td>N*m</td></tr><tr><td>8</td><td>故障模式</td><td>目标值</td><td>/</td></tr><tr><td>9</td><td>扭矩裕度</td><td>目标值</td><td>%</td></tr></table>

本实验通过一台配备第11代IntelW- 2223CPU处理器的工作站进行，采用Python3.9版本的编程语言，模型框架使用TensorFlow2.1构建。

# 3.2 故障诊断

首先用训练集数据验证模型，将原始训练集分为模型训练集及模型测试集，对7种特征数据进行归一化处理，将故障模式作为目标值数据进行独热编码，然后将数据重塑成三维数组输入到网络中进行训练。模型相关的参数设置如表2所示：

表2 模型参数设置

Table 2 Model parameter settings  

<table><tr><td>参数名称</td><td>设定值</td><td>参数名称</td><td>设定值</td></tr><tr><td>通道特征维度</td><td>16</td><td>批处理数量</td><td>512</td></tr><tr><td>动态路由次数</td><td>7</td><td>迭代次数</td><td>200</td></tr><tr><td>胶囊数量</td><td>6</td><td>测试集占比</td><td>0.15</td></tr><tr><td>胶囊维度</td><td>8</td><td>验证集占比</td><td>0.15</td></tr><tr><td>BiGRU层隐藏层数</td><td>2</td><td>优化器</td><td>Adam</td></tr><tr><td>BiGRU层隐含层单元数</td><td>1024</td><td>数据输入格式</td><td>3维数组</td></tr><tr><td>全连接层维度</td><td>2/512</td><td>损失函数</td><td>交叉熵损失函数</td></tr><tr><td>全连接层输出激活函数</td><td>Softmax</td><td>Dropout</td><td>0.4</td></tr></table>

模型采用交叉损失函数来计算输出和真值之间的差值，通过反向传播更新模型参数。对于单个样本，样本在第i类上的真实标签值为  $y_{i}$  模型对于样本预测属于第i类的概率值为  $y_{i}$  ，分类总数为C，则交叉损失函数  $L$  如下式所示。

$$
L = -\sum_{\mathrm{i}}^{\mathrm{C}}y_{i}\log (y_{i}) \tag{1}
$$

通过不断的训练，模型逐渐获得生成近似结果的能力，训练损失与准确率的变化如图2所示。大约150次迭代后对直升机发动机故障的诊断准确率分类达到  $99.7\%$  以上，Caps- BiGRU- Attention模型在训练和测试阶段表现出良好的收敛性，同时在图3的混淆矩阵中可看出模型测试集上分类的具体结果以及模型优秀的泛化性能；在111396个样本中，仅有371个被错误诊断，其中228个是虚警，143属于漏检，相对而言一定程度的虚警是可以接受的。通过画出接收者操作特征曲线（Receiver Operating Characteristic Curve，ROC）并计算曲线下面积（Area Under Curve，AUC）的值，AUC接近1，且ROC曲线整体接近坐标轴，表明模型对特征数据具有强大的学习能力。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/888e735bc59071217bd443a5a27cfd6699a5217005168208583787b7157086b2.jpg)  
图2 故障诊断模型训练迭代图

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/264bf198a1635f65a50d34bcd7aaabba306f9e972d844ea6b89a374230f7fa67.jpg)  
Fig.2 Training iteration diagram of the fault diagnosis model

图4展示了模型对诊断错误样本的置信度。置信度表示模型对结果的信任程度，由输出层的Softmax函数给出。尽管模型在某些样本上表现出错误，但较低的置信度显示了模型更好的泛化性能，而较高的置信度可能会对模型在其他应用

中的表现产生不利影响。图中随机选取了300个错诊断样本，结果显示置信度主要集中在0.5到0.8之间。这表明模型在处理这些模糊样本时存在犹豫，虽然分类错误，但对这些样本保持了一定程度的警惕。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/c62b70041b809c00c3e6d1b737826a4ad7b62984b6190c3a2473cfc8cfb670dc.jpg)  
图4 Caps-BiGRU-Attention模型错分类样本置信区间 Fig.4 Confidence interval of misclassified samples for the Caps-BiGRU-Attention model

# 3.3 扭矩裕度预测

同样的，将扭矩裕度作为目标值输入到模型中进行预测，无需对其进行独热编码，但需要进行归一化处理，并且将损失函数替换为均方误差，输出层神经元个数也由2提升到512。为了提升模型性能，在进行扭矩裕度预测时，将故障状态也作为输入特征以提取更多信息。因此，输入层的特征数量由7个增加到8个。模型采用均方误差（Mean Squared Error，MSE）作为损失函数，表达式式2所示，其中  $N$  为样本数量，  $t_i$  为真实值，  $t_i$  为模型预测值。

$$
MSE = \frac{1}{N}\sum_{i = 1}^{N}(t_i - t_i)^2 \tag{2}
$$

通过反向传播更新模型参数，图5为模型训练时的损失值以及均方根误差变化情况；在经过150迭代后误差基本稳定。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/49a4da8d108796a7e63f8c9de689d7a77813c04e9bcd7071e75695265621131d.jpg)  
Fig.3 Confusion matrix for engine fault diagnosis

# 图5扭矩裕度预测模型训练迭代图

Fig.5 Training iteration variation diagram of the torque margin prediction model

图6展示了模型在测试集上的预测表现，表征了模型预测的不确定性程度，选取了最后几个点的真实值、预测值及其误差区间，图中预测值都处于真实值1倍标准差以内，表明在多数领域内将模型预测值替代真实值用于分析将不会产生较大影响。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/aebd85c256000fc5675768ec331c4ede002bd268d206cd059260107a0a9ae49d.jpg)  
图6模型测试集部分预测值与真实值误差区间对比 Fig.6 Comparison of error intervals between predicted values and true values in the algorithm test set

表3通过引入其他网络模型和模型来对比本模型在故障诊断以及扭矩裕度预测的效果。对模

型及对比模型分别在进行十次实验，并取中值记录。对分类以及预测分别采用了不同的指标。本文分别实验了Caps- BiGRU- Attention、CNN- BiGRU- Attention、CNN- BiLstm、CNN- BiGRU以及RandomForest模型在同样的数据集上进行了比较。在故障诊断中Caps- BiGRU- Attention准确率超过了  $99.7\%$  ，相较于机器学习模型提升了 $6\%$  ，胶囊网络在提取特征方面由于CNN网络，提升了  $3\%$  的模型性能；总的来说，模型实现了更高的召回率，精度和F1分数。在扭矩裕度的预测中模型的均方误差只有0.0014，平均绝对百分比误差小于  $4\%$  ，相对于机器学习模型提高了 $23\%$  的平均绝对百分比误差。总的来说，Caps- BiGRU- Attention通过赋予输入特征不同的权重，注意力机制提高了模型对复杂数据的拟合能力，使模型能够自动学习并关注输入数据中最相关的部分。胶囊网络提取了内在的空间关联信息，这种自动聚焦能力结合强大的特征提取能力提升了模型对数据的表达能力，从而使其能够更准确地捕捉数据中的模式和规律。

表3多模型性能指标对比

Table 3 Comparison table of performance metrics for multiple models  

<table><tr><td>领域</td><td>模型</td><td>准确率</td><td>精确率</td><td>召回率</td><td>F1</td><td>MCC</td></tr><tr><td rowspan="5">故障状态
诊断</td><td>Caps-BiGRU-Attention</td><td>0.997</td><td>0.9968</td><td>0.9969</td><td>0.9969</td><td>0.9938</td></tr><tr><td>CNN-BiGRU-Attention</td><td>0.9681</td><td>0.9682</td><td>0.9653</td><td>0.9667</td><td>0.9336</td></tr><tr><td>CNN-BiLstm</td><td>0.9543</td><td>0.9550</td><td>0.9498</td><td>0.9522</td><td>0.9048</td></tr><tr><td>CNN-BiGRU</td><td>0.9528</td><td>0.9540</td><td>0.9477</td><td>0.9506</td><td>0.9017</td></tr><tr><td>Random Forest</td><td>0.9367</td><td>0.9312</td><td>0.9417</td><td>0.9351</td><td>0.8729</td></tr><tr><td rowspan="3">评价指标</td><td>模型</td><td>均方误差</td><td>均方根误差</td><td>平均绝对误差</td><td>平均绝对百分比误差</td><td>决定系数</td></tr><tr><td>Caps-BiGRU-Attention</td><td>0.0014</td><td>0.0376</td><td>0.0271</td><td>3.9572</td><td>99.9992</td></tr><tr><td>CNN-BiGRU-Attention</td><td>0.0096</td><td>0.0982</td><td>0.0685</td><td>6.8093</td><td>99.9952</td></tr><tr><td rowspan="3">扭矩裕度
预测</td><td>CNN-BiGRU</td><td>0.0104</td><td>0.1024</td><td>0.0688</td><td>20.6641</td><td>99.9947</td></tr><tr><td>CNN-BiLstm</td><td>0.0404</td><td>0.2010</td><td>0.1488</td><td>23.6817</td><td>99.9800</td></tr><tr><td>Random Forest</td><td>0.0704</td><td>0.2653</td><td>0.2457</td><td>29.89</td><td>99.8584</td></tr></table>

状态的关联性，引入了SHAP（SHapley AdditiveexPlanations）模型来进行分析。SHAP值计算方式见下式：

# 4直升机涡轮发动机健康管理

# 4.1 SHAP特征分析

为了研究温度、空速等参数与故障以及健康

$$
\phi_{i}(f) = \sum_{S\in N\backslash \{i\}}\frac{|S|!}{|N|}\bullet (|N| - |S| - 1)\bullet [f(S\cup \{i\}) - f(S)] \tag{3}
$$

其中  $N$  是所有特征的集合，  $S$  是不包含特征  $i$  的特征子集，  $\phi_i(f)$  是特征  $i$  的 SHAP 值，  $f(s)$  是模型在给定特征子集 S 时的预测输出。

图 7- 8 分别是使用 Random Forest 模型进行故障状态以及扭矩裕度预测过程的 SHAP 特征摘要图。图中的横坐标表示 SHAP 值，不同特征的 SHAP 值分布在中间的基准线两侧。摘要图纵轴根据特征的平均绝对 SHAP 值排序，越重要的特征越靠上。

左侧区域代表影响因素对结果产生负向影响，使模型预测值减小，而右侧区域代表影响因素对结果产生正向影响，从而增大预测值[23]。在故障诊断时，预测值为故障代码，越大代表越接近 1，故障概率越高；在扭矩裕度预测中，预测值为扭矩裕度，越大则表示发动机健康状况越好。征值从蓝色渐变至红色，表示自变量的数值逐渐增大。

图 7 为故障诊断特征摘要图，可以看出外部空气温度、平均气体温度、测量扭矩在特征中最靠上，对故障模式的影响也最大；由于外部空气温度、测量扭矩取值变蓝时，贡献值集中在基准线左侧，也就是这些特征取值在增大时，会使模型的输出降低，也就是趋近于 0，发生故障的概率变低。另一方面，平均气体温度则与之相反。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/5896e81475af451a04151a885f426e5813642b1d96faca4ce70573e832b130db.jpg)  
图7 故障诊断特征摘要图

Fig.7 SHAP feature summary plot of fault diagnosis model图 8 中表示在扭矩裕度预测时故障模式是最

重要的特征，故障的发生会使扭矩裕度降低；故障特征红蓝数据完全分布在左右两侧，显示了故障模式发生时和健康状态会受到很大影响。空速、压缩机转速、可用功率以及平均气体温度等指标也会线性影响扭矩裕度，其值越小，扭矩裕度越大，这与发动机的设计有关，而测量扭矩和外部气体温度的增加则会降低扭矩裕度，更高的输出扭矩显然不利于发动机的健康运转。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/12662eae8d7188ed0f1a32a678f35b7183eaf7955c129afb2eef49abb1fba725.jpg)  
图8扭矩裕度预测特征摘要图 Fig.8 SHAP feature summary plot of torque margin prediction model

图 9 展示了不同温度下的各特征表现。根据外部空气温度是否低于 0 摄氏度，将数据分两部分，分别计算 SHAP 值并进行比较。图中可看出不同的温度下各个特征的贡献差异很大，低温情况下指示空速、可用功率的贡献值对扭矩裕度的影响差异很大，并且这种情况下，故障模式的影响最高，低温下情况压缩机转速以及可用功率对扭矩裕度的影响则变的非常小。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/428cf04016ea562ccbc833db60492bb2dc23f9e64f3e3f9cf33929de83837ae2.jpg)  
图9扭矩裕度预测模型特征贡献值随平均气体温度范围变化图

Fig.9 Variation diagram of SHAP values of the of torque margin prediction model with respect to the average gas temperature range

图 10- 13 展示了特征的具体取值对模型的影响，图表横轴显示特征效率因子的不同取值，纵轴显示该特征的 SHAP 值。图 10 中可以发现在故障诊断中以及故障预测中，净功率在 100kW 前后有完全不同的趋势，净功率提升到接近 100kW 时模型输出趋向于下降，也就是无故障状态，但当超过 100kW 后会急剧提高。图 11 也表明净功率提升到接近 100kW 时，预测模型会输出更好的扭矩裕度，但超过 100kW 后急速下降，表明发动机受到了一定程度的健康损害。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/64b40342caf56949bce9cb9b98b5fc135c773b5588ee111eb8389ab4815903ae.jpg)  
图10 故障诊断模型净功率特征散点图

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/072b4310e0f30f143a7f07c22f3c6c56bff7fdd30786e7ae3bbc0ce64c65abc5.jpg)  
Fig.10 Scatter plot of net power in the fault diagnosis model  
图11 扭矩裕度预测模型净功率特征散点图 Fig.11 Scatter plot of net power in the torque margin prediction model 图12 扭矩裕度预测模型外部空气温度特征散点图 Fig.12 Scatter plot of air temperature in the torque margin prediction model

图12揭示了外部空气温度的高低和扭矩裕度的正相关性，并且在整个取值范围内都存在正相关性，说明越高的温度越对健康保障有利。图13表明指示空速越大扭矩裕度越小，特别是达到 $110\mathrm{km / h}$  后，扭矩急剧下降，显然不利于对发动机的健康运行。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/2bfe92fbd5014eb1fc13ab560a6e3bccd5e054d43ca58cfc093802fc2034e56c.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/338e77e696a26f599eccfa2a58510011ca64329cbfa00ca776077d4dd86bb6f4.jpg)  
图13 扭矩裕度预测模型指示空速特征散点图 Fig.13 Scatter plot of IAS in the torque margin prediction model

总体而言，外部空气温度、平均气体温度、以及测量扭矩对直升机涡轮发动机的故障模式和健康状态都有很大影响，故障模式也是健康状态的最大影响因素。较高的外部空气温度、测量扭矩和压缩机转速，以及较低的平均气体温度，会降低故障概率。而较低的平均气体温度、可用功率、压缩机转速和指示空速，以及较高的外部空气温度、测量扭矩和净功率，则有助于提升发动机的扭矩裕度。

净功率提升到接近100kW时最有利于其健康状态，超过  $100\mathrm{kW}$  后对发动机产生不利影响；越高的外部温度下运行发动机越好，在  $0\mathrm{- }100\mathrm{km / h}$  的速度范围运行对发动机有良好的保护作用，指示空速超过  $110\mathrm{km / h}$  会损害发动机，原因可能是增加的气动负荷和潜在的过热风险达到了警戒值。最后，同时，测量扭矩和平均气体温度有一定的相关性，这种相关性可能在提取特征是产生干扰。故障诊断错误时没有特殊的特征作用，但测量扭矩可能是导致预测误差的关键因素。

# 4.2 扭矩裕度概率密度分布拟合

不同的运行条件下发动机的目标扭矩是变化的，扭矩裕度  $t_m$  由下式给出，其中，  $T_{m}$  和 $M_{m}$  表示目标扭矩以及测量扭矩。从式4可看出扭矩裕度取决于目标扭矩以及测量扭矩，扭矩裕度从侧面反映了发动机的效能[24]，文章尝试通过扭矩裕度来判断健康状态，但有效的判断需要结合对扭矩裕度与健康状态之间关系的先验知识。

$$
t_{m} = (M_{m} - T_{m}) / T_{m} \tag{4}
$$

通过拟合扭矩裕度的概率密度分布，可以了

解其与健康状态之间的关系[25]，并使用K- S（Kolmogorov- Smirnov）检验以及Akaike信息准则值（Akaike Information Criterion，AIC）来判断分布是否合适，p值是检验统计量在零假设成立的条件下达到或超过观察值的概率。它表示观察到的样本与理论分布之间的差异在多大程度上可以归因于随机性，本文中设定显著性水平为0.05，若p值大于0.05则可认为服从此分布。AIC值越小，模型的拟合优度与复杂度之间的权衡越好。因此，在比较多个模型时，AIC值较小的模型通常被认为是更优的。模型在扭矩裕度预测中的表现已被验证，因此使用模型对验证集和测试的数据进行预测，得到验证集数据的故障模式、目标扭矩以及扭矩裕度。图14是验证集的目标扭矩和扭矩裕度的分布箱图，数据分布显示了多个峰值。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/65ff0864c001421775f3e9d653d11a40429b7f7822dc34ecc152af896cfe473f.jpg)  
图14验证集目标扭矩和扭矩裕度箱图 Fig.14 Box plot of target torque and torque margin for the validation set

首先使用极大似然估计对验证集的扭矩裕度尝试多种分布的参数估计；包括正态分布、指数分布、均匀分布、伽马分布、贝塔分布、对数正态分布、卡方分布、最小威布尔分布、t分布、F分布、柯西分布、拉普拉斯分布、瑞利分布、帕累托分布、右偏Gumbel分布、logistic分布、爱尔兰分布、幂律分布、中村分布以及贝塔素数分布[26]。对以上分布分别进行K- S检验并计算p值，所有拟合分布的p值均远小于0.05的显著性水平，表明这些分布与观察到的数据有显著差异。

从图14的数据分布图以及对常见分布的拟合结果来看，数据分布可能接近混合模型或者其他未知分布。混合高斯密度模型是常见的混合模型，接下来尝试拟合混合高斯密度模型。图15是不同组分数下的混合高斯密度模型对验证及扭矩裕度的拟合情况，在图中，当组分数达到10

时，p值接近0.4，明显高于显著性水平0.05，表明模型与观察数据之间的拟合效果较好，AIC值也有了显著的降低。组分数继续增大，虽然p值会波动提高，但AIC值已经不会有太大变化，模型产生了过拟合，且由于组分数过多也难以明确具体的对应关系，生成的具体健康管理方案也会越加复杂。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/b3a420bdd267a608315e9e05b6b7d3e377f8c290f3c490c74b82973703135b71.jpg)  
图15p值及AIC值随混合高斯密度函数组分数变化图 Fig.15 Variation of p-values and AIC values with the number of components in the mixed Gaussian density functions

图16为组分数为10时混合高斯密度模型拟合的QQ图（Quantile- Quantile Plot），用于比较样本分布与理论分布之间的关系，蓝色点表示样本分布的分位数与理论分位数的关系；红色线表示理论分布的期望线。蓝色点基本保持在期望线附近，表示拟合程度良好，但是在某些扭矩裕度值附近（例如取值为- 10以及25时）有些许偏离。图17为组分数为10时混合高斯密度模型与实际数据分布对比图，也支持了上述结论。但从中可以看出不同的数据区间的表现形式不同，可能分属不同的分布。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/f109591e7ffff0fbc3c2cf6d8bc7b1126e2706bc707afb0bb02be5f564d2dd2a.jpg)  
图16混合高斯密度函数拟合QQ图 Fig.16 Quantile-Quantile Plot of mixed Gaussian density function fitting

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/23c285e31105d7e37c871b1f6e2857995bce023468ffe7d34e3a3019297980f1.jpg)  
图17 混合高斯密度函数拟合数据图

Fig.17 Fitting data plot of mixed Gaussian density function

显然，扭矩裕度越大代表着发动机的状况越好，那么不同状态的也就是不同扭矩裕度范围内可能分属于不同的分布，或者相同分布的不同参数。将直升机涡轮发动机的健康状态分为四个等级：严重失效、轻微失效、衰减状态和健康状态。可依次对应验证集和测试集的四个数据区间，实验过程中尝试了上百种数据的分割方式，最终将扭矩裕度分为了4个部分对应发动机四种健康状态，分别拟合后可产生最优的分布拟合。

观察图17，可选取三个扭矩裕度分割点将数据分为4个部分，并使用极大似然估计分别拟合上文的20种概率分布，由于箱数的大小也会影响分布，所以采用了粒子群优化方法在2- 100中寻找最优箱数，目标函数是使p值最大。

图18是验证集划分后数据分布拟合结果，子图中显示了在这四个区间p值最大的三种分布曲线以及原始数据。同理，图19是测试集的数据分布拟合。

表4汇总了每段分割数据的区间以及拟合的三个最优分布，并提供了其p值和AIC值来评估其拟合情况。可以看出验证集和测试集在严重失效、轻微失效以及健康状态的数据区间内都找到了合适的分布，箱数也都接近，但衰减状态的数据难以拟合。

在严重失效、轻微失效和健康状态下，虽然贝塔分布不总是拥有最高的p值，但通常是适合的选择，除了测试集数据的第1部分数据外，p值都大于显著性水平且AIC值最低，过多的分布会提升健康管理方案的复杂度，因此将贝塔分布作为以上数据区间的最优分布，在表4的最后一列记录了最优分布的参数，包括贝塔分布（形状参数α，形状参数β，位置参数loc，尺度参数scale）以及Logistic分布（位置参数loc，尺度参数scale）。

验证集和测试集的第3部分数据也就是衰减状态数据始终难以拟合，推测衰减状态的数据集中在0附近，且衰减过程复杂多变，导致难以拟合，或者是属于某种未知分布。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/241afe4e07a157bed843bb8a348f5369493b225fa768c34ccb73b1caa9f6ea89.jpg)  
图18 验证集扭矩裕度分段后概率密度函数拟合图

Fig.18 Fitted probability density function plot of segmented torque margin for the validation set

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/a7dedd00-78a4-4f47-b9da-fa911727156c/a1095df7f397fc8e5f3cdc690b3e9ff799a6db3065c6308c6602c5250b214daf.jpg)  
图19 测试集扭矩裕度分段后概率密度函数拟合图 Fig.19 Fitted probability density function plot of segmented torque margin for the test set

表4扭矩裕度分段后概率密度函数拟合参数表

Table 4 Table of fitting parameters for the probability density function of segmented torque margin  

<table><tr><td>数据集</td><td>目标裕度范围</td><td>p值</td><td>分布</td><td>箱数</td><td>AIC值</td><td>分布函数参数值</td></tr><tr><td rowspan="16">验证集</td><td rowspan="4">(-∞,-8]</td><td>0.999</td><td>正态分布</td><td>20</td><td>1143.93</td><td>\</td></tr><tr><td>0.945</td><td>伽马分布</td><td>15</td><td>1164.29</td><td>\</td></tr><tr><td>0.916</td><td>贝塔分布</td><td>20</td><td>1130.30</td><td>(5492493.3, 40.6, -618299.3, 618294.0</td></tr><tr><td>0.175</td><td>贝塔分布</td><td>19</td><td>18439.20</td><td>(3.8, 2.6, -8.5, 5.7)</td></tr><tr><td rowspan="2">(-8,-3]</td><td>0.127</td><td>最小威布尔分布</td><td>31</td><td>18571.63</td><td>\</td></tr><tr><td>0.117</td><td>正态分布</td><td>36</td><td>18697.90</td><td>\</td></tr><tr><td rowspan="3">(-3,16]</td><td>0</td><td>最小威布尔分布</td><td>32</td><td>67470.56</td><td>\</td></tr><tr><td>0</td><td>贝塔分布</td><td>10</td><td>66762.50</td><td>\</td></tr><tr><td>0</td><td>t分布</td><td>43</td><td>69269.38</td><td>\</td></tr><tr><td rowspan="3">(16, +∞]</td><td>0.988</td><td>贝塔分布</td><td>47</td><td>6750.68</td><td>(1.0, 11.1, 16.0, 24.0)</td></tr><tr><td>0.876</td><td>最小威布尔分布</td><td>16</td><td>6754.50</td><td>\</td></tr><tr><td>0.809</td><td>伽马分布</td><td>48</td><td>6763.17</td><td>\</td></tr><tr><td rowspan="4">(-∞,-8]</td><td>0.793</td><td>logistic分布</td><td>31</td><td>1451.71</td><td>(9.2, 0.25)</td></tr><tr><td>0.62</td><td>拉普拉斯分布</td><td>30</td><td>1478.75</td><td>\</td></tr><tr><td>0.17</td><td>t分布</td><td>29</td><td>1459.30</td><td>\</td></tr><tr><td>0.473</td><td>最小威布尔分布</td><td>19</td><td>4738.22</td><td>\</td></tr><tr><td rowspan="5">测试集</td><td rowspan="2">(-8,-5]</td><td>0.13</td><td>贝塔分布</td><td>42</td><td>4657.68</td><td>(4.0, 1.8, -8.7, 3.7)</td></tr><tr><td>0.009</td><td>t分布</td><td>15</td><td>4996.706</td><td>\</td></tr><tr><td rowspan="3">(-5,20]</td><td>0</td><td>logistic分布</td><td>16</td><td>109707.694</td><td>\</td></tr><tr><td>0</td><td>正态分布</td><td>39</td><td>109342.603</td><td>\</td></tr><tr><td>0</td><td>t分布</td><td>37</td><td>109344.603</td><td>\</td></tr></table>

<table><tr><td></td><td>0.992</td><td>贝塔分布</td><td>46</td><td>1089.614</td><td>(1.2, 44.8, 20.0, 58.8)</td></tr><tr><td>(20, +∞]</td><td>0.962</td><td>指数分布</td><td>22</td><td>1092.213</td><td>\</td></tr><tr><td></td><td>0.962</td><td>伽马分布</td><td>47</td><td>1090.062</td><td>\</td></tr></table>

# 5总结

文章使用胶囊网络替代传统卷积网络用于提取特征，结合SE注意力机制以及BiGRU网络用于直升机发动机故障诊断及扭矩裕度预测并达到了良好的效果，利用SHAP量化了不同特征对于故障以及健康指标的影响程度，总结了有利于直升机涡轮发动机健康管理的环境条件以及运行环境，揭示了特征对于发动机故障和扭矩裕度的影响机理，最后针对验证集和测试集的扭矩裕度的分布进行了拟合，得到了最优分布贝塔分布以及涡轮发动机严重失效、轻微失效、衰减状态以及健康状态四种状态的区间，可用于维修方案设计以及健康管理。

后续将尝试寻找符合全寿命周期的概率密度函数分布，归纳衰减状态的故障规律，将概率密度函数结合深度学习模型来完善健康管理方案，并结合有限元分析方法、材料弹塑性理论以及热机耦合理论，建立面向直升机发动机健康管理的时变参数模型、结构失效模型和维修管理体系，揭示涡轮发动机失效的相互作用机理，为科学评估和预报涡轮发动机系统的服役性能提供方法与理论支撑。

# 参考文献：

[1]侯波，徐冠峰，闫慧娟，等.某型直升机主桨叶大梁断裂故障分析[J].航空动力学报.2023，38(6):1489- 1495. Hou Bo，X U. Guanfeng，Yan Hujuan, et al. Fracture fault analysis of main blades girder on a helicopter[J].Journal of Aerospace Power.2023,38(6):1489- 1495. (in Chinese) [2]Leoni J, Tanelli M, Palman A. A new comprehensive monitoring and diagnostic approach for early detection of mechanical degradation in helicopter transmission systems[J]. Expert Systems with Applications. 2022,210:118412. [3]Mironov A, Doronkin P. The Demonstrator of Structural Health Monitoring System of Helicopter Composite Blades[J]. Procedia Structural Integrity. 2022, 37: 241- 249. [4]万安平，龚志鹏，王景霖，等.多工况直升机附

件齿轮箱振动故障诊断[J].振动、测试与诊断.2024， 44(2):246- 252.

Wan Anping，Gong Zhipeng，Wang Jinglin, et al. Vibration Fault Diagnosis of Helicopter Accessory Gearbox Under Multi- operating Conditions[J]. Journal of Vibration. Measurement & Diagnosis.2024,44(2): 246- 252. (in Chinese) [5] Sun K, Yin A, Lu S. Domain distribution variation learning via adversarial adaption for helicopter transmission system fault diagnosis[J]. Mechanical Systems and Signal Processing.2024,215:111419. [6]Mironov A, Doronkin P, Priklonsky A, et al. The Role of Advanced Technologies of Vibration Diagnostics to Provide Efficiency of Helicopter Life Cycle[J]. Procedia Engineering.2017,178:96- 106. [7]Ouyang L, Jin N, Bai L, et al. Soft measurement of oil - water two- phase flow using a multi- task sequence- based CapsNet[J]. ISA Transactions.2023,137:629- 645. [8]Moudgil A, Singh S, Rani S, et al. Deep learning for ancient scripts recognition: A CapsNet- LSTM based approach[J]. Alexandria Engineering Journal.2024,103:169- 179. [9]Li X, Jiang H, Liu Y, et al. An integrated deep multiscale feature fusion network for aeroengine remaining useful life prediction with multisensor data[J]. Knowledge- Based Systems.2022,235:107652. [10]Lyu F, Liu J, Chen L, et al. 3D in- situ stress prediction for shale reservoirs based on the CapsNet- BiLSTM hybrid model[J]. International Journal of Rock Mechanics and Mining Sciences.2024,183:105937.

[11]Nizarudeen S, Shanmughavel G R. Comparative analysis of ResNet, ResNet- SE, and attention- based RaNet for hemorrhage classification in CT images using deep learning[J]. Biomedical Signal Processing and Control.2024,88:105672.

[12]管智峰.基于特征优选和ESPBO- HKELM的变压器故障诊断研究[D].阜新：辽宁工程技术大学，2023.

Zhi Feng Guan. Research on Transformer Fault Diagnosis Based on Feature Selection and ESPBO- HKELM. Fuxin: Liaoning Technical University, 2023. (in Chinese) [13]Wen H, Liu B, Di M, et al. A SHAP- enhanced XGBoost model for interpretable prediction of coseismic landslides[J]. Advances in Space Research. 2024, 74(8):3826- 3854.

[14] Lu Y, Tang L, Liu Z, et al. Unsupervised quantitative structural damage identification method based on BiLSTM networks and probability distribution model[J]. Journal of Sound and Vibration. 2024, 590:118597.

[15]张雄，张逸轩，张明，等.基于小波包散布熵与Meanshift概率密度估计的轴承故障识别方法研究[J].湖南大学学报（自然科学版）.2021，48(8)：

133- 140.

Zhang Xiong, Zhang Yixuan, Zhang Ming, et al. Research on Bearing Fault Identification Method Based on Wavelet Packet Dispersion Entropy and Meanshift Probability Density Estimation[J]. Journal of Hunan University(Natural Sciences). 2021, 48(8): 133- 140. (in Chinese)

[16] Zhang G, Wang Y, Li X, et al. Health indicator based on signal probability distribution measures for machinery condition monitoring[J]. Mechanical Systems and Signal Processing. 2023, 108: 110460.

[17] Zhang S, Liang W, Zhao W, et al. Electro hydraulic SBW fault diagnosis method based on novel 1DCNN- LSTM with attention mechanisms and transfer learning[J]. Mechanical Systems and Signal Processing. 2024, 220: 111644.

[18] Chen R, Shen H, Zhao Z, et al. Global routing between capsules[J]. Pattern Recognition. 2024, 148: 110142.

[19] Zhang T, Jia J, Chen C, et al. BiGRUD- SA: Protein S- sulfenylation sites prediction based on BiGRU and self- attention[J]. Computers in Biology and Medicine. 2023, 163: 107145.

[20] Saad Shakeel M. CAAM: A calibrated augmented attention module for masked face recognition[J]. Journal of Visual Communication and Image Representation. 2024, 104: 104315.

[21] Zhou G, Hu G, Zhang D, et al. A novel algorithm system for wind power prediction based on RANSAC data screening and Seq2Seq- Attention- BiGRU model[J]. Energy. 2023, 283: 128986.

[22] Ye M, Li L, Yoo D, et al. Prediction of shear strength in UHPC beams using machine learning- based models and SHAP interpretation[J]. Construction and Building Materials. 2023, 408: 133752.

[23] Kashifi M T. Investigating two- wheelers risk factors for severe crashes using an interpretable machine learning approach and SHAP analysis[J]. IATSS Research. 2023, 47(3): 357- 371.

[24] Serafini J, Bernardini G, Porcelli R, et al. In- flight health monitoring of helicopter blades via differential analysis[J]. Aerospace Science and Technology. 2019, 88: 436- 443.

[25] Lin Z, Cai Y, Liu W, et al. Estimating the state of health of lithium- ion batteries based on a probability density function[J]. International Journal of Electrochemical Science. 2023, 18(6): 100137.

[26] 吴涵, 袁越, 侯语涵, 等. 配电网理论线损概率分布函数的计算与分析[J]. 中国电机工程学报. 2024, 44(16): 6444- 6454.

W. 
U. Han, Yuan Yue, Hou Yuhan, et al. Computation and Analysis of Theoretic Line Loss Probability Distribution Function of Distribution Network[J]. Proceedings of the CSEE. 2024, 44(16): 6444-6454. (in Chinese)