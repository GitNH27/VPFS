import cv2
# NOTE: pupil_apriltags seems to be broken on Python 3.12, so this needs to be run with <3.12
from pupil_apriltags import Detector

detector = Detector()

img = cv2.imread("speaker.jpg", cv2.IMREAD_GRAYSCALE)
image = cv2.imread("speaker.jpg", cv2.IMREAD_COLOR)

# Detect tags
detections = detector.detect(img)

font = cv2.FONT_HERSHEY_PLAIN

for tag in detections:
    image = cv2.putText(image, str(tag.tag_id), (int(tag.center[0]), int(tag.center[1])), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
    image = cv2.rectangle(image, (int(tag.corners[0][0]), int(tag.corners[0][1])), (int(tag.corners[2][0]), int(tag.corners[2][1])), (255, 0, 0), 2)

cv2.imshow("image", image)

cv2.waitKey(0)

cv2.destroyAllWindows()