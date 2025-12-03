import os  # ファイルやディレクトリ操作用
import boto3  # AWS SDK for Python。S3へのアクセスに使用
import mimetypes  # ファイルのMIMEタイプ判定用
from botocore.exceptions import ClientError  # S3操作での例外処理用

# --- 設定 ---
bucket_name = "webesite2025pracicefujii"  # アップロード先のS3バケット名
region_name = "us-east-1"                  # S3バケットのリージョン

# スクリプトの場所を取得して、そこを基準に website フォルダのパスを作成
script_dir = os.path.dirname(os.path.abspath(__file__))  # このスクリプトの絶対パス
upload_dir = os.path.join(script_dir, "website")         # websiteフォルダへの絶対パス

# --- S3クライアント作成 ---
# 指定リージョンに接続するS3クライアントを作成
s3 = boto3.client("s3", region_name=region_name)

def upload_folder_to_s3(local_dir, bucket):
    """
    指定フォルダ内のファイルを再帰的にS3にアップロードする関数。
    HTML/CSS/JS/画像などのMIMEタイプも自動設定される。
    """
    # フォルダの存在チェック
    if not os.path.exists(local_dir):
        print(f"Error: Upload folder does not exist: {local_dir}")  # 存在しなければエラー表示
        return

    uploaded_files = 0  # アップロード成功したファイル数をカウント

    # os.walkでフォルダを再帰的に探索
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            # ローカルファイルの絶対パス
            local_path = os.path.join(root, file)

            # S3上での相対パスを作成（websiteフォルダを基準に）
            relative_path = os.path.relpath(local_path, local_dir)

            # Windows環境ではバックスラッシュをスラッシュに置換
            s3_path = relative_path.replace("\\", "/")  

            # MIMEタイプを自動判定（ブラウザで正しく表示されるように設定）
            content_type, _ = mimetypes.guess_type(local_path)
            if content_type is None:  # 判定できない場合はバイナリとして扱う
                content_type = "binary/octet-stream"

            try:
                # ファイルをS3にアップロード
                # ExtraArgsでContentTypeを設定することでブラウザでHTMLがダウンロードされないようにする
                s3.upload_file(
                    local_path,
                    bucket,
                    s3_path,
                    ExtraArgs={"ContentType": content_type}
                )
                # アップロード成功時のログ出力
                print(f"Uploaded: {local_path} → s3://{bucket}/{s3_path} (ContentType: {content_type})")
                uploaded_files += 1  # カウントを増やす
            except ClientError as e:  # アップロード失敗時
                print(f"Failed to upload {local_path}: {e}")  # エラーログ出力

    # アップロード結果の表示
    if uploaded_files == 0:
        print("Warning: No files were uploaded.")  # ファイルが一つもアップロードされなかった場合
    else:
        print(f"Upload completed: {uploaded_files} files uploaded.")  # 成功件数を表示

    # アップロード完了後、静的サイトURLを出力
    website_url = f"http://{bucket}.s3-website-{region_name}.amazonaws.com"
    print(f"Access your website at: {website_url}")  # ブラウザでアクセス可能なURLを表示

# --- スクリプト直接実行時の処理 ---
if __name__ == "__main__":
    # 指定したフォルダをS3にアップロード
    upload_folder_to_s3(upload_dir, bucket_name)
