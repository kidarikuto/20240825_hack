import base64
import io
import os

import matplotlib
matplotlib.use("Agg")  # 非GUIベースのバックエンドを使用
import matplotlib.font_manager as fm
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import StreamingHttpResponse
# LoginRequiredMixinを継承すると
# ログインしていないユーザーがビューにアクセスを試みるとログインページにリダイレクトする
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators import gzip
from django.views.decorators.clickjacking import xframe_options_exempt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor

from .camera import VideoCamera
from .models import EntryExitLog

User = get_user_model()


class LabStatusView(LoginRequiredMixin, View):
    def get(self, request):
        current_user_latest_log = EntryExitLog.objects.filter(user=request.user).order_by("-timestamp").first()
        if current_user_latest_log is None:
            current_user_status = "記録なし"
        elif current_user_latest_log.action == "IN":
            current_user_status = "入室中"
        else:
            current_user_status = "退室中"
        in_lab_user_count = (
            EntryExitLog.objects.filter(action="IN").count() - EntryExitLog.objects.filter(action="OUT").count()
        )
        all_user_latest_logs = EntryExitLog.objects.all().order_by("-timestamp")[:10]

        return render(
            request,
            "records/status.html",
            {
                "current_user_status": current_user_status,
                "in_lab_user_count": in_lab_user_count,
                "all_user_latest_logs": all_user_latest_logs,
            },
        )


class EnterExitToggleView(LoginRequiredMixin, View):
    # postリクエストが送信されたときに実行
    def post(self, request):
        current_user_latest_log = EntryExitLog.objects.filter(user=request.user).order_by("-timestamp").first()

        if current_user_latest_log is None or current_user_latest_log.action == "OUT":
            EntryExitLog.objects.create(user=request.user, action="IN")
        else:
            EntryExitLog.objects.create(user=request.user, action="OUT")

        return redirect("records:lab_status")


# kidaが作成
class LoadingView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "records/loading.html")


class LogGraphView(LoginRequiredMixin, View):
    def get(self, request):

        all_logs = EntryExitLog.objects.all()
        latest_logs = EntryExitLog.objects.all().order_by("-timestamp")[:10]
        in_lab_users = [log.user.username for log in latest_logs if log.action == "IN"]
        in_lab_count = len(all_logs.filter(action="IN")) - len(all_logs.filter(action="OUT"))

        # FIXME: 履歴を取得してデータ加工
        # users = ['user1', 'user2', 'user3', 'user4', 'user5']
        users = list(User.objects.all().values_list("username", flat=True))
        user_num = len(users)
        enter_log = [0 for i in range(user_num)]
        train_data = []
        # username 曜日　timerange 8個
        for log in all_logs:
            user_index = users.index(log.user.username)
            if log.action == "IN":  # 入室時間帯を記憶
                time = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                time = time.split(" ")
                # time=log.timestamp.split(" ")
                time = time[1].split(":")
                time = int(time[0])
                timerange = time // 3
                enter_log[user_index] = timerange
            elif log.action == "OUT":  # testデータの作成
                user_data = [log.user.username]
                # dt=datetime.strptime(log.timestamp,'%Y-%m-%d %H:%M:%S')
                # 曜日を取得 (0: 月曜日, 1: 火曜日, ..., 6: 日曜日)
                weekday_number = log.timestamp.weekday()
                user_data.append(weekday_number)

                # 時間帯を作成
                time = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                time = time.split(" ")
                time = time[1].split(":")
                time = int(time[0])
                exit_log = time // 3
                # hist=hist_list(enter_log[user_index],exit_log)
                hist = [0 for i in range(8)]
                for i in range(enter_log[user_index], exit_log + 1):
                    hist[i] = 1

                user_data += hist
                train_data.append(user_data)

        # FIXME: 学習してプロット
        learn_train_data = pd.DataFrame(
            train_data,
            columns=["name", "days of week", "0~3", "3~6", "6~9", "9~12", "12~15", "15~18", "18~21", "21~24"],
        )
        X = learn_train_data[["name", "days of week"]]
        y = learn_train_data[["0~3", "3~6", "6~9", "9~12", "12~15", "15~18", "18~21", "21~24"]]
        X = pd.get_dummies(X, columns=["name"])
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        # モデルの定義
        # model = MultiOutputRegressor(RandomForestRegressor())
        model = MultiOutputRegressor(XGBRegressor())
        model.fit(X_train, y_train)
        # 予測
        y_pred = model.predict(X_test)
        # 評価
        mse = mean_squared_error(y_test, y_pred)
        output_data = [
            pd.DataFrame([], columns=["0~3", "3~6", "6~9", "9~12", "12~15", "15~18", "18~21", "21~24"])
            for i in range(7)
        ]
        for i in range(7):
            for name in users:
                input_data = pd.DataFrame({"name": [name], "days of week": [i]})
                input_data = pd.get_dummies(input_data, columns=["name"])
                input_data = input_data.reindex(columns=X.columns, fill_value=0)
                prediction = pd.DataFrame(
                    model.predict(input_data),
                    columns=["0~3", "3~6", "6~9", "9~12", "12~15", "15~18", "18~21", "21~24"],
                )
                print(f"users:{name},予測: {prediction}")
                output_data[i] = pd.concat([output_data[i], prediction], ignore_index=True)
        result = pd.DataFrame([], columns=["0~3", "3~6", "6~9", "9~12", "12~15", "15~18", "18~21", "21~24"])
        for i in range(7):
            tmp_sum = output_data[i].sum()
            tmp_sum = pd.DataFrame(tmp_sum).T
            result = pd.concat([result, tmp_sum], ignore_index=True)
        print(f"{result=}")

        # FIXME: 日本語フォントを指定
        # jpn_fonts=list(np.sort([ttf for ttf in fm.findSystemFonts() if 'ipaexg' in ttf or 'msgothic' in ttf or 'japan' in ttf or 'ipafont' in ttf]))
        font_folder = "fonts/"
        jpn_fonts = list(
            np.sort(
                [
                    os.path.join(font_folder, ttf)
                    for ttf in os.listdir(font_folder)
                    if "ipaexg" in ttf or "msgothic" in ttf or "japan" in ttf or "ipafont" in ttf
                ]
            )
        )
        jpn_font = jpn_fonts[0]
        prop = fm.FontProperties(fname=jpn_font)

        plt.rcParams["font.family"] = prop.get_name()
        # ヒストグラムを保存するためのリスト
        plots = []
        weekdays = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]

        for i in range(len(result)):
            max_val_index = result.iloc[i].idxmax()

            # 色を指定 (A=透明度を含むRGBA形式)
            colors = ["red" if x == max_val_index else "blue" for x in result.iloc[i].index]
            colors = [(1, 0, 0.5, 0.7) if color == "red" else (0, 0.5, 1, 0.7) for color in colors]

            # 棒グラフの描画
            plt.figure(figsize=(8, 4))
            ax = plt.gca()  # gca()は現在の軸を取得する関数
            width = 0.8
            bar_roundness = 0.2  # 棒グラフの角の丸みを設定
            for j, (x, y) in enumerate(zip(result.iloc[i].index, result.iloc[i].values)):
                # 棒の位置を設定
                rect = patches.FancyBboxPatch(
                    (j - width / 2, 0),
                    width,
                    y,
                    boxstyle=f"round,pad=0.02,rounding_size={bar_roundness}",
                    linewidth=1,
                    facecolor=colors[j],
                    edgecolor=colors[j],
                )
                ax.add_patch(rect)  # バーをプロットに追加

            # 軸とタイトルの設定
            ax.set_xlim(-0.5, len(result.iloc[i].index) - 0.5)
            ax.set_ylim(0, max(result.iloc[i].values) + 1)
            ax.set_xticks(range(len(result.iloc[i].index)))  # X軸の目盛り位置を設定
            ax.set_xticklabels(result.iloc[i].index)
            # plt.title(f'{weekdays[i]}', weight='bold')
            # plt.xlabel('時間帯', weight='bold')
            # plt.ylabel('人数予測値', weight='bold', rotation="horizontal", labelpad=30)
            plt.xticks(rotation=0)
            plt.tight_layout()

            # 画像をバイナリデータに変換
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            # バイナリデータをbase64でエンコードしてHTMLで埋め込めるようにする
            graphic = base64.b64encode(image_png)
            graphic = graphic.decode("utf-8")
            plots.append(graphic)
            plt.close()

        print(jpn_font)
        plots_weekdays = zip(plots, weekdays)

        context = {
            "latest_logs": latest_logs,
            "in_lab_users": in_lab_users,
            "in_lab_count": in_lab_count,
            "plots_weekdays": plots_weekdays,
            "users": users,
        }
        return render(request, "records/graph.html", context)


def gen(camera):
    while True:
        # カメラ画像1フレーム取得
        frame = camera.get_frame()
        # 1フレームデータ返却
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


# records/face/
def index(request):
    return render(request, "records/index.html")


# records/face/capture/
# index内にインラインフレームで表示
@gzip.gzip_page
@xframe_options_exempt
def capture(request):
    return StreamingHttpResponse(gen(VideoCamera()), content_type="multipart/x-mixed-replace; boundary=frame")
