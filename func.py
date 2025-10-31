import cv2

cap = cv2.VideoCapture(0)
print("Camera opened?", cap.isOpened())

if cap.isOpened():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Test Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
