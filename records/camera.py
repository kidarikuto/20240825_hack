
import cv2
import face_recognition
import numpy as np
import os

class VideoCamera(object):
    def __init__(self):
        # カメラ有効化/初期設定
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))

        # カスケード分類器設定
        self.cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
        
        # 顔認識用の設定
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces("FacialRecognition/images")

    def __del__(self):
        # カメラ停止
        self.video.release()

    def load_known_faces(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
                image_path = os.path.join(directory, filename)
                name = os.path.splitext(filename)[0]
                image = face_recognition.load_image_file(image_path)
                face_encoding = face_recognition.face_encodings(image)[0]
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(name)

    def get_frame(self):
        # 1フレーム取得
        ret, image = self.video.read()
        if not ret:
            return None
        
        # 顔認識処理
        rgb_frame = np.ascontiguousarray(image[:, :, ::-1])
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]

            # 顔画像周辺に枠を描画
            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(image, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_TRIPLEX, 1.0, (255, 255, 255), 2)

        # byteデータに変換
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
