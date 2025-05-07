# lambda/index.py
import json
import os
import urllib.request # urllib.request をインポート
# import boto3
# import re  # 正規表現モジュールをインポート
# from botocore.exceptions import ClientError


# Lambda コンテキストからリージョンを抽出する関数
# def extract_region_from_arn(arn):
    # ARN 形式: arn:aws:lambda:region:account-id:function:function-name
   #  match = re.search('arn:aws:lambda:([^:]+):', arn)
    # if match:
        # return match.group(1)
    # return "us-east-1"  # デフォルト値

# グローバル変数としてクライアントを初期化（初期値）
# bedrock_client = None

# モデルID
# MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")
# Model_ID = os.environ.get("MODEL_ID","https://ba05-35-233-232-80.ngrok-free.app/generate")
# ★ ここに Google Colab で取得した ngrok の公開URLを設定します ★
COLAB_API_URL = "https://60e3-35-197-145-163.ngrok-free.app/generate"

# URLが設定されていない場合のエラーチェック (念のため)
#if not COLAB_API_URL or COLAB_API_URL == "https://ba05-35-233-232-80.ngrok-free.app/generate":
#	print("致命的エラー: Colab APIのURLが lambda/index.py に設定されていません！")

def lambda_handler(event, context):
# CORS Preflightリクエストへの対応 (OPTIONSメソッド)
    # API GatewayのProxy統合を使っている場合、ブラウザが事前にこのリクエストを送ることがある
#    if event.get('httpMethod') == 'OPTIONS':
#        return {
#            'statusCode': 200,
#            'headers': {
#                "Access-Control-Allow-Origin": "*",
#                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
#                "Access-Control-Allow-Methods": "OPTIONS,POST" # 許可するメソッド
#            },
#            'body': '' # OPTIONSリクエストに対するボディは空でOK
#        }

    try:
# --- Bedrockクライアントの初期化処理は不要なので削除 ---
 #--- コンテキストから実行リージョンを取得し、クライアントを初期化 ---
        # global bedrock_client
        ## if bedrock_client is None:
        #     region = extract_region_from_arn(context.invoked_function_arn)
        #     bedrock_client = boto3.client('bedrock-runtime', region_name=region)
        #     print(f"Initialized Bedrock client in region: {region}")

        print("Received event:", json.dumps(event))
        
        # Cognitoで認証されたユーザー情報を取得
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
       conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)
 #       print("Using model:", MODEL_ID)
        
        # 会話履歴を使用
        messages = conversation_history.copy()
        
        # ユーザーメッセージを追加
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Nova Liteモデル用のリクエストペイロードを構築
        # 会話履歴を含める
       # bedrock_messages = []
       Fast_API_messages = []
        for msg in messages:
            if msg["role"] == "user":
                Fast_API_messages.append({
                    "role": "user",
                    "content": [{"text": msg["content"]}]
                })
            elif msg["role"] == "assistant":
                Fast_API_messages.append({
                    "role": "assistant", 
                    "content": [{"text": msg["content"]}]
                })
        
        # invoke_model用のリクエストペイロード
        request_payload = {
            "messages": Fast_API_messages,
            "inferenceConfig": {
                "maxTokens": 512,
                "stopSequences": [],
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        print("Calling Bedrock invoke_model API with payload:", json.dumps(request_payload))
        
        # invoke_model APIを呼び出し
       # response = bedrock_client.invoke_model(
       #     modelId=MODEL_ID,
       #     body=json.dumps(request_payload),
       #     contentType="application/json"
       # )
        
        with  response = urlib.request.urlopen(
                                url = COLAB_API_URL,
                                                data = json.dumps(request_payload).encode('utf-8')
                                                                headers = {"Content-Type" : "application/json"},
                                                                                method = "POST"
                                                                                                )
           as response :
                      the HttpStatus = respons.getcode()


        # レスポンスを解析
       response_body = json.loads(response['body'].read())
       #print("Bedrock response:", json.dumps(response_body, default=str))
        print("Fast_API response", json.dumps(response_body, default-str))

        # 応答の検証
        if not response_body.get('output') or not response_body['output'].get('message') or not response_body['output']['message'].get('content'):
            raise Exception("No response content from the model")
        
        # アシスタントの応答を取得
        assistant_response = response_body['output']['message']['content'][0]['text']
        
        # アシスタントの応答を会話履歴に追加
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        
# --- ここからが Colab API を呼び出す処理 ---
#        ai_response_text = "すみません、AIモデルからの応答取得に失敗しました。" # デフォルトのエラーメッセージ
#        success = False # API呼び出し成功フラグ

 #       if not COLAB_API_URL or COLAB_API_URL == "https://e885-34-83-214-173.ngrok-free.app/generate":
  #           ai_response_text = "エラー: Lambda関数内でAPIエンドポイントURLが設定されていません。"
   #     else:
            # ColabのFastAPIが受け付ける形式でデータを作成 (promptキーを持つJSON)
    #        request_data = {
     #           "prompt": message
                # 会話履歴を使う場合は、Colab APIの仕様に合わせてここに追加する
                # 例: "history": conversation_history
      #      }
            # Python辞書をJSON形式のバイト列に変換
       #     request_body = json.dumps(request_data).encode('utf-8')

            # リクエストオブジェクトを作成
        #    req = urllib.request.Request(
         #       COLAB_API_URL,
          #      data=request_body,
                # ヘッダーでJSON形式であることを伝える
           #     headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                # ColabのFastAPIエンドポイントに合わせてメソッドを指定 (通常はPOST)
            #    method='POST'
           # )

            #print(f"Sending request to Colab API: {COLAB_API_URL}")
#            response_body_text = "" # エラー時のログ出力用
 #           try:
                # APIにリクエストを送信し、レスポンスを受け取る (タイムアウトを30秒に設定)
  #              with urllib.request.urlopen(req, timeout=30) as response:
   #                 print(f"Received response status: {response.status}")
                    # レスポンスボディを読み取り、UTF-8でデコード
    #                response_body_text = response.read().decode('utf-8')

     #               if response.status == 200:
                        # JSONとして解釈
      #                  response_data = json.loads(response_body_text)

                        # Colab APIのレスポンスJSONからAIの返答部分を取り出す
                        # (キー名はColab側のFastAPIの実装に合わせる。例: "generated_text")
       #                 if "generated_text" in response_data:
        #                   ai_response_text = response_data.get("generated_text")
         #                  success = True # 応答取得成功
          #                 print(f"Successfully got response from Colab: {ai_response_text[:100]}...")
           #             else:
            #               ai_response_text = "応答の形式が正しくありません (キー 'generated_text' が見つかりません)。"
             #              print(f"Invalid response format from Colab: {response_body_text}")

              #      else:
                        # APIが200以外のステータスコードを返した場合
               #         ai_response_text = f"Colab API エラー: ステータスコード {response.status}, Body: {response_body_text}"
                #        print(ai_response_text)

#            except urllib.error.HTTPError as e:
                # urllib.error.urlopenが投げる可能性のあるHTTPエラー (4xx, 5xx)
 #               print(f"Error calling Colab API (HTTPError): {e}")
  #              try:
   # エラーレスポンスのボディも読める場合がある
   #                 error_body = e.read().decode('utf-8', errors='ignore')
    #                ai_response_text = f"AIモデルへの接続でHTTPエラーが発生しました (コード: {e.code})。詳細: {error_body}"
     #           except Exception:
      #               ai_response_text = f"AIモデルへの接続でHTTPエラーが発生しました (コード: {e.code})。"
       #     except urllib.error.URLError as e:
        #        # ネットワークレベルのエラー (タイムアウト、名前解決不可、接続拒否など)
         #       print(f"Error calling Colab API (URLError): {e}")
          #      ai_response_text = f"AIモデルへの接続に失敗しました ({e.reason})。Colabサーバーが起動しているか、URLが正しいか、ネットワーク経路を確認してください。"
           # except json.JSONDecodeError as e:
                 # 正常ステータス(200)だが、レスポンスがJSONではなかった場合
            #     print(f"Error decoding JSON response from Colab API: {e}")
             #    print(f"Raw response: {response_body_text}") # 生のレスポンスを出力
              #   ai_response_text = "AIモデルからの応答を正しく処理できませんでした (JSON Decode Error)。"
  #          except Exception as e:
                # その他の予期せぬエラー (タイムアウト含む TimeoutError など)
   #             print(f"Unexpected error calling Colab API: {e}")
    #            import traceback
     #           traceback.print_exc() # スタックトレースを出力
      #          ai_response_text = f"AIモデルの呼び出し中に予期せぬエラーが発生しました: {type(e).__name__}"
        # --- Colab API 呼び出し処理 ここまで ---



        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }


