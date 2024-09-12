import face_recognition
import cv2
import numpy as np
import os
from collections import deque
import time

# フォルダ内のすべての画像ファイルを読み込む
def load_known_faces(directory):
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
            image_path = os.path.join(directory, filename)
            name = os.path.splitext(filename)[0]
            image = face_recognition.load_image_file(image_path)
            face_encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(face_encoding)
            known_face_names.append(name)
    return known_face_encodings, known_face_names

# 画像の保存されているフォルダを指定
directory = "images"
known_face_encodings, known_face_names = load_known_faces(directory)

# Webカメラを使用して顔認識を行う
video_capture = cv2.VideoCapture(0)

# 顔の過去の位置と状態を記録する辞書
position_history = {}
entry_exit_state = {}
last_seen_time = {}

# フレームの幅
frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))

# 閾値設定
disappear_threshold = 3  # 顔が消失しても許容する秒数

# 最後の入退室判断時間を記録
last_event_time = {}

while True:
    _, frame = video_capture.read()
    rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    current_time = time.time()

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        # 顔の位置を追跡
        if name not in position_history:
            position_history[name] = deque(maxlen=1)
            last_seen_time[name] = current_time
        
        position_history[name].append(left)

        # フレームの左端に見切れた場合、退室を判定
        if left < 50:  # 左端に顔の「left」座標が見切れたとき
            if entry_exit_state.get(name) != "exited":
                print(f"{name} 退室")
                entry_exit_state[name] = "exited"
                last_event_time[name] = current_time

        # フレームの右端に見切れた場合、入室を判定
        elif right > frame_width - 50:  # 右端に顔の「right」座標が見切れたとき
            if entry_exit_state.get(name) != "entered":
                print(f"{name} 入室")
                entry_exit_state[name] = "entered"
                last_event_time[name] = current_time
        
        # 顔が検知された時間を更新
        last_seen_time[name] = current_time

    # 顔が一定時間以上検知されなかった場合、データをクリア
    for name in list(last_seen_time.keys()):
        if current_time - last_seen_time[name] > disappear_threshold:
            del position_history[name]
            del last_seen_time[name]

    # 情報を描画
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_TRIPLEX, 1.0, (255, 255, 255), 2)

    cv2.imshow('WebCam', frame)

    # 終了(qキー)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
