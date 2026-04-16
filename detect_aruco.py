import cv2
import asyncio
import time


async def detect_aruco(marker_id):
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    camera_path = "/dev/v4l/by-path/pci-0000:00:14.0-usb-0:4:1.3-video-index0"

    cap = cv2.VideoCapture(camera_path)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        corners, ids, rejected = detector.detectMarkers(frame)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            for i in range(len(ids)):
                detected_id = ids[i][0]
                print(f"Detected ID: {detected_id}")
                if (detected_id == marker_id):
                    print("目標IDを検出しました。プログラムを終了します")
                    cap.release()
                    cv2.destroyAllWindows()
                    return True

        time.sleep(0.01)

        #cv2.imshow("aruco detection", frame)

        #if cv2.waitKey(1) & 0xFF == ord("q"):
        #    break


if __name__ == "__main__":
    marker_id = 1
    asyncio.run(detect_aruco(marker_id))
