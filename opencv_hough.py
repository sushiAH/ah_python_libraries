"""
段差上での位置補正に用いる
段差の右端をodom座標系の原点とする
"""

import cv2
import numpy as np
import time
import math


def capture_single_frame(device_id=0):
    cap = cv2.VideoCapture(device_id)
    if not cap.isOpened():
        print("カメラが見つかりません")
        return None
    for _ in range(10):
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if ret:
        return frame
    else:
        return None


def draw_rad_circle(img, px, py):
    cv2.circle(img, (int(px), int(py)),
               radius=5,
               color=(0, 0, 255),
               thickness=-1)


def show_lines(img, lines):
    if lines is None:
        print("線が検出されていません")
        return None

    for i in range(0, len(lines)):
        x1, y1, x2, y2 = lines[i][0]
        cv2.line(img, (x1, y1), (x2, y2),
                 color=(0, 255, 0),
                 thickness=3,
                 lineType=cv2.LINE_4,
                 shift=0)


def sort_by_angle(lines):
    v_lines = []  #vertical
    h_lines = []  #horizontal
    if (lines is None):
        return None, None

    for i in range(0, len(lines)):
        line = lines[i][0]
        rad = calc_line_slope(line)

        if (rad < 20 and rad > -20):
            h_lines.append(line)

        elif ((rad >= -90 and rad <= -70) or (rad <= 90 and rad >= 70)):
            v_lines.append(line)

    return v_lines, h_lines


def calc_line_slope(line):
    x1, y1, x2, y2 = line
    if (x1 == None or y1 == None or x2 == None or y2 == None):
        return None

    rad = math.atan2(y2 - y1, x2 - x1)
    return math.degrees(rad)


def select_h(h_lines):
    if (h_lines is None):
        return None

    h_lines_up = []
    h_lines_down = []
    h_mean = np.mean(h_lines, axis=0)
    for i in range(0, len(h_lines)):
        if (h_lines[i][1] > h_mean[1]):
            h_lines_down.append(h_lines[i])
        elif (h_lines[i][1] < h_mean[1]):
            h_lines_up.append(h_lines[i])

    return h_lines_down, h_lines_up


def select_v(v_lines):
    if (v_lines is None):
        return None

    v_lines_right = []
    v_lines_left = []

    v_mean = np.mean(v_lines, axis=0)
    for i in range(0, len(v_lines)):
        if (v_lines[i][0] > v_mean[0]):
            v_lines_right.append(v_lines[i])
        elif (v_lines[i][0] < v_mean[0]):
            v_lines_left.append(v_lines[i])

    return v_lines_right, v_lines_left


# 方程式を立てて交点を解く
def calc_intersection(v_best, h_best):
    if (v_best is None or h_best is None):
        return None, None

    # 縦線の2点
    x1, y1, x2, y2 = v_best
    # 横線の2点
    x3, y3, x4, y4 = h_best

    # 直線1: a1*x + b1*y = c1
    a1 = y1 - y2
    b1 = x2 - x1
    c1 = a1 * x1 + b1 * y1

    # 直線2: a2*x + b2*y = c2
    a2 = y3 - y4
    b2 = x4 - x3
    c2 = a2 * x3 + b2 * y3

    # 連立方程式を解く（クラメルの公式）
    det = a1 * b2 - a2 * b1
    if abs(det) > 1e-10:
        px = (c1 * b2 - c2 * b1) / det
        py = (a1 * c2 - a2 * c1) / det

        return px, py


def img_to_cam(x, y, s, obj_x, obj_y):
    # x,y: 画像上のピクセル座標
    # s: スケーリング係数 [mm/px]
    # obj_x,obj_y: オブジェクトのワールド座標
    # x_cam,y_cam: 台の上座標系でのカメラ位置(台の右下をodomの原点として取る)

    cam_resolution = [640, 480]
    calib_x = cam_resolution[0] / 2
    calib_y = cam_resolution[1] / 2

    delta_x = (x - calib_x) * s
    delta_y = (y - calib_y) * s
    print("誤差x", delta_x)
    print("誤差y", delta_y)

    x_cam_in_odom = obj_x - (-delta_y)
    y_cam_in_odom = obj_y - (-delta_x)

    return x_cam_in_odom, y_cam_in_odom


def calc_correct_pos():

    # ---params---
    cam_to_wheel_length = 560

    #path_img = "/home/aratahorie/test_code/img/kado.jpg"
    path_img = "/home/aratahorie/migikado.jpg"
    #img = cv2.imread(path_img)
    img = capture_single_frame(2)
    if (img is None):
        return None

    height, width = img.shape[:2]

    img = img[0:height // 2, :]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 15)
    edges = cv2.Canny(binary, 50, 150)
    lines = cv2.HoughLinesP(edges,
                            1,
                            np.pi / 180,
                            threshold=20,
                            minLineLength=40,
                            maxLineGap=20)

    v_lines, h_lines = sort_by_angle(lines)
    h_lines_down, h_lines_up = select_h(h_lines)
    v_lines_right, v_lines_left = select_v(v_lines)

    h_lines_down_mean = np.mean((h_lines_down), axis=0).astype(int)
    h_lines_up_mean = np.mean((h_lines_up), axis=0).astype(int)
    v_lines_right_mean = np.mean((v_lines_right), axis=0).astype(int)
    v_lines_left_mean = np.mean((v_lines_left), axis=0).astype(int)

    px_1, py_1 = calc_intersection(v_lines_right_mean, h_lines_down_mean)
    px_2, py_2 = calc_intersection(v_lines_left_mean, h_lines_down_mean)
    px_3, py_3 = calc_intersection(v_lines_right_mean, h_lines_up_mean)
    px_4, py_4 = calc_intersection(v_lines_left_mean, h_lines_up_mean)

    x_mean = int((px_3 + px_4) / 2)
    y_mean = int((py_2 + py_4) / 2)

    h_lines_down_slope = calc_line_slope(h_lines_down_mean)
    v_lines_right_slope = calc_line_slope(v_lines_right_mean)

    if (v_lines_right_slope < 0):
        v_lines_right_slope += 90
    elif (v_lines_right_slope > 0):
        v_lines_right_slope += -90

    final_slope = (h_lines_down_slope + (v_lines_right_slope)) / 2

    s = (40 / 70)
    x_cam_in_odom, y_cam_in_odom = img_to_cam(x_mean, y_mean, s, 760, 450)

    #カメラから車輪までの変換
    odom_x = x_cam_in_odom - cam_to_wheel_length * math.cos(
        math.radians(final_slope))
    odom_y = y_cam_in_odom - cam_to_wheel_length * math.sin(
        math.radians(final_slope))

    #-----------描画----------------
    print("水平下", h_lines_down_mean)
    print("水平上", h_lines_up_mean)
    print("垂直右", v_lines_right_mean)
    print("垂直左", v_lines_left_mean)
    show_lines(img, lines)
    draw_rad_circle(img, px_1, py_1)
    draw_rad_circle(img, px_2, py_2)
    draw_rad_circle(img, px_3, py_3)
    draw_rad_circle(img, px_4, py_4)
    draw_rad_circle(img, x_mean, y_mean)

    print("中心点座標", x_mean, y_mean)
    print("h_lines_down_slope", h_lines_down_slope)
    print("v_lines_right_slope", v_lines_right_slope)
    print("車体角度", final_slope)
    print("カメラX", x_cam_in_odom)
    print("カメラY", y_cam_in_odom)
    print("車輪x", odom_x)
    print("車輪y", odom_y)

    # cv2.imshow("Result", img)
    # cv2.imshow("gray", gray)
    # cv2.waitKey(0)

    return odom_x * 0.001, odom_y * 0.001, final_slope


if __name__ == "__main__":
    calc_correct_pos()
