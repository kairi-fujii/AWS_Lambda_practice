# boto3をインポート
import boto3
# ロギングをインポート
import logging
from botocore.exceptions import ClientError

# --- 設定 ---
region_name = "us-east-1"      # DynamoDB のリージョン
table_name = "products"        # 商品テーブル名

try:
    # DynamoDB 接続用クライアントを作成
    dynamodb = boto3.client("dynamodb", region_name=region_name)

    try:
        # DynamoDB テーブルを作成
        response = dynamodb.create_table(
            TableName=table_name,
            # プライマリキーは商品ID（id）
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"}  # HASH=パーティションキー
            ],
            # GSI で使う属性を事前に定義
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "N"},    # プライマリキー
                {"AttributeName": "jan", "AttributeType": "S"}    # GSI 用
            ],
            # 読み書きキャパシティ（学習用に小さめ）
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
            # JANコード検索用の GSI を追加
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "JanIndex",  # GSI名
                    "KeySchema": [
                        {"AttributeName": "jan", "KeyType": "HASH"}  # GSIのパーティションキー
                    ],
                    "Projection": {"ProjectionType": "ALL"},       # 全属性を取得可能にする
                    "ProvisionedThroughput": {"ReadCapacityUnits": 1, "WriteCapacityUnits": 1}
                }
            ]
        )

        print(f"{table_name} テーブルを作成しました")

    # テーブルが既に存在する場合の例外処理
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"{table_name} テーブルは既に存在しています")
        else:
            raise e

# DynamoDB クライアント接続失敗など
except ClientError as e:
    logging.error(e)

