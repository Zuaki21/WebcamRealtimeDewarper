import cv2

def main():
    # カメラデバイスを開く（0は通常デフォルトのWebカメラを指す）
    cap = cv2.VideoCapture(1)

    # 解像度を1280x720に設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("カメラを開けませんでした。")
        exit()

    try:
        while True:
            # フレームをキャプチャ
            ret, frame = cap.read()

            # フレームが正しく読み取れたかの確認
            if not ret:
                print("フレームを取得できませんでした。")
                break

            # フレームを画面に表示
            cv2.imshow('WebCamera', frame)

            # 'q'を押したらループから抜ける
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # 終了処理
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
