# Microsoft Graph Parallel Requests in Python

このサンプルでは、MS Graph の以下の API へのリクエストを並列で処理することで、効率的に結果を取得します。

* [List users](https://docs.microsoft.com/en-us/graph/api/user-list?view=graph-rest-beta)
* [List signIns](https://docs.microsoft.com/en-us/graph/api/signin-list?view=graph-rest-beta)

## Prerequisites

### 実行環境
* Python (>= 3.5)
* pip
* Azure AD に登録されているアプリ（以下のアクセス許可を付与）
  * User.Read.All
  * Directory.Read.All
  * AuditLog.Read.All


## Installation

```bash
pip install -r requirements.txt
```

## Usage

### 設定

1. `settings.template.py` を `settings.py` にコピーします。
2. `settings.py` を設定します。

|  parameters                |  description  |
| -------------------------- | ------------- |
|  TENANT_NAME               |  Azure AD テナント名  |
|  CLIENT_ID                 |  クライアント ID  |
|  CLIENT_SECRET             |  クライアント シークレット  |
|  MULTI_THREAD_ENABLED      |  True の場合、マルチスレッドを有効化する  |
|  MULTI_THREAD_MAX_WORKERS  |  最大スレッド数  |
|  LOGGING_ENABLED           |  True の場合、Graph API への各リクエストのステータスを出力する  |
|  OUTPUT_FILE               |  結果の出力先ファイル名  |

### ユーザー一覧の取得

``` bash
python get_users.py
```

### サインインの取得
```bash
python get_sign_ins.py
```

## Links

* [How to perform large scale operations efficiently using Microsoft Graph](https://myignite.techcommunity.microsoft.com/sessions/65997)
  * [Demo codes in C# (github repo)](https://github.com/piotrci/Microsoft-Graph-Efficient-Operations)
* [Microsoft Azure Active Directory Authentication Library (ADAL) for Python](https://github.com/AzureAD/azure-activedirectory-library-for-python)
* [Throttling guidance | Graph API concepts](https://msdn.microsoft.com/en-us/library/azure/ad/graph/howto/azure-ad-graph-api-throttling)