import cv2
img= cv2.imread('capture.jpg')
cropped_image = img[52:121,148:217 ]
cv2.imshow("cropped_image",cropped_image)
cv2.waitKey(0)
