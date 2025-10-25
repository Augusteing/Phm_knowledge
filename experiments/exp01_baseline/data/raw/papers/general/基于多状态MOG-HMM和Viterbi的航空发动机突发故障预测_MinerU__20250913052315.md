# 基于多状态MOG-HMM和Viterbi的航空发动机突发故障预测

李丽敏，王仲生，姜洪开（西北工业大学航空学院西安510652）

摘要针对航空发动机的突发故障，提出了一种基于多状态混合高斯隐马尔科夫模型（mixture of Gaussian- hidden Markov model，简称MOG- HMM）和Viterbi算法相结合的预测方法。首先，根据航空发动机突发故障的历史监测数据建立多状态MOG- HMM模型，确定状态数、状态转移矩阵、观察值概率分布以及最终的突发故障状态；然后，对新采集的观测数据，通过Viterbi算法解码出该观测数据对应的当前状态；最后，计算该状态到达突发故障状态的时间间隔，从而可以对突发故障进行预测。仿真和实验结果表明，该方法能够实现对突发故障的预测，并且符合标准预测指标的要求。

关键词多状态混合高斯隐马尔科夫模型；Viterbi算法；突发故障预测；航空发动机中图分类号  $\mathrm{TP206^{+}}$  .3

# 引言

航空发动机作为飞机的动力系统，其安全性和可靠性关乎整个飞机能否正常工作，更重要的是关乎人民生命财产安全。近年来，航空发动机突发故障的发生呈上升趋势。突发故障是指使系统立即丧失其功能的破坏性故障，比缓变性故障更具有破坏性和危险性。由于突发故障的发生具有快速性和随机性，发生前的征兆不明显，因此很难进行预测。

故障预测的目的是通过预测方法预测系统将来的健康状态和从当前状态到达故障状态的时间间隔[3- 4]。近年来，对故障预测的关注促进了很多方法、工具以及应用的产生。根据预测原理的不同，故障预测方法可以分为3种类型，分别是基于模型的预测方法、基于实验的预测方法以及基于数据驱动的预测方法。基于模型的预测方法依赖于分析物理模型所代表的系统的行为，形式多为代数或微分方程，由于其前提是需要建立物理模型，因此过程往往很复杂；基于实验的预测方法利用某一时期的实验反馈数据去调整一些可靠性模型的参数，对于经验的要求很高；基于数据驱动的预测方法能

将传感器采集到的信号转换为可靠性模型，这些模型可以描述故障退化的行为，该方法的优点是简单而且针对性强。目前，预测逐渐趋向于数据驱动型的方法。对于缓变性故障的数据驱动型预测方法已经有很多，而对于突发故障的预测研究很少。Diego Alejandro等提出的MOG- HMM方法在缓变性故障预测上的效果明显，该方法是将混合高斯（mixture of Gaussion，简称MOG）分布拟合方法和HMM建模方法进行结合，它能够以状态序列的形式描述故障的演化过程。由于突发故障可以看做是一个被压缩的缓变故障，因此笔者考虑将该方法进行改进后应用于航空发动机突发故障的预测。

为了能够将MOG- HMM方法应用于航空发动机突发故障的预测，首先分析突发故障的特点，然后对MOG- HMM方法进行改进。由于突发故障状态变化较快，而且状态持续时间较短，为了能够扑捉到当前状态，同时提高利用MOG- HMM模型计算从当前状态到达突发故障状态的时间间隔的精确度，通过增加MOG- HMM模型的状态数来实现，并利用Viterbi算法的最优路径思想，将新采集数据

进行状态解码。在计算时间间隔时对状态转移矩阵利用Dijkstra算法计算最短路径，可以得到最短的时间间隔，为预防突发故障的发生提供一定的参考。

# 1 航空发动机突发故障预测整体方案

如图1所示为基于多状态MOG- HMM模型和Viterbi算法的突发故障预测总体流程。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/84100434-e542-4d30-a78a-fa65c312c590/05da7caf6c106f27479e26a3fcff88661faf08d43a9b2e408c38edec2fd7e1b8.jpg)  
图1基于多状态MOG-HMM模型和Viterbi算法的突发故障预测总体流程

Fig.1 Flow chart of abrupt failure prognosis based on multi- states MOG- HMM and Viterbi algorithm

首先采用Baum- welch算法对突发故障历史监测数据进行训练，从而获得其对应的多状态MOG- HMM模型。该模型的参数包括状态个数、初始状态概率分布、状态转移概率分布、观测值概率分布，以及计算从当前状态到达突发故障状态的时间间隔所需要的中间参数，即每个状态的停留时间和训练数据所对应的最终状态，包括整个训练数据的时间序列所对应的状态序列。离散隐马尔科夫模型的观测量可以采用分布式离散概率来表示，但连续隐马尔科夫模型中的观测序列通常都假设是由高斯概率密度函数模拟产生的。航空发动机是一个复杂系统，从上面采集到的传感器信号往往包含了各种噪声，因此由单一高斯概率密度函数来模拟HMM观测序列已经不能满足要求，于是使用几个高斯概率密度函数的线性组合模拟观测序列的产生。如果高斯概率密度函数足够多，则混合高斯密度可以逼近任意的概率分布函数[13]。每一个高斯概率密度函数都有各自的均值和协方差矩阵，这些参数可以通过观测样本特征进行统计学习得到。本研究方法中的观测值概率分布就是通过混合高斯概率密度函数来逼近的。

率密度函数来逼近的。

获得训练出来的多状态MOG- HMM模型之后，首先，对新采集来的数据采用Viterbi算法进行当前状态估计；然后，采用Dijkstra算法估计当前状态到达突发故障状态的最短路径，即最快多久后会发生突发故障；最后，计算该路径经历的总时间，从而得出该新采集数据对应当前状态到达突发故障状态的时间间隔。

# 2 基于多状态MOG-HMM和Viterbi算法的突发故障预测

基于多状态MOG- HMM和Viterbi算法的突发故障预测分为3个步骤。

第1步，对突发故障历史监测数据集合  $\mathcal{X}$  进行特征提取和特征选择，获得一个新的观测序列  $X$  ，维数根据特征个数确定，长度根据实际情况自定义。

通过Baum- welch算法获得代表突发故障多状态MOG- HMM模型  $\lambda$  的6个参数可表示如下

$\lambda = (P,\mathbf{A},\mathbf{B},\mu (D(S_{i}))$ $\sigma (D(S_{i})),S_{\mathrm{final}})$  (1)其中：  $P$  为突发故障多状态MOG- HMM模型的初始状态分布，表示初始条件下突发故障的每个状态出现的概率，可初步确定当前最可能出现状态，往往根据先验知识进行设置；  $\mathcal{A}$  表示状态转移概率分布矩阵，其中的每一个元素表示从突发故障的当前状态到达其他所有可能状态的概率；  $B$  表示观察值概率分布矩阵，表示该观察值符合的某种概率分布，可用于计算当前观测值出现的概率；  $\mu (D(S_{i}))$  为高斯混合分布函数中的均值，用于每个状态持续的平均时间；  $\sigma (D(S_{i}))$  为高斯混合分布函数中的方差；  $\mu (D(S_{i}))$ $\sigma (D(S_{i})),S_{\mathrm{final}}$  为计算从当前状态到达突发故障状态的时间间隔所需要的中间参数。计算这6个参数的过程如下：

1）对突发故障历史监测数据集合  $\mathcal{X}$  进行特征提取和特征选择，获得观测序列  $X_{i},i = 1,2,\dots ,n_{\circ}$

2）设置观测序列  $X_{i}$  的多状态个数  $N,N$  值的量化计算是将整个测试数据持续的时间  $T$  除以突发故障状态持续的时间  $t$  ，即  $N = T / t$  ，设置每个状态的高斯混合数  $M^{[13]}$  。

3）初始化参数  $P,A$  和  $B$  ，并将观测序列  $X$  平均分割为  $N$  部分，即每个状态对应  $n / N$  个观测值。通过  $\mathrm{k}$  -means聚类将  $X$  的每个状态聚类为  $M$  类，并将每类数据按照高斯混合序号  $(1,2,\dots ,M)$  进行编号，得到以高斯混合序号  $(1,2,\dots ,M)$  表示的时间序列  $O_{t}(t = 1,2,\dots ,N)$  。

4）通过Baum-welch算法训练  $P,A$  ，概率 $P1(O|\lambda)$  迭代前后的差值作为训练停止的条件，获得更新的  $P$  和  $\mathbf{A}$  。  $\textbf{B}$  由突发故障数据通过混合高斯分布参数估计求得，即通过式（2）、式（3）求得。

5）通过Viterbi解码获得整个时间序列  $O_{i}$  对应的状态序列  $S_{i}$  。

6）通过式（4）～式（6）计算中间参数 $\mu (D(S_{t})),\sigma (D(S_{t}))$  和  $S_{\mathrm{final}}$  。 $b_{j}(O) = \sum_{m = 1}^{M}C_{j,m}\xi (O_{\mu_{j,m}},\sigma_{j,m})\quad (j = 1,2,\dots ,N)$

其中：  $C_{j,m}$  为混合加权系数，符合

$$
\sum_{m = 1}^{M}C_{j,m} = 1\quad (C_{j,m}\geqslant 0) \tag{3}
$$

$\xi (O,\mu_{j,m},\sigma_{j,m})$  为多维正态高斯分布

$$
\mu (D(S_{t})) = \frac{1}{L}\sum_{l = 1}^{L}D(S_{t,l}) \tag{4}
$$

$$
\sigma (D(S_{t})) = \sqrt{\frac{1}{L}\sum_{l = 1}^{L}[D(S_{t,l}) - \mu(D(S_{t}))]^{2}} \tag{5}
$$

$$
S_{\mathrm{final}} = S_N \tag{6}
$$

其中：  $D(\cdot)$  为观测值访问当前状态的停留时间；  $t$  为状态索引；  $l$  为访问次数索引；  $L$  为观测值对某一状态总的访问次数；  $S_{\mathrm{final}}$  为该模型对应的最终突发故障状态。

至此，通过训练获得了突发故障历史监测数据对应的多状态MOG- HMM模型，接下来可以利用这个模型对新采集数据进行状态估计和从当前状态到达突发故障状态的时间间隔预测。

第2步，对新采集数据进行当前状态解码。首先对新采集数据  $y_{t}(1\leq t\leq T)$  进行特征提取和特征选择，通过  $\mathrm{k}$  - means聚类和混合高斯分布概率获得该新采集数据的时间序列  $\mathcal{O}_i$  ，采用Viterbi算法对该时间序列  $\mathcal{O}_i$  进行解码，解码过程如下。

1）输入：训练出来的模型  $\lambda = (P,A,B$ $\mu (D(S_{t})),\sigma (D(S_{t})),S_{\mathrm{final}}$  和观测  $\mathcal{O}_i$

输出：最优路径  $I^{*} = (i_{1}^{*},i_{2}^{*},\dots ,i_{l}^{*})$

2）初始化：  $t = 1$  时，  $\delta_{1}(i) = P_{i}b_{i}(o_{1}),i = 1,2,$ $\dots ,N;\psi_{1}(i) = 0$  。

3）递推：  $t = 2,3,\dots ,T$  时

$$
\begin{array}{rl} & {\delta_{t}(i) = \underset {1\leqslant j\leqslant N}{\max}[\delta_{t - 1}(j)a_{j,i}]b_{i}(o_{t})}\\ & {\psi_{t}(i) = \underset {1\leqslant j\leqslant N}{\operatorname{argmax}}[\delta_{t - 1}(j)a_{j,i}]} \end{array}
$$

4）终止：  $C^{*} = \max_{1\leqslant j\leqslant N}\delta_{T}(i)$

$$
i_{T}^{*} = \arg \max_{1\leqslant i\leqslant N}[\delta_{T}(i)]
$$

5）最优路径回溯：对  $t = T - 1,T - 2,\dots ,1$

$i_{T}^{*} = \psi_{t + 1}(i_{t + 1}^{*})$  ，求得新采集数据的状态序列 $I^{*} = (i_{1}^{*},i_{2}^{*},\dots ,i_{T}^{*})$  ，用  $S_{t} = (S_{1},S_{2},\dots ,S_{T})$  表示。

根据状态序列，求取该段数据对应的当前状态，截取新采集数据对应状态序列  $S_{i}$  的最后一段序列，表示如下

$$
S_{\mathrm{end}} = (S_{t - 1},\dots ,S_{t - 2},S_{t - 1},S_{T}) \tag{7}
$$

其中：  $l$  为最后状态序列的截取位置；  $T$  为当前时刻；取  $S_{\mathrm{end}}$  中数量最多的值作为当前状态  $S_{\mathrm{current}}$  。

第3步，当前状态到达突发故障状态的时间间隔估计。根据识别出的当前状态  $S_{\mathrm{current}}$  、突发故障多状态MOG- HMM模型估计出的最终突发故障状态  $S_{\mathrm{final}}$  以及训练出来的状态转移矩阵  $\mathbf{A}$  ，利用Dijkstra算法计算出从状态  $S_{\mathrm{current}}$  到达状态  $S_{\mathrm{final}}$  的最短路径，即从当前状态到达最终突发故障状态的最短时间。

计算当前状态到达突发故障状态的时间间隔，计算如下

$$
\mathrm{RUL} = \sum_{t = S_{\mathrm{current}}}^{S_{\mathrm{final}}}\mu (D(S_t)) \tag{8}
$$

# 3 实验验证与分析

通过转子实验台驱动特殊加工过的副叶来模拟航空发动机属叶突发性断裂故障。实验之前，通过调整扇叶中1片叶片的固定松紧程度，使其能在一定的转速下通过离心力作用将其甩出，从而模拟航空发动机副叶突发性断裂的故障。笔者所用的实验数据是该实验台在  $400\mathrm{r / min}$  的转速下，用电涡流传感器采集滚轴垂直方向上的振动位移信号，采样频率设为  $256\mathrm{Hz}$  ，采样时间为  $0.8\mathrm{s}$  。由图2可以看出，在0.7s时刻发生了突发故障，导致振动信号

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/84100434-e542-4d30-a78a-fa65c312c590/e0552fc3739ce8e963f24f3dcc780662d2e30d21f9681064dd0dc9c50737ea7b.jpg)  
图2模拟0.8s内航空发动机叶片突发性断裂故障振动信号

Fig.2 Vibration signal of aero- engine abrupt failure simulated over 0.8 s

发生剧烈变化。

突发故障演化过程的多状态MOG- HMM模型建立过程和结果如下。

1）根据训练数据的长度（212）和采样频率 $(256\mathrm{Hz})$ ，确定训练数据的多状态MOG-HMM的时序长度。设  $T = 8$ ，每个  $T$  代表的时间为0.1s，这样可以将训练数据划分为8个部分，每个部分代表1个观测，如图3所示。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/84100434-e542-4d30-a78a-fa65c312c590/b2ee135aed9fd5014030c5d594bc499c80cac4737dadef4aaf8644211b7b8dde.jpg)  
图3将原始训练数据划分的顺序观测序列

Fig.3 Divided the original training data into sequential observation sequences

2）对以上介绍的突发故障数据用Baum-welch算法进行训练。设状态数  $N$  为8，每个状态中的高斯混合数  $M$  为2。

首先随机初始化  $\pi$  和  $\mathbf{A}$  以及  $B$ ，由于本研究中采用的HMM结构为左右型，所以  $\pi$  不需要更新，经过Baum- welch算法训练后得到高斯混合  $M,P$  以及  $\mathbf{A}$  的值分别为

$M =$

$$
\begin{array}{r}\left[ \begin{array}{llllllll}0.1247.0.3752.0.4838,0.8750,0.6777,0.7500,0.3856,0.8750\\ 0.8753.0.6248,0.5162,0.1250,0.3223,0.2500,0.6144,0.1250 \end{array} \right] \end{array}
$$

p=[1,0,0,0,0,0,0,0]

$A =$

<table><tr><td>0.848 4</td><td>0.151 6</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr><tr><td>0</td><td>0.888 7</td><td>0.111 3</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr><tr><td>0</td><td>0</td><td>0.872 6</td><td>0.127 4</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr><tr><td>0</td><td>0</td><td>0</td><td>0.885 9</td><td>0.114 1</td><td>0</td><td>0</td><td>0</td><td>0</td></tr><tr><td>0</td><td>0</td><td>0</td><td>0</td><td>0.902 1</td><td>0.057 9</td><td>0</td><td>0</td><td>0</td></tr><tr><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.879 8</td><td>0.120 2</td><td>0</td><td>0</td></tr><tr><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.871 6</td><td>0.128 4</td><td>0</td></tr><tr><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>1</td></tr></table>

而  $B$  值可以通过观测值状态序列  $\mathcal{O}_t,M$  和多维高斯概率密度通过线性求和获得。

利用训练出来的多状态MOG- HMM模型对测试数据进行突发故障预测，选择另外一组叶片突然断裂的数据作为测试数据，该组测试数据是在0.7s时刻发生突然断裂的实验条件下获取的，同时突发故障状态持续了0.1s。

首先，将测试数据平均分割为8部分，通过Viterbi解码确定每一部分数据所属突发故障所处的状态；然后，再计算每个状态到达最终突发故障状态所需要的时间。图4所示为采用本研究方法对测试数据进行突发故障预测获得的结果。

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/84100434-e542-4d30-a78a-fa65c312c590/ca5c7bbe762db8a711daa89ca0060e464324bb7518368b1b402b54b606f04ff2.jpg)  
图4叶片断裂突发故障预测结果 Fig.4 Prognosis result of blade fracture abrupt failure

如图4所示，直线表示测试数据对应的实际到达突发故障的时间间隔，它是通过当前时刻  $t_c$  与剩余时间间隔相加等于整个数据的时间长度  $T_{s}$  获得的，表示如下

$$
\mathbf{R}\mathbf{U}\mathbf{L} + t_c = T_z \tag{9}
$$

从而得到实际到达突发故障的时间间隔为

$$
\mathbf{R}\mathbf{U}\mathbf{L} = T_z - t_c \tag{10}
$$

利用每0.1s时间内的数据进行测试，计算每组数据到达突发故障所需要的时间，获得了由“\*”表示的突发故障时间间隔预测结果。预测之后与实际突发故障发生的时间间隔进行比较，判断其预测效果。表1为用预测标准中的3个评价指标对上述突发故障预测结果进行的评价，评价指标分别

# 表1对叶片断裂突发故障进行预测的效果评价

Tab.1 Evaluating result of blade fracture abrupt failure prognosis  

<table><tr><td>预测评价标准</td><td>预测评价标准描述</td><td>评价结果</td></tr><tr><td>MSE</td><td>均方根误差,范围[0,∞),最优值为0</td><td>0.326 4</td></tr><tr><td>MAPE</td><td>平均绝对百分比误差,范围[0,∞),最优值为0</td><td>5.041 6</td></tr><tr><td>RA</td><td>瞬时预测精度,范围[0,1],最优值为1</td><td>1</td></tr></table>

为 MSE, MAPE 和 RA, 如果计算出来的各个预测评价指标都在要求的范围内, 则说明该预测算法针对突发故障有效。

从表 1 的结果可以看出, 本研究方法能够用于突发故障的预测。

# 4 结束语

提出了多状态 MOG- HMM 模型和 Viterbi 算法相结合的航空发动机突发故障预测方法。对模拟的航空发动机突发故障进行训练和预测, 通过建立多状态的 MOG- HMM 模型观察其对突发故障的预测效果。仿真和实验结果表明, 本研究方法能够用于航空发动机突发故障的预测, 符合标准预测指标的要求, 为航空发动机的健康监控提供了一定的参考。

# 参考文献

[1] 徐亚森, 王仲生, 姜洪开. 基于能量演化的航空发动机突发性故障预示模型设计[J]. 测控技术, 2012, 31(8): 140- 143. Xu Yasen, Wang Zhongsheng, Jiang Hongkai. Research on catastrophic fault prediction model based on energy feature revolution[J]. Measurement and Control Technology, 2012, 31(8): 140- 143. (in Chinese) [2] Wang Zhongsheng. Research on correlation of sudden failure of aircraft with human- machine- environment[C] //2011 Second International Conference on Mechanic Automation and Control Engineering (MACE). Inner Mongolia, China: IEEE, 2011; 6735- 6738. [3] 周英, 李森, 张泉南, 等. GB/T 23713.1—2009 机器状态监测与诊断、预测第 1 部分: 一般指南[S]. 北京: 中国标准出版社, 2009. [4] 续媛君, 潘宏侠. 设备故障趋势预测的分析与应用[J]. 振动、测试与诊断, 2006, 26(4): 305- 308. Xu Yuanjun, Pan Hongxia. Diagnosis of working conditions of aluminum reduction cells based on wavelet- neural network[J]. Journal of Vibration. Measurement & Diagnosis, 2006, 26(4): 305- 308. (in Chinese) [5] Heng A, Zhang S, Tan A C, et al. Rotating machinery prognostics: state of the art, challenges and opportunities[J]. Mechanical Systems and Signal Processing, 2009, 23(3): 724- 739.

[6] 从飞云, 陈进, 董广明. 基于谱维度和 AR 模型的滚动轴承故障诊断[J]. 振动、测试与诊断, 2012, 32(4): 538- 541. Cong Yunfei, Chen Jin, Dong Guangming. Spectral kurtosis and AR model based method for fault diagnosis of rolling bearings[J]. Journal of Vibration, Measurement & Diagnosis, 2012, 32(4): 538- 541. (in Chinese) [7] Murphy K P. Dynamic bayesian networks: representation, inference and learning[D]. California: University of California, 2002. [8] Rabiner L R. A tutorial on hidden markov models and selected applications in speech recognition[J]. Proceedings of the IEEE, 1989, 77(2): 257- 286. [9] Tobon- Mejia D A, Kamal M, Noureddine Z, et al. A data- driven failure prognostics method based on mixture of gaussian hidden markov models[J]. IEEE Transactions on Reliability, 2012, 61(2): 491- 503. [10] 李航. 统计学习方法[M]. 北京: 清华大学出版社, 2012: 180- 184. [11] Dijkstra E W. A note on two problems in connexion with graphs[J]. Mannerische Mathematik, 1959, 1(1): 269- 271. [12] Baum L E, Petrie T, Soules G, et al. A maximization technique occurring in the statistical analysis of probabilistic functions of Markov chains[J]. Ann Math Statist, 1970, 41(1): 164- 171. [13] Tobon- Mejia D A, Medjaher K, Zerhouni N, et al. A mixture of gaussian hidden Markov model for failure diagnostic and prognostic[C] //2010 IEEE Conference on Automation Science and Engineering. Toronto, Ontario, Canada: IEEE, 2010: 338- 343. [14] Saxena A, Celaya J, Balaban E, et al. Metrics for evaluating performance of prognostics techniques[C] // International Conference on Prognostics and Health Management (PHM08). Danver: IEEE, 2008: 1- 17.

![](https://cdn-mineru.openxlab.org.cn/result/2025-09-13/84100434-e542-4d30-a78a-fa65c312c590/2a71b40f778d89d61e2054192770e29deacb4aeeecd8d7ba0b8718c743458e24.jpg)

第一作者简介: 李丽敏, 女, 1985 年 6 月生, 博士研究生。主要研究方向为机械故障诊断与预测的智能方法。曾发表《Feature selection of sudden failure based on affinity propagation clustering》(《Advanced Materials Research》2012, Vol. 586) 等论文。E- mail: liliminxiaomi@mail. nwpu. edu. cn

ic Motors Technology Co. Ltd as the test specimen. Because the output frequency and output voltage are regulated independently in the system, mechanical characteristics and regulation characteristics of the ultrasonic motor can be measured. Test results show that both characteristics are uniform functions, which can satisfy the requirements of the servo motor's operation characteristics. The rotary ultrasonic motor can thus be used as a servo motor.

Keywords ultrasonic motor; drive and control; operation characteristic; mechanical characteristic; regulation characteristic; servo motor

# Aero-engine Abrupt Failure Prognosis Based on Multi-states MOG-HMM and Viterbi Algorithm

Li Limin, Wang Zhongsheng, Jiang Hongkai (School of Aeronautics, Northwestern Polytechnical University Xi'an, 710072, China)

Abstract Aiming at abrupt failure of aero- engine, an aero- engine abrupt failure prognosis method is proposed by combining of multi- states MOG- HMM and Viterbi algorithm. First of all, according to the historical monitoring data of aero- engine, a multi- states MOG- HMM model is built, that it can determine the number of states, the state transfer matrix, the observation probability distribution and the ultimate abrupt failure state. Then new observation data are collected, through Viterbi algorithm to decode the data to obtain its current state. Finally, the abrupt failure can be predicted by by calculating the time from current state to the final abrupt failure state. Simulation and experimental results show that the method can realize the prognosis of abrupt failure, which also meet the requirements of standard predictor.

Keywords multi- states MOG- HMM; Viterbi algorithm; abrupt failure prognosis; aero- engine

# Optimal Sensor Placement for the Balance System of LAMOST

Hu Na $^{1,2,3}$ , Cui Xiangqun $^{1,2}$ , Yang Dehua $^{1,2}$ , Lu Qishuai $^{1,2}$  (1. National Astronomical Observatories, Nanjing Institute of Astronomical Optics & Technology, Chinese Academy of Sciences Nanjing, 210042, China) (2. Key Laboratory of Astronomical Optics & Technology, Chinese Academy of Sciences Nanjing, 210042, China) (3. Graduate University of Chinese Academy of Sciences Beijing, 100049, China)

Abstract An innovative united method based on principal component analysis (PCA) and the combination modal assurance criteria (CMAC) method is proposed for optimal sensor location. Firstly, using PCA, a raw data matrix is formed with the results of three optimal sensor location algorithms, and the principal components and comprehensive evaluation value are obtained, which can be used to choose candidate locations. Secondly, the MAC matrix of all combinations of the candidate locations is calculated and the points which meet the demand of minimum no- diagonal elements will be chosen. Results show that with the cantilever beam as a research object, the united method has better results than four traditional methods according to three evaluation criteria. Finally, the united method is used in the balance system of large area multi- object spectroscopic telescope (LAMOST) to get the sensor arrangement in two directions.

Keywords optimal sensor placement; principal component analysis; effective independence method; modal kinetic energy; QR decomposition; modal assurance criteria; large area multi- object spectroscopic telescope (LAMOST)