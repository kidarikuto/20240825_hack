import face_recognition
import cv2
import numpy as np
import os

# フォルダ内のすべての画像ファイルを読み込む
def load_known_faces(directory):
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
            # 画像のパスと名前を取得
            image_path = os.path.join(directory, filename)
            name = os.path.splitext(filename)[0]

            # 画像を読み込み、顔の特徴値を取得
            image = face_recognition.load_image_file(image_path)
            face_encoding = face_recognition.face_encodings(image)[0]

            # 取得した特徴値と名前をリストに追加
            known_face_encodings.append(face_encoding)
            known_face_names.append(name)

    return known_face_encodings, known_face_names

# 画像の保存されているフォルダを指定
directory = "images"
known_face_encodings, known_face_names = load_known_faces(directory)

# Webカメラを使用して顔認識を行う
video_capture = cv2.VideoCapture(0)

while True:
    _, frame = video_capture.read()
    rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        # 情報を描画
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_TRIPLEX, 1.0, (255, 255, 255), 2)

    cv2.imshow('WebCam', frame)

    # 終了(qキー)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()