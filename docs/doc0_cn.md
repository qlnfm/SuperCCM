# 🎇 SuperCCM 工作原理

---

## 🧭 摘要

**SuperCCM** 接收一张图像作为输入，输出所有计算得到的参数，并可选择生成可视化结果：

<div style="display: flex; gap: 10px; justify-content: center;">
<img src="assets/vis/img.jpg" width='300px'>
<img src="assets/vis/result.png" width='300px'>
<div style="flex-shrink: 0;">

| 参数    | 数值     |
| :---- | :----- |
| CNFL  | 34.361 |
| CNFD  | 31.25  |
| CNBD  | 181.25 |
| CNFA  | 0.137  |
| CNFW  | 0.025  |
| CTBD  | 300.0  |
| CNFT  | 15.224 |
| CNFrD | 1.557  |

</div>
</div>

---

## 💎 参数是如何计算的？

> ### ❗ 注意
>
> 在给出参数结果时，请务必一同报告SuperCCM的版本号，以便复现和具备可比性。
> 
> **当前版本号: 1.0**

### 1. CNFL

CNFL 表示所有神经纤维的总长度。
图像依次经过分割模块和骨架化模块处理，最终在骨架图上计算总长度。

> 两个 4 连通像素之间的距离记为 1 像素，斜向 8 连通像素的距离记为 √2 像素。

### 2. CNFD

CNFD 表示**主要神经纤维**的数量。

> ### ❓ 如何判断主要神经纤维？
>
> SuperCCM 的 TrunkModule 会综合考虑纤维的强度一致性、曲折程度，并设置最小长度阈值，从而判断主要神经纤维。

### 3. CNBD

CNBD 表示主要神经纤维上的一级分支数量，即分支点的计数。

### 4. CNFA

CNFA 表示神经纤维的总面积，通过统计二值化分割图中的前景像素得到。

> ### ❗ 注意
>
> CNFA 是唯一一个其计算方式与 ACCMetrics 不同的参数。

### 5. CNFW

CNFW 为神经纤维的平均宽度，计算方式为总面积除以总长度。

### 6. CNBD

CNBD 表示神经纤维中的分支点总数。

### 7. CNFT

CNFT 为所有**主要神经纤维**的平均曲折程度，其计算方式与 CCMetrics 中的 TC 一致。

> 算法可参考 [tc.py](../superccm/impl/metircs/tc.py)

### 8. CNFrD

CNFrD 为神经纤维的分形维数，通过在二值化图像上使用盒计数法（Box-Counting）得到。

