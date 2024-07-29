# ベースイメージとしてPythonを使用
FROM python:3.9

# 作業ディレクトリを作成
WORKDIR /app

# 必要なファイルをコピー
COPY requirements.txt requirements.txt
COPY . .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# ポートを設定
EXPOSE 8000

# アプリケーションを起動
CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
