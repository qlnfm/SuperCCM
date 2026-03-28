# 🎇 SuperCCM Parameter Calculation Workflow

This document was translated by ChatGPT. Here is [Original version](how_analysis_cn.md).

> Applicable Version: v1.1


## 0. Image Loading

Load an image file as a grayscale image for subsequent analysis.

In version 1.1, this method has been optimized. It attempts to find the largest connected region of non-zero pixels,
and after performing a closing operation, treats it as a clean ROI (Region of Interest).
Therefore, it is more adaptable to images with extra bottom regions and mosaic-stitched images.

In addition, to accommodate different CCM devices, the **field-of-view pixel ratio** must be specified.
By default, it is 400/384 (μm/pixel), which corresponds to images produced by HRT-III/RCM.


## 1. Nerve Segmentation

The purpose of this step is to binarize the image:
pixels classified as corneal nerves are assigned a value of 255, while non-nerve pixels are assigned 0.

This task is performed using a UNet model. The full source code of this model can be found on GitHub:
https://github.com/qlnfm/Segmentation-models-for-CCM-images

In version 1.1, the model has been optimized by training on an augmented dataset that includes seams and random masking,
making it more suitable for segmenting mosaic-stitched images.

It is worth noting that UNet, as an FCN model, can handle input images of arbitrary resolution.
Images from other CCM devices, such as wide-field corneal confocal microscopes, can also be analyzed.
However, these have **not been validated**.


## 2. Skeletonization

The binarized image from the previous step is skeletonized to extract its topological structure.
Additionally, isolated fragments are filtered out, and spurs and false branch points are removed.


## 3. Graph Construction

The cleaned skeletonized image is converted into a multigraph (undirected).
For each pixel:
- A pixel with 1 neighbor in its 8-neighborhood is considered an endpoint.
- A pixel with 2 neighbors is considered a segment point.
- A pixel with 3 or more neighbors is considered a branch point.

Endpoints and branch points are treated as nodes,
and connected segment points are treated as edges to construct a multigraph.


## 4. Main Nerve Fiber Extraction

Based on the tutorial video by the Early Neuropathy Assessment Group
and the main nerve fiber selection rules from ACCMetrics,
the criteria for selecting main nerve fibers are defined as follows:

1. Both ends of the nerve lie on the image boundary. The boundary is defined as 5% of the average of image width and height.
2. The Euclidean distance between the two ends is greater than 50% of the average of image width and height.
3. Main nerve fibers do not overlap.
4. For overlapping nerve fibers, a combined score based on turning angle, length, and intensity is calculated.
   The fiber with the highest score is considered the main nerve fiber, and the others are treated as branches.


## 5. Parameter Calculation

> We strongly recommend reporting the SuperCCM version along with the parameters.

The calculation methods for each parameter are as follows:

### 1) Resolution (μm/pixel)

Actual field-of-view length of the image (μm) / image pixel length (pixel)

### 2) Image Area (pixel)

Total number of valid pixels in the image

### 3) Image Area (mm²)

Image Area (pixel) × Resolution / 1000 × Resolution / 1000

### 4) Length of Nerves (pixel)

The distance between two 4-connected pixels is considered 1 pixel,
and the distance between diagonally connected pixels is considered sqrt(2) pixels.
The total nerve length is the sum of all such distances.

### 5) Length of Nerves (mm)

Length of Nerves (pixel) × Resolution / 1000

### 6) CNFL (mm/mm²)

Length of Nerves (mm) / Image Area (mm²)

### 7) Count of Main Nerves (n)

Total number of main nerve fibers

### 8) CNFD (n/mm²)

Count of Main Nerves / Image Area (mm²)

### 9) Count of Primary Branch Points (n)

Total number of primary branch points

### 10) CNBD (n/mm²)

Count of Primary Branch Points / Image Area (mm²)

### 11) Nerve Area (pixel)

Total number of pixels belonging to nerve regions in the image

### 12) Nerve Area (mm²)

Nerve Area (pixel) × Resolution / 1000 × Resolution / 1000

### 13) CNFA (mm²/mm²)

Nerve Area (mm²) / Image Area (mm²)

### 14) Count of Branch Points (n)

Total number of branch points

### 15) CTBD (n/mm²)

Count of Branch Points / Image Area (mm²)

### 16) CNFT

Tortuosity (also known as TC), defined as the average tortuosity of all main nerve fibers.

The tortuosity algorithm follows the paper:
Kallinikos P, Berhanu M, O'Donnell C, Boulton AJ, Efron N, Malik RA.
Corneal nerve tortuosity in diabetic patients with neuropathy.
Invest Ophthalmol Vis Sci. 2004;45(2):418-422.
doi:10.1167/iovs.03-0637

Reimplemented in Python and validated with minimal error compared to original results.

Note: If the number of main nerve fibers is 0, this value is None.

### 17) CNFrD

Fractal dimension of the binarized corneal nerve image calculated using the box-counting method.