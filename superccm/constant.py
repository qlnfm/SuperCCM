# Image shape
SHAPE = (384, 384)
# Field of view range (mm)
VIEW_DIAMETER_MM = 0.4
# The smallest pixel size of the binarized segmented area is used for filtering.
MIN_BINARY_AREA = 128
# The smallest pixel size of the area located at the edge of the image after binarized segmentation, used for filtering.
MIN_BINARY_EDGE_AREA = 32
INITIAL_EDGE_LENGTH_THRESHOLD = 25
INITIAL_EDGE_LENGTH_GRADIENT = 5
SHORT_EDGE_LENGTH_THRESHOLD = 2
EDGES_ANGLE_THRESHOLD = 60.0
# The minimum length of the main nerve fibers
MIN_MAIN_NERVE_LENGTH = 300
# The minimum width of the main nerve fibers
MIN_MAIN_NERVE_WIDTH = 6000
# The minimum length of the branches emanating from the main nerve fibers
MIN_PRIMARY_BRANCH_LENGTH = 3
