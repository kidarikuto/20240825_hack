import base64
# import csv
import io
# import math
# import random
# from collections import Counter
# from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')  # 非GUIベースのバックエンドを使用
import matplotlib.pyplot as plt
# import numpy as np
import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
# LoginRequiredMixinを継承すると
# ログインしていないユーザーがビューにアクセスを試みるとログインページにリダイレクトする
from django.shortcuts import redirect, render
from django.views import View
# from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor

from .models import EntryExitLog


class LabStatusView(LoginRequiredMixin, View):
    def get(self, request):
        current_user_latest_log = EntryExitLog.objects.filter(user=request.user).order_by('-timestamp').first()
        if current_user_latest_log is None:
            current_user_status = '記録なし'
        elif current_user_latest_log.action == 'IN':
            current_user_status = '入室中'
        else:
            current_user_status = '退室中'
        in_lab_user_count = EntryExitLog.objects.filter(action='IN').count() - EntryExitLog.objects.filter(action='OUT').count()
        all_user_latest_logs = EntryExitLog.objects.all().order_by('-timestamp')[:10]

        return render(request, 'records/status.html', {
            'current_user_status': current_user_status,
            'in_lab_user_count': in_lab_user_count,
            'all_user_latest_logs': all_user_latest_logs,
        })


class EnterExitToggleView(LoginRequiredMixin, View):
    # postリクエストが送信されたときに実行
    def post(self, request):
        current_user_latest_log = EntryExitLog.objects.filter(user=request.user).order_by('-timestamp').first()

        if current_user_latest_log is None or current_user_latest_log.action == 'OUT':
            EntryExitLog.objects.create(user=request.user, action='IN')
        else:
            EntryExitLog.objects.create(user=request.user, action='OUT')

        return redirect('records:lab_status')

# kidaが作成
class LogGraphView(View):
    def get(self, request):
        
        all_logs = EntryExitLog.objects.all()
        latest_logs = EntryExitLog.objects.all().order_by('-timestamp')[:10]
        in_lab_users = [
            log.user.username for log in latest_logs if log.action == 'IN'
        ]
        in_lab_count = len(all_logs.filter(action='IN'))-len(all_logs.filter(action='OUT'))

        # FIXME: 履歴を取得してデータ加工
        users = ['user1', 'user2', 'user3', 'user4', 'user5']
        user_num=len(users)
        enter_log=[0 for i in range(user_num)]
        train_data=[]
            # username 曜日　timerange 8個
        for log in all_logs:   
            user_index=users.index(log.user.username)
            if log.action=="IN":#入室時間帯を記憶
                time = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                time=time.split(" ")
                # time=log.timestamp.split(" ")
                time=time[1].split(":")
                time=int(time[0])
                timerange=time//3
                enter_log[user_index]=timerange
            elif log.action=="OUT":#testデータの作成
                user_data=[log.user.username]
                # dt=datetime.strptime(log.timestamp,'%Y-%m-%d %H:%M:%S')
                # 曜日を取得 (0: 月曜日, 1: 火曜日, ..., 6: 日曜日)
                weekday_number = log.timestamp.weekday()
                user_data.append(weekday_number)

                #時間帯を作成
                time = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                time=time.split(" ")
                time=time[1].split(":")
                time=int(time[0])
                exit_log=time//3
                # hist=hist_list(enter_log[user_index],exit_log)
                hist=[0 for i in range(8)]
                for i in range(enter_log[user_index],exit_log+1):
                    hist[i]=1
                
                user_data+=hist
                train_data.append(user_data)
        
        # FIXME: 学習してプロット
        learn_train_data=pd.DataFrame(train_data,columns=['name','days of week','0~3','3~6','6~9','9~12','12~15','15~18','18~21','21~24'])
        X = learn_train_data[['name', 'days of week']]
        y = learn_train_data[['0~3', '3~6', '6~9', '9~12', '12~15', '15~18', '18~21', '21~24']]
        X = pd.get_dummies(X, columns=['name'])
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        # モデルの定義
        # model = MultiOutputRegressor(RandomForestRegressor())
        model = MultiOutputRegressor(XGBRegressor())
        model.fit(X_train, y_train)
        # 予測
        y_pred = model.predict(X_test)
        # 評価
        mse = mean_squared_error(y_test, y_pred)
        output_data=[pd.DataFrame([],columns=['0~3','3~6','6~9','9~12','12~15','15~18','18~21','21~24']) for i in range(7)]
        for i in range(7):
            for name in users:
                input_data = pd.DataFrame({
                'name': [name],
                'days of week': [i]
                })
                input_data=pd.get_dummies(input_data,columns=['name'])
                input_data = input_data.reindex(columns=X.columns, fill_value=0)
                prediction = pd.DataFrame(model.predict(input_data),columns=['0~3','3~6','6~9','9~12','12~15','15~18','18~21','21~24'])
                print(f'users:{name},予測: {prediction}')
                output_data[i]=pd.concat([output_data[i],prediction],ignore_index=True)  
        result=pd.DataFrame([],columns=['0~3','3~6','6~9','9~12','12~15','15~18','18~21','21~24'])
        for i in range(7):
            tmp_sum=output_data[i].sum()
            tmp_sum=pd.DataFrame(tmp_sum).T
            result=pd.concat([result,tmp_sum],ignore_index=True)

        # グラフを作成        
        # ヒストグラムを保存するためのリスト
        plots = []
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i in range(len(result)):
            plt.figure(figsize=(8, 4))
            result.iloc[i].plot(kind='bar')
            plt.title(f'{weekdays[i]}')
            plt.xlabel('Range')
            plt.ylabel('Expected number of people')
            # 画像をバイナリデータに変換
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            # バイナリデータをbase64でエンコードしてHTMLで埋め込めるようにする
            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')
            plots.append(graphic)
            plt.close()

        context = {
            'latest_logs': latest_logs,
            'in_lab_users': in_lab_users,
            'in_lab_count': in_lab_count,
            'plots': plots,
        }
        return render(request, 'records/graph.html', context)
