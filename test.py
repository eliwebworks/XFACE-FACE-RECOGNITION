import cv2

# Unique identifier of the camera device
camera_id = 'bZs1DmrUQ3IKo0xWEUkuoAVlzAKkEGx8AcWk0HHIb0I'

# Use the cv2.CAP_DSHOW flag and camera index to open the camera
#cap = cv2.VideoCapture(cv2.CAP_DSHOW + camera_id)

def count_cameras():
    num_cameras = 0
    index = 0

    while True:
        #cap = cv2.VideoCapture(index)
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            break
        num_cameras += 1
        cap.release()
        index += 1

    return num_cameras

num_cameras = count_cameras()
print(f"Number of available cameras: {num_cameras}")

# Loop through camera indexes and try opening each one
"""for camera_index in range(10):  # You can adjust the range as needed
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Camera at index {camera_index} is not available.")
    else:
        print(f"Camera at index {camera_index} is available.")
        cap.release()  # Release the camera
"""



