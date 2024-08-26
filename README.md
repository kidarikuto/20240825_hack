<div align="center">
  <img src="https://github.com/user-attachments/assets/e473e579-935b-48c4-ab40-689f26ee1f64">
  <p><b>ラボウォッチ - 研究室の入室状況を管理・閲覧できるサービス</b></p>
</div>
<hr>


## 概要・背景
<div style="display: flex; align-items: center; justify-content: space-around;">
  <img src="https://github.com/user-attachments/assets/85bd6526-30b8-4536-ae2e-cf13a1612772" width="45%">
  <img src="https://github.com/user-attachments/assets/0ce9ae76-4232-4a88-b364-fe3eaee24cfe" width="45%">
</div>


## 各機能紹介
<div style="display: flex; align-items: center; justify-content: space-around;">
  <img src="https://github.com/user-attachments/assets/21e4d728-dc11-48c6-9f81-499ac791de51" width="45%">
  <img src="https://github.com/user-attachments/assets/b85deec9-5c6d-41cc-b581-904520b44c7e" width="45%">
  <img src="https://github.com/user-attachments/assets/96b5a514-99f3-4806-813a-d3834ba1834e" width="45%">
  <img src="https://github.com/user-attachments/assets/4ff198b1-7dd4-463a-8030-eabce172c6aa" width="45%">
</div>


## 使用技術
| カテゴリー | 技術スタック |
| --- | --- |
| バックエンドフレームワーク | <img src="https://img.shields.io/badge/-Django-092E20.svg?logo=django&style=flat"> |
| バックエンド言語 | <img src="https://img.shields.io/badge/-Python-F9DC3E.svg?logo=python&style=flat"> |
| フロントエンドフレームワーク | <img src="https://img.shields.io/badge/-Bootstrap-563D7C.svg?logo=bootstrap&style=flat"> |
| フロントエンド言語 | <img src="https://img.shields.io/badge/-HTML5-333.svg?logo=html5&style=flat"> <img src="https://img.shields.io/badge/-CSS3-1572B6.svg?logo=css3&style=flat"> <img src="https://img.shields.io/badge/Javascript-276DC3.svg?logo=javascript&style=flat"> |
| データベース | <img src="https://img.shields.io/badge/-SQLite3-3a78b8.svg?logo=sqlite&style=flat"> |
| バージョン管理 | <img src="https://img.shields.io/badge/-Git-ffdab9.svg?logo=git&style=flat"> <img src="https://img.shields.io/badge/-GitHub-181717.svg?logo=github&style=flat"> |
| 機械学習 | <img src="https://img.shields.io/badge/-Matplotlib-3776AB.svg?logo=Matplotlib&style=flat"> <img src="https://img.shields.io/badge/-NumPy-013243.svg?logo=numpy&style=flat"> <img src="https://img.shields.io/badge/-Pandas-150458.svg?logo=Pandas&style=flat"> <img src="https://img.shields.io/badge/-Scikit%20Learn-F7931E.svg?logo=scikit-learn&style=flat"> <img src="https://img.shields.io/badge/-XGBoost-FF6600.svg?logo=xgboost&style=flat"> |
| 顔認識 | <img src="https://img.shields.io/badge/-OpenCV-5C3EE8.svg?logo=opencv&style=flat"> <img src="https://img.shields.io/badge/-Face%20Recognition-4E9A06.svg?logo=opencv&style=flat"> <img src="https://img.shields.io/badge/-NumPy-013243.svg?logo=numpy&style=flat"> |
| リンター・フォーマッター | <img src="https://img.shields.io/badge/-Black-000000.svg?logo=black&style=flat"> <img src="https://img.shields.io/badge/-Flake8-3776AB.svg?logo=python&style=flat"> <img src="https://img.shields.io/badge/-isort-ef8336.svg?logo=python&style=flat"> |
| パッケージ管理 | <img src="https://img.shields.io/badge/-pip-3775A9.svg?logo=pypi&style=flat"> |


## 要件
- git
- python
  - virtualenv
  - pip
- libomp
- cmake


## 使い方
```bash
# リポジトリをクローン
$ git clone https://github.com/harune-pg/geek_hackathon_vol13_team22.git
$ cd geek_hackathon_vol13_team22

# 仮想環境を構築
$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt

# マイグレーションを実施
(venv) $ python manage.py migrate

# 初期データを読み込む
(venv) $ python manage.py loaddata accounts/fixture/fixture1.json records/fixture/fixture2.json

# アプリケーションを起動
(venv) $ python manage.py runserver
```

- サインアップ画面
  - http://127.0.0.1:8000/accounts/signup/


## 今後の機能
[issues](https://github.com/harune-pg/geek_hackathon_vol13_team22/issues)


## 備考
[ハッカソン主催公式Xの投稿](https://x.com/geek_pjt/status/1827625601286668299?s=46)

<details>
<summary>感想</summary>

面識なし、開発経験なし、Git初挑戦、Django初挑戦などの背景が各メンバーにありながら、構想から約1週間で作り上げました！
- よかった点
  - 即席チームで初ハッカソンなので緊張してたが、上手く連携を取り、形にする所まで行けたのは良かった
- 課題
  - 締め切りギリギリだったので、日程調整を気をつけたい

</details>

<details>
<summary>終了の仕方</summary>

```bash
# アプリケーションを終了
^C

# 仮想環境を終了
(venv) $ deactivate
```

</details>


## 製作者
- [@harune-pg](https://github.com/harune-pg)
- [@kidarikuto](https://github.com/kidarikuto)
- [@Yukumo-Job](https://github.com/Yukumo-Job)


## 協力者
- Aya
