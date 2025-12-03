# timeをインポート
import time
# jsonをインポート
import json
# boto3をインポート
import boto3
# ロギングをインポート
import logging
# boto3例外クラスのClientErrorをインポート
from botocore.exceptions import ClientError

# リージョン
region_name = "us-east-1"
# バケット名（※任意に変更してください）
bucket = "webesite2025pracicefujii"


try:
    # S3接続用クライアント
    s3 = boto3.client("s3", region_name=region_name)

    # S3バケットを作成
    s3.create_bucket(
        Bucket=bucket
    )
    # 設定が完了するまで1秒間待機
    time.sleep(1)

    # ブロックパブリックアクセスを設定
    s3.put_public_access_block(
        Bucket=bucket,
        # すべて無効とする
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        },
    )
    # 設定が完了するまで1秒間待機
    time.sleep(1)


    # バケットポリシーをJSON文字列として設定
    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject",],
            "Resource": [f"arn:aws:s3:::{bucket}/*",]
        },]
    })
    # バケットポリシーを設定
    s3.put_bucket_policy(
        Bucket=bucket,
        Policy=policy
    )

    # 静的ウェブサイトに設定するエラーページとトップページ
    website_configuration = {
        "ErrorDocument": {"Key": "error.html"},
        "IndexDocument": {"Suffix": "index.html"}
    }
    # 静的ウェブホスティングを設定
    s3.put_bucket_website(
        Bucket=bucket,
        WebsiteConfiguration=website_configuration
    )

    # ウェブサイトエンドポイントを表示
    print(f"http://{bucket}.s3-website-{region_name}.amazonaws.com")

# クライアントエラーキャッチ
except ClientError as e:
    # エラー出力
    logging.error(e)
