# 基于GA-AANN神经网络的SDQ算法的航空发动机传感器数据预处理

吕升，郭迎清，孙浩

（西北工业大学动力与能源学院，陕西西安710129）

摘要：为实现对输入健康管理系统的航空发动机传感器数据进行数据鉴定、故障诊断以及去除噪声信号干扰，提出了一种航空发动机传感器数据预处理方法。针对双通道传感器航空涡扇发动机，搭建了以合理性检验模块和解析冗余检验模块为主要内容的SDQ算法模型，利用遗传算法优化的AANN神经网络实现传感器的解析冗余检验。采用蒙特卡罗仿真方法，将改进的SDQ算法与一种基于最小二乘法的SDQ算法进行对比仿真验证。结果表明，本文提出的SDQ算法在发动机稳态条件下对阶跃故障和漂移故障隔离的平均正确率分别提高了  $1.7\%$  和  $19.1\%$  ，在发动机动态条件下对阶跃故障和漂移故障隔离的平均正确率分别提高了  $12.5\%$  和  $33.8\%$  。且在多传感器故障诊断和除噪方面性能优异，处理后的传感器信号平均信噪比提高了8.27dB。

关键词：航空发动机传感器；故障诊断；SDQ算法；遗传算法；AANN神经网络  中图分类号：V233.7 文献标识码：A 文章编号：1001- 4055（2018）05- 1142- 09  DOI：10.13675/j.cnki.tjjs.2018.05.022

# Aero-Engine Sensor Data Preprocessing Based on SDQ Algorithm of GA-AANN Neural Network

LV Sheng，GUO Ying- qing，SUN Hao

(School of Power and Energy，Northwestern Polytechnical University，Xi'an 710129，China)

Abstract：In order to realize the data identification，fault diagnosis and noise interference of the aero- engine sensor data of the input health management system，a method of aero- engine sensor data preprocessing was proposed.Aiming at the air turbofan engine of dual- channel sensor，a SDQ algorithm model with reasonableness checks module and analytical redundancy checks module as the main content was established，and the AANN neural network optimized by genetic algorithm was used to realize the analytical redundancy checks of the sensor. The improved SDQ algorithm was compared with a SDQ algorithm based on the least squares method using the Monte Carlo simulation method. The simulation results prove that the average correct rate of step fault and drift fault isolation of the improved SDQ algorithm increased by  $1.7\%$  and  $19.1\%$  respectively when the engine in steady states，and the average correct rate of step fault and drift fault isolation of the improved SDQ algorithm increased by  $12.5\%$  and  $33.8\%$  respectively when the engine in dynamic states.The algorithm also has excellent performance in multi- sensor fault diagnosis and noise reduction，and the average signal- to- noise ratio of the processed sensor signal increased by 8.27dB.

Key words：Aero- engine sensor；Fault diagnosis；SDQ algorithm；Genetic algorithm；AANN neural network

# 1引言

航空发动机传感器数据的鉴定是健康管理系统中非常重要的一部分，是实现发动机故障诊断和控制的基础。其确保制定决策所依据的数据能够真实地反映发动机工况，实现准确的控制和性能预测。

国内外对基于传感器数据的故障诊断做了大量研究。常见方法可分为三类：基于数据、基于模型和基于知识的传感器故障诊断，其中前两种方法研究最为广泛。基于数据的传感器故障诊断方法通常利用神经网络，将传感器在正常和故障状态下的样本进行训练，运行时以传感器各状态量为输入生成故障向量，达到诊断的目的；而基于模型的传感器故障诊断方法是建立包含传感器状态的航空发动机模型，通过观测器或滤波器估计传感器状态进行故障诊断。国内叶志峰等将BP神经网络引入传感器故障诊断[2]，但构建的网络结构简单，效果不稳定，存在较多的误诊和漏诊现象；张书刚等采用卡尔曼滤波器进行传感器故障诊断[3]，但该方法受限于发动机模型精度，当数据受到干扰或偏置时，诊断精度会大大降低。

国外NASA格林研究中心提出了一种SensorData Qualification（SDQ）算法[45]，已逐渐成为传感器数据鉴定和故障诊断领域的热点研究内容。该算法依据构建的传感器网络，来确定其中各传感器的状态，实现传感器的故障诊断和隔离。在网络中，各成员传感器之间的相互关系是确定的，一旦发现不满足网络的关系，对应的传感器将会被识别。经过一段时间的持续性检验，仍被检测出错误关系的传感器将会被标记为故障传感器，并从网络中移除。搭建传感器的解析冗余网络，是SDQ算法的核心内容。

自联想神经网络（Auto- associative neural network，AANN）在处理线性相关以及非线性相关的数据变量的关系方面性能优异，也可以实现数据筛选任务，如降低噪声。而遗传算法(GA)在非线性寻优问题中有良好的表现[6]，可将这两种算法相结合实现传感器网络的构建。

本文以双通道传感器的航空涡扇发动机为研究对象，将AANN神经网络与GA相结合，提出了一种基于GA优化AANN神经网络的SDQ算法，期望利用大量的航空发动机传感器历史数据作为先验知识，快速构造一种高精度、高可靠性、高稳定度的传感器解析冗余网络以实现传感器故障诊断和定位。

# 2 SDQ算法介绍

SDQ算法是在某些关键的传感器数据用于制定发动机故障诊断、控制以及其他功能决策之前，对接收到的该传感器数据进行验证和整合。运用SDQ算法的一般化数据流如图1所示。其中，SDQ算法是由多层系统组成，包括合理性检验（Reasonableness Checks）、解析冗余检验（Analytical Redundancy Checks）以及最小化虚警率的附加逻辑（持续性检验（Persistency Checks））和数据确认及合并子系统（Qualification and Consolidation）。

# 2.1 合理性检验

合理性检验用于识别明显故障，本文采用范围检验和速率检验来诊断此类故障。范围检验主要针对传感器的硬故障，速率检验主要针对小幅阶跃变化的传感器故障，以及间歇性传感器故障信号。

# 2.2 解析冗余检验

解析冗余检验旨在识别小量级和慢速退化的传感器故障，是SDQ算法中的核心部分。当传感器无

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/f6542900-5f51-4185-854f-1b62f0dfe01d/5e30d66c0c87288e9db2c86207c8558380b0e9c8e3b77fabe6870f9dc8acbdce.jpg)  
Fig.1 SDQ algorithm generalized data flow

故障时，各传感器满足对应的网络关系；当传感器发生故障时，可以通过评估被违反的网络关系来确定故障传感器。

解析冗余检验的第一步是冗余通道检验，即确定两个物理冗余传感器（通道A和B）是否匹配，如式（1）

$$
\left|i_{\mathrm{A}} - i_{\mathrm{B}}\right|\leqslant r_{\mathrm{rec}} \tag{1}
$$

式中  $r_{\mathrm{rec}}$  是传感器  $i$  的冗余通道检验限制值。如果式（1）成立，证明冗余传感器一致，则不需要进一步的运算；如果式（1）不成立，则需要对传感器  $i$  与网络中其他传感器之间的关系做进一步地评估，进行解析冗余检验的第二步，即传感器的解析网络检验。

传统SDQ算法中，将传感器按类分组，相关的传感器放到同一个网络中，如风扇转速和高压压气机转速，利用多组数据拟合得到相关传感器的近似线性关系，构成传感器冗余网络，用于解析网络检验。但该方法无法构建存在单一类型的传感器的网络，且忽略了不同类型传感器间的相互影响，网络精度不高，可靠性低。

# 2.3 AANN神经网络

AANN神经网络是一种前馈神经网络，通过使用反向传播训练或类似技术捕获输入- 输出关系。AANN神经网络共包含3个隐含层，其中瓶颈层是最重要的隐含层，其将输入数据压缩成一组新的较低维数的不相关的变量，使数据尽可能被简洁和紧凑地描述，从而得到数据变量之间的关系[10]

AANN神经网络结构复杂，训练大量数据时搜索速度慢且无法全局搜索，易陷入局部最优。GA作为一种基于自然选择和群体遗传学的并行算法，能够快速收敛到全局最优解[11]。利用GA全局寻优，得到AANN神经网络初始权值和阈值，然后再用AANN神经网络进行局部寻优，得到精确的传感器解析冗余网络。

# 3 SDQ算法的仿真实现及改进

# 3.1 发动机模型

本文以一个150座干线客机用、双转子、高涵道比、137.2kN推力级的民用涡扇发动机为研究对象[12]。该发动机应用SDQ算法的结构框图如图2所示。A，B两组传感器有相同的初始值，每组包含6种类型传感器数据。利用上述发动机模型，创建一个数据库，包含各飞行状态下的3000组无故障数据。

# 3.2 SDQ主要模块实现

# 3.2.1 合理性检验

范围检验下限值设置为数据库中最小值的0.75

倍，上限值设置为数据库中最大值的1.25倍；速率检验限制值设置为数据库中最大变化绝对值。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/f6542900-5f51-4185-854f-1b62f0dfe01d/122464ee2624658859344b95934533734b9bd1b7c51b3cf02a4b7bfe64642411.jpg)  
Fig.2 Frame diagram of SDQ algorithm based on turbofan engine simulink model

# 3.2.2 解析冗余检验

解析冗余检验包含冗余通道检验和基于传感器网络的解析网络检验。本文采用虚警率不超过 $0.005\%$  来确定每个传感器的冗余通道检验限制值。

解析网络检验更加复杂，本文通过改变燃油流量  $W_{\mathrm{f}}$  ，飞行高度  $Alt$  和马赫数  $Ma$  来改变发动机状态。将各状态下的传感器数据共同作为AANN神经网络的训练数据，得到传感器解析冗余网络。

# 3.3 AANN神经网络改进

针对涡扇发动机，为了精确构建传感器解析冗余关系，本文对AANN神经网络进行了如下改进。

# 3.3.1 构建AANN神经网络组

在发动机不同的工作状态下，各输出量的解析关系不同[13]。因此针对不同的飞行状态，分别采用一组AANN神经网络进行传感器故障诊断与定位，并根据燃油流量  $W_{\mathrm{f}}$  范围选定对应工况，如图3所示。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/f6542900-5f51-4185-854f-1b62f0dfe01d/bebff927fc659268dc7b17356aec32c7d8d4b44a7bc3c6bff850414297fa8774.jpg)  
Fig.3 AANNs achieve analytical network checks

图3中  $y(t)$  代表不同工况下6种传感器数据， $\hat{y}_0(t)$ ， $\hat{y}_1(t)$ ， $\hat{y}_2(t)$  和  $\hat{y}_3(t)$  分别代表传感器输入对应工况的AANN神经网络的输出数组。表1给出了各组AANN神经网络对应的发动机状态。

Table 1 AANNs correspond to engine state  

<table><tr><td>Condition of the engine</td><td>Network label</td></tr><tr><td>Takeoff condition</td><td>AANNs0</td></tr><tr><td>Rated condition</td><td>AANNs1</td></tr><tr><td>Cruise condition</td><td>AANNs2</td></tr><tr><td>Idling condition</td><td>AANNs3</td></tr></table>

AANN网络具有优良非线性动力学特性和并行计算能力，能够有效辨识发动机动态过程。然而，由于动态过程中传感器数据变化范围很大，对应关系复杂多变，影响神经网络的精度和泛化能力，本文将动态过程进行分块处理，共分为3部分。以慢车状态到最大状态为例：过渡态初始部分，以上述得到的慢车状态关系网络（AANNs3）为基础，利用对应动态数据进行线性拟合，得到修正的传感器解析网络；过渡态中间部分，利用中间动态数据训练得到AANN神经网络；过渡态结尾部分，以最大状态关系网络（AANNs0）为基础，同样利用对应动态数据线性拟合得到修正后的传感器解析网络。

# 3.3.2 AANN神经网络结构

本文针对双通道传感器发动机模型，AANN神经网络基于A，B两组互为冗余的传感器搭建，其中，A组为电磁式传感器，B组为液压式传感器，每组分别包含图2中6个传感器。AANN神经网络有如图4所示的两种结构。第一种结构为A，B两组冗余传感器各自对应一个AANN神经网络，第二种结构为A，B两组冗余传感器对应一个AANN神经网络。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/f6542900-5f51-4185-854f-1b62f0dfe01d/87eac148d94db9a73169ed65a79ca017c09115d7e090aab732100345edff0ee8.jpg)  
Fig.4 Two different AANNs configuration

经仿真验证，结构2中AANN网络易受冗余传感器差值的影响，网络精度不高，使传感器故障诊断和定位的准确度下降。主要因为冗余传感器之间的差值，是由于传感器工作机理不同、测量环境差异等多种因素造成的，而传感器网络是基于各传感器的解析关系构建的，如果将冗余传感器放到一个网络中，

冗余差值将会严重影响实际的传感器间的解析关系，因此采用第一种AANN组结构。

本文采用训练误差  $J_{\mathrm{test}}$  与测试误差  $J_{\mathrm{train}}$  作为确定神经元个数的依据[14]。性能指数  $J$  定义为

$$
J = \frac{\sum_{i = 1}^{n}(y_{\mathrm{d}}(n) - y_{\mathrm{Net}}(n))^{2}}{\sum_{i = 1}^{n}(y_{\mathrm{d}}(n))^{2}} \tag{2}
$$

式中  $y_{\mathrm{d}}(n)$  代表期望值，  $y_{\mathrm{Net}}(n)$  代表AANN网络输出，  $n$  代表训练或测试的样品大小。  $6 - 33 - 5 - 33 - 6$  结构的网络  $J_{\mathrm{test}}$  为1.43，  $J_{\mathrm{train}}$  为1.23，性能参数最优，确定其为网络结构。

# 3.3.3 GA优化AANN神经网络

本文采用拉丁超立方(LHS)方法生成初始种群[15]，编码方式采用格雷码，以轮盘赌方案为选择算法，以双点随机交叉为交叉算子，交叉概率为0.9，变异算子的变异概率为0.08，以网络误差矩阵平方和的倒数为适应度函数，进化代数设定为100。优化后得到了AANN神经网络初始权值和阈值，再进行网络训练，得到最终的传感器解析冗余网络。表2所示为未优化和优化后的AANN神经网络主要参数对比，可知经过优化的AANN神经网络训练时间大量缩短，网络精度显著提高。

Table 2 Comparison of performance parameters of AANN and GA-AANN  

<table><tr><td></td><td>AANN</td><td>GA-AANN</td></tr><tr><td>Epoch</td><td>247</td><td>54</td></tr><tr><td>Time/s</td><td>1392</td><td>292</td></tr><tr><td>Performance</td><td>9.61×10-5</td><td>1.17×10-7</td></tr></table>

# 4 数字仿真验证

参考文献[16]中提到一种SDQ算法，其合理性检验与本文提到的方法一致，解析冗余检验是将同种类型传感器通过最小二乘法拟合得到近似线性关系。下面将该方法与本文提出的基于GA优化AANN神经网络的SDQ算法进行对比仿真实验。

# 4.1 稳态条件下单故障诊断仿真实验

仿真实验在巡航状态下进行。如图5所示，间歇故障、阶跃故障和漂移故障分别被注入到涡扇航空发动机模型中，阶跃故障和漂移故障为正向故障，间歇故障为负向故障。由于A，B两通道的结果相同，本文只针对A通道采用上述两种方法进行对比。

为了采用更充分的实际数据，检验GA- AANN神经网路的泛化能力，参照文献[17，18]提出的民用涡扇发动机故障诊断系统的验证方法，本文采用蒙特

卡罗仿真方法，针对上述三种传感器故障类型，随机选取3000组巡航工作状态，随机匹配不同故障情形，其中6种传感器各500组故障数据，故障幅度在

$[1.33\% ,10\% ]$  内均匀分布。

针对间歇故障、阶跃故障和漂移故障，两种方法的各传感器故障诊断和隔离正确率如表3所示，根据

Table 3 Accuracy of diagnosis and isolation of three types of failures (steady state)  

<table><tr><td rowspan="2" colspan="2"></td><td colspan="6">Detected and isolated faults</td><td></td><td></td></tr><tr><td>XNIPC</td><td>XNHPC</td><td>p25</td><td>p3</td><td>T3</td><td>T45</td><td></td><td></td></tr><tr><td rowspan="18">Least squares</td><td rowspan="3">XNIPC</td><td>Intermittent</td><td>0.996</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td>Step</td><td>0.952</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td>Drift</td><td>0.834</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td rowspan="3">XNHPC</td><td>Intermittent</td><td>0.000</td><td>1.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td>Step</td><td>0.000</td><td>0.982</td><td>0.000</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td>Drift</td><td>0.000</td><td>0.666</td><td>0.000</td><td>0.000</td><td>0.270</td><td></td><td></td></tr><tr><td rowspan="3">p25</td><td>Intermittent</td><td>0.000</td><td>0.000</td><td>0.930</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td>Step</td><td>0.000</td><td>0.000</td><td>0.912</td><td>0.056</td><td>0.000</td><td></td><td></td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.624</td><td>0.244</td><td>0.000</td><td></td><td></td></tr><tr><td rowspan="3">p3</td><td>Intermittent</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.954</td><td>0.000</td><td></td><td></td></tr><tr><td>Step</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.950</td><td>0.000</td><td></td><td></td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.902</td><td>0.000</td><td></td><td></td></tr><tr><td rowspan="3">T3</td><td>Intermittent</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.990</td><td></td><td></td></tr><tr><td>Step</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.964</td><td></td><td></td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.914</td><td></td><td></td></tr><tr><td rowspan="3">T45</td><td>Intermittent</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.958</td><td></td><td></td></tr><tr><td>Step</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.986</td><td></td><td></td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.516</td><td></td><td></td></tr><tr><td rowspan="18">GA-AANN</td><td rowspan="3">XNIPC</td><td>Intermittent</td><td>0.996</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td>Step</td><td>0.984</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td>Drift</td><td>0.922</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td rowspan="3">XNHPC</td><td rowspan="2">Intermittent</td><td>0.000</td><td>1.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td>Step</td><td>0.000</td><td>0.988</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td></tr><tr><td>Drift</td><td>0.000</td><td>0.974</td><td>0.000</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td rowspan="3">p25</td><td>Intermittent</td><td>0.000</td><td>0.000</td><td>0.930</td><td>0.000</td><td>0.000</td><td></td><td></td></tr><tr><td>Step</td><td>0.000</td><td>0.000</td><td>0.932</td><td>0.034</td><td>0.000</td><td></td><td></td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.912</td><td>0.048</td><td>0.000</td><td></td><td></td></tr><tr><td rowspan="3">p3</td><td>Intermittent</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.954</td><td>0.000</td><td></td><td></td></tr><tr><td>Step</td><td>0.000</td><td>0.000</td><td>0,000</td><td>0.950</td><td>0.000</td><td></td><td></td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.934</td><td>0.000</td><td></td><td></td></tr><tr><td rowspan="3">T3</td><td>Intermittent</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.990</td><td></td><td></td></tr><tr><td>Step</td><td>0.000</td><td>0.000</td><td>0,000</td><td>0.000</td><td>0.994</td><td></td><td></td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.956</td><td></td><td></td></tr><tr><td rowspan="3">T45</td><td>Intermittent</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.958</td><td></td><td></td></tr><tr><td>Step</td><td>0.000</td><td>0.000</td><td>0.000</td><td>1.000</td><td></td><td></td><td></td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.904</td><td></td><td></td></tr></table>

结果分析可知：间歇故障采用合理性检验模块诊断，两种方法中这部分相同，因此诊断结果一致；阶跃故

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/f6542900-5f51-4185-854f-1b62f0dfe01d/f2a49de1b45488e0a60cd4e99f0086e84b3eb721f96510489d08d1c798e9b90a.jpg)  
Fig.5 Sensor fault input curves

障的诊断效果基本一致，但采用基于GA- AANN的SDQ算法要比基于最小二乘法的SDQ算法更精确，可以诊断出微小幅度的故障，平均正确率提高了 $1.7\%$ ；漂移故障的诊断结果，两者差别较大，基于GA- AANN网络的SDQ算法的性能明显更优，平均正确率提高了 $19.1\%$ 。

# 4.2 动态条件下单故障诊断仿真实验

为检验基于GA- AANN神经网络SDQ算法在发动机动态工作过程中的故障诊断效果，本文设定慢车状态到最大状态过渡态，注入阶跃故障和漂移故障进行故障诊断算法验证。同样采用蒙特卡罗仿真方法验证，得到如表4所示的故障诊断结果。

Table 4 Accuracy of diagnosis and isolation of two types of failure (dynamic state)  

<table><tr><td rowspan="2"></td><td colspan="8">Detected and isolated faults</td></tr><tr><td></td><td>XNIPC</td><td>XNHPC</td><td>p25</td><td>p3</td><td>T3</td><td>T45</td><td></td></tr><tr><td rowspan="12">Least squares</td><td rowspan="2">XNIPC</td><td>Step</td><td>0.714</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td></tr><tr><td>Drift</td><td>0.498</td><td>0.000</td><td>0.222</td><td>0.090</td><td>0.000</td><td>0.000</td></tr><tr><td rowspan="2">XNHPC</td><td>Step</td><td>0.000</td><td>0.824</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td></tr><tr><td>Drift</td><td>0.000</td><td>0.546</td><td>0.000</td><td>0.126</td><td>0.000</td><td>0.000</td></tr><tr><td rowspan="2">p25</td><td>Step</td><td>0.000</td><td>0.000</td><td>0.756</td><td>0.114</td><td>0.000</td><td>0.000</td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.422</td><td>0.256</td><td>0.000</td><td>0.000</td></tr><tr><td rowspan="2">p3</td><td>Step</td><td>0.000</td><td>0.224</td><td>0.000</td><td>0.596</td><td>0.000</td><td>0.000</td></tr><tr><td>Drift</td><td>0.000</td><td>0.232</td><td>0.000</td><td>0.248</td><td>0.000</td><td>0.000</td></tr><tr><td rowspan="2">T3</td><td>Step</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.866</td><td>0.000</td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.720</td><td>0.000</td></tr><tr><td rowspan="2">T45</td><td>Step</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.778</td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.624</td></tr><tr><td rowspan="12">GA-AANN</td><td rowspan="2">XNIPC</td><td>Step</td><td>0.856</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td></tr><tr><td>Drift</td><td>0.822</td><td>0.000</td><td>0.026</td><td>0.000</td><td>0.000</td><td>0.000</td></tr><tr><td rowspan="2">XNHPC</td><td>Step</td><td>0.000</td><td>0.902</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td></tr><tr><td>Drift</td><td>0.000</td><td>0.858</td><td>0.000</td><td>0.018</td><td>0.000</td><td>0.000</td></tr><tr><td rowspan="2">p25</td><td>Step</td><td>0.000</td><td>0.000</td><td>0.884</td><td>0.064</td><td>0.000</td><td>0.000</td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.876</td><td>0.000</td><td>0.000</td><td>0.000</td></tr><tr><td rowspan="2">p3</td><td>Step</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.834</td><td>0.000</td><td>0.000</td></tr><tr><td>Drift</td><td>0.000</td><td>0.098</td><td>0.000</td><td>0.754</td><td>0.000</td><td>0.000</td></tr><tr><td rowspan="2">T3</td><td>Step</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.910</td><td>0.000</td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.894</td><td>0.000</td></tr><tr><td rowspan="2">T45</td><td>Step</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.898</td></tr><tr><td>Drift</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.882</td></tr></table>

根据结果分析可知，相比基于最小二乘法的SDQ算法，基于GA- AANN神经网络的SDQ算法的性能显著提高，阶跃故障的平均隔离正确率提高了 $12.5\%$ ，漂移故障的平均隔离正确率提高了 $33.8\%$ 。但相比稳态条件下故障诊断结果，基于GA- AANN的SDQ算法在过渡态条件下故障诊断和隔离正确率有明显的下降，这主要由于过渡态各参数变化复杂，分块模型精度相对较低，为保证虚警率，故障阈值设定较高，对于小幅故障无法检测出来。

# 4.3 多故障（含噪声）诊断仿真实验

基于最小二乘法的SDQ只针对单故障诊断，对本文提出的基于GA- AANN的SDQ算法进行多传感器故障诊断检验。将风扇转速 $X_{\mathrm{NIPC}}$ 和高压压气机出口总温 $T_{3}$ 对应的两个传感器在15s注入漂移故障，同时各传感器都注入小幅的噪声信号，图6为上述各个传感器的GA- AANN网络输入一输出残差与给定的阈值对比图。从图中可以看出，两种故障传感器可

以被迅速被隔离出来。

同时，对基于GA- AANN神经网络的SDQ算法的除噪能力进行检验。图7为各传感器GA- AANN网络的输入与输出对比图，处理后传感器信号的平均信噪比提高了8.27dB，证明改进的SDQ算法的除噪效果良好。

综上所述，本文提出的基于GA- AANN的SDQ算法相比原来的SDQ算法，在传感器故障诊断和隔离以及滤除噪声方面的性能均有显著提高。基于GA- AANN神经网络来优化SDQ算法，主要依靠大量传感器先验数据，利用AANN神经网络强大的重构解析关系能力，排除干扰因素，充分考虑各传感器数据间相互关系，构建了更高精度的传感器网络，而采用遗传算法，则避免了训练过程中的局部优化同时缩短了神经网络的训练时间，从而快速得到一种高精度、高可靠度的传感器解析冗余网络，能够准确诊断和隔离更微小的传感器故障，且能够滤除噪声干扰。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/f6542900-5f51-4185-854f-1b62f0dfe01d/3cfa96a154d8d5a97363276d4f304649871af8862919305e696d8fe161bffb3b.jpg)  
Fig.6 GA-AANN network fault diagnosis of multiple faults

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/f6542900-5f51-4185-854f-1b62f0dfe01d/67466937fb01a84b6e09573d276497d531c78047017d740fa29adb14cc062a7b.jpg)  
Fig.7 GA-AANN network filter noise results

# 5 总结

通过本文研究，得到如下结论：

（1)本文采用GA优化AANN神经网络，缩短了网络的训练时间，构建了一种高精度、高可靠性、高稳定度的传感器网络。

（2）在发动机稳态条件下，基于GA-AANN神经网络的SDQ算法相较于原来的SDQ算法，对阶跃故障定位的平均正确率提高了  $1.7\%$  ，对漂移故障定位的平均正确率提高了  $19.1\%$  ，显著提高了单传感器故障诊断和隔离的正确率。

（3）在发动机动态条件下，基于GA-AANN神经网络的SDQ算法相较于原来的SDQ算法，对阶跃故障定位的平均正确率提高了  $12.5\%$  ，对漂移故障定位的平均正确率提高了  $33.8\%$  。由于过渡态各参数变化范围很大，传感器网络模型精度受限，相比稳态条件下，故障诊断和隔离正确率有不同程度的下降，但

满足实际性能需求

（4）本文提出的优化后的SDQ算法在多故障诊断和除噪方面性能优异，处理后的传感器信号平均信噪比提高了8.27dB

# 参考文献：

[1] 龚志飞，郭迎清，基于主元分析法的航空发动机传感器故障诊断研究[J].计算机测量与控制，2012，20(8). [2] 叶志锋，孙建国，应用神经网络诊断航空发动机气路故障的前景[J].推进技术，2002，23（1）：1- 4.（YE Zhi- feng，SUN Jian- guo. Prospect for Neural Networks Used Aeroengine Fault Diagnosis Technology[J]. Journal of Propulsion Technology，2002，23（1）:1- 4.） [3] 张书刚，郭迎清，陈小磊，航空发动机故障诊断系统性能评价与仿真验证[J].推进技术，2013，34（8）：1121- 1127. （ZHANG Shu- gang，GUO Ying- qing，CHEN Xiao- lei. Performance Evaluation and Simula-

tion Validation of Fault Diagnosis System for Aircraft Engine [J]. Journal of Propulsion Technology, 2013, 34 (8):1121- 1127. [4] Maul W A, Melcher K J, Chicatelli A K, et al. Sensor Data Qualification for Autonomous Operation of Space Systems[R]. AIAA FS- 06- 07. [5] Melcher K J, Fulton C E, Maul W A, et al. Development and Application of a Portable Health Algorithms Test System[R]. NASA/TM 2007- 214840. [6] Hines J, Uhrig R. Use of Autoassociative Neural Networks for Signal Validation[J]. Journal of Intelligent & Robotic Systems, 1998, 21(2):143- 154. [7] 崔文斌, 叶志锋, 彭利方. 基于信息融合遗传算法的航空发动机气路故障诊断[J]. 航空动力学报, 2015, 30(5):1275- 1280. [8] Wong E, Fulton C E, Maul W A, et al. Sensor Data Qualification System (SDQS) Implementation Study [R]. NASA/TM 2009- 215442. [9] Guo- Jian H, Gui- Xiong L, Geng- Xin C, et al. Self- Recovery Method Based on Auto- Associative Neural Network for Intelligent Sensors[C]. Jinan: 8th World Congress on Intelligent Control and Automation (WCI- C4), 2010. [10] Reyes J, Vellasco M, Tanscheit R. Measurement Correction for Multiple Sensors Using Modified Autoassociative Neural Networks[J]. Neural Computing & Applications, 2013, 24(7- 8).

[11] 刘浩然. 一种基于改进遗传算法的神经网络优化算法研究[J]. 仪器仪表学报, 2016, 37(7):1573- 1580. [12] 张书刚, 郭迎清, 陆军. 基于GasTurb/MATLAB的航空发动机部件级模型研究[J]. 航空动力学报, 2012, 27(12):2850- 2856. [13] Guo T, Mattern D, Jaw L, et al. Model- Based Sensor Validation for a Turbofan Engine Using Autoassociative Neural Networks[J]. International Journal of Smart Engineering System Design, 2003, 5(1):21- 32. [14] Meskin N. Multiple- Model Sensor and Components Fault Diagnosis in Gas Turbine Engines Using Autoassociative Neural Networks[J]. Neural Computing & Applications, 2013, 24(7- 8). [15] 王清, 招启军. 基于遗传算法的旋翼翼型综合气动优化设计[J]. 航空动力学报, 2016, 31(6):1486- 1495. [16] Jeffrey T Csank, Donald L Simon. Sensor Data Qualification Technique Applied to Gas Turbine Engines [R]. NASA/TM 2013- 216609. [17] Simon D L, Bird J, Davison C, et al. Benchmarking Gas Path Diagnostic Methods: A Public Approach [R]. ASME 2008- GT- 51360. [18] Simon D L. Propulsion Diagnostic Method Evaluation Strategy (ProDIMES) User S Guide [R]. NASA/TM 2010- 21.

（编辑：朱立影）