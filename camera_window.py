import cv2
import numpy as np
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk

def add_margin(cv_img, top, right, bottom, left, color):
    height, width = cv_img.shape[:2]
    new_width = width + right + left
    new_height = height + top + bottom
    # colorには(B, G, R)の形式で色を指定する必要がある
    if len(cv_img.shape) == 3:
        result = np.full((new_height, new_width, 3), color, dtype=cv_img.dtype)
    else:
        result = np.full((new_height, new_width), color, dtype=cv_img.dtype)
    result[top:top+height, left:left+width] = cv_img
    return result


def open_camera(start_index=1):
    # 利用可能なカメラを探す
    num_cameras = 10  # 探索するカメラの最大数
    for i in range(start_index, start_index + num_cameras):
        index = i % num_cameras
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            return cap, index
    return None, -1

# ウィンドウの初期化
root = tk.Tk()
root.title('魚眼効果補正')


info_message = tk.Label(root, text="ここにエラーメッセージが表示されます。")
info_message.pack()

# 初期カメラのセットアップ
cap, camera_id = open_camera()
if cap is None:
    info_message.config(text="利用可能なカメラが見つかりません")
else:
    info_message.config(text="利用可能なカメラが見つかりました")

# 解像度を1280x720に設定
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# カメラIDを表示するラベル
camera_id_label = tk.Label(root, text=f"使用中のカメラID: {camera_id}")
camera_id_label.pack()

def change_camera():
    global cap, camera_id
    if cap is not None:
        cap.release()
    cap, camera_id = open_camera(camera_id + 1)
    if cap is None:
        print("利用可能なカメラが見つかりません")
        camera_id_label.config(text="利用可能なカメラが見つかりません")
    else:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        camera_id_label.config(text=f"使用中のカメラID: {camera_id}")

# カメラ変更ボタン
change_button = tk.Button(root, text="カメラ変更", command=change_camera)
change_button.pack()

def on_distortion_scale(val):
    global D
    # スライダーの値を浮動小数点数に変換
    distortion_scale = float(val)
    # スライダーの値を歪み係数の最初の要素に適用し、他の要素は0にする
    # ここでは、単純化のために、スライダーが0の時に全ての歪みが無効になるようにしています
    D = np.array([distortion_scale, 0, 0, 0], dtype=np.float32)


distortion_slider = tk.Scale(root, from_=-5, to=5, resolution=0.01, orient=tk.HORIZONTAL, command=on_distortion_scale,length=300)
distortion_slider.set(-0.30)  # 初期値を適当に設定
distortion_slider.pack()

# 画像表示用のキャンバスを2つ作成
canvas_original = tk.Canvas(root, width=1280, height=720)
canvas_original.pack(side=tk.TOP)
canvas_corrected = tk.Canvas(root, width=1920, height=1080)
canvas_corrected.pack(side=tk.BOTTOM)

# カメラキャリブレーションパラメータ
K = np.array([[960, 0, 960], [0, 960, 540], [0, 0, 1]], dtype=np.float32)
D = np.array([0, 0, 0, 0], dtype=np.float32)

# グローバル変数として resize_scale を定義し、初期値を設定
resize_scale = 1.0

def update_frame():
    global cap, canvas_original, canvas_corrected, K, D
    if cap is not None:
        ret, frame = cap.read()
        if ret:
            # 元の画像を表示
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_original = Image.fromarray(frame_rgb)
            imgtk_original = ImageTk.PhotoImage(image=img_original)
            canvas_original.create_image(0, 0, anchor=tk.NW, image=imgtk_original)
            canvas_original.image = imgtk_original

            # 画像の中心を基準に1920x1080に余白を追加
            margin_frame = add_margin(frame, 180, 320, 180, 320, (0, 0, 0))

            # 魚眼歪み補正を毎フレーム更新
            map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3, dtype=np.float32), K, margin_frame.shape[1::-1], cv2.CV_16SC2)
            undistorted_img = cv2.remap(margin_frame, map1, map2, interpolation=cv2.INTER_LINEAR)
            undistorted_img_rgb = cv2.cvtColor(undistorted_img, cv2.COLOR_BGR2RGB)

            #1920x1080 -> 1600×820にクロップ (画像の中心が基準)
            #undistorted_img_rgb = undistorted_img_rgb[130:950, 160:1760]
            

            img_corrected = Image.fromarray(undistorted_img_rgb)
            imgtk_corrected = ImageTk.PhotoImage(image=img_corrected)
            canvas_corrected.create_image(0, 0, anchor=tk.NW, image=imgtk_corrected)
            canvas_corrected.image = imgtk_corrected

        root.after(20, update_frame)


# 最初にupdate_frameをスケジュール
root.after(0, update_frame)

# Tkinterイベントループを開始
root.mainloop()
