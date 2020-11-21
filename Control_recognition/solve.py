import cv2


def solve_png(img_path):
    org = cv2.imread(img_path)
    height, width = org.shape[:2]


