# GENFLUX Backend API Reference - External API

> **📘 Note**: このドキュメントは、GENFLUX Python SDK が内部で使用する REST API の仕様です。  
> SDK の使い方については、[Python SDK API Reference](./API_REFERENCE.md) を参照してください。

## 📚 関連ドキュメント

- **[API_REFERENCE.md](./API_REFERENCE.md)**: Python SDK Client の使い方
- **[QUICKSTART.md](./QUICKSTART.md)**: 最初の評価を実行

---


**Version**: 1.0.0


GENFLUX Platform Backend API

## API Surfaces

### Frontend Integration API (`/api/v1/platform`)
- Supabase JWT認証
- ユーザー管理、課金、使用量確認など

### External API (`/api/v1/external`)
- Project API Key認証
- 評価、RedTeam、ポリシーチェック機能


---

## 📋 目次

- [configs](#configs)
- [credits](#credits)
- [external](#external)
- [jobs](#jobs)
- [reports](#reports)
- [スキーマ定義](#スキーマ定義)

---

## 認証

Project API Key認証を使用します（`X-API-Key` ヘッダー）。

**認証ヘッダー例**:
```
X-API-Key: <Your Project API Key>
```

Project API Keyは、Platform API の `/api/v1/platform/api-keys` エンドポイントで作成できます。

---

## configs

### `GET` /api/v1/external/configs/

**概要**: List Configs

**詳細**:
```
設定一覧を取得

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
    - TODO: ページネーション
```



**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/ConfigListResponse"
}
```

---

### `POST` /api/v1/external/configs/

**概要**: Create Config

**詳細**:
```
設定を作成

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_id, user_id はAPI Keyから自動取得
```


**リクエストボディ**:

Content-Type: `application/json`

```json
{
  "$ref": "#/components/schemas/ConfigCreate"
}
```

**レスポンス**:

- **201**: Successful Response

```json
{
  "$ref": "#/components/schemas/ConfigResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `GET` /api/v1/external/configs/{config_id}

**概要**: Get Config

**詳細**:
```
設定を取得

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `config_id` | string | path | ✓ | - |


**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/ConfigResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `PUT` /api/v1/external/configs/{config_id}

**概要**: Update Config

**詳細**:
```
設定を更新

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `config_id` | string | path | ✓ | - |

**リクエストボディ**:

Content-Type: `application/json`

```json
{
  "$ref": "#/components/schemas/ConfigUpdate"
}
```

**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/ConfigResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `DELETE` /api/v1/external/configs/{config_id}

**概要**: Delete Config

**詳細**:
```
設定を削除

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `config_id` | string | path | ✓ | - |


**レスポンス**:

- **204**: Successful Response

- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

## credits

### `POST` /api/v1/external/credits/consume

**概要**: Consume Credits

**詳細**:
```
クレジットを消費（テスト用）。

Args:
    request_body: クレジット消費リクエスト
    request: FastAPI Requestオブジェクト（ミドルウェアで使用）
    tenant_id: テナントID（API Key認証から取得）
    db: データベースセッション

Returns:
    ConsumeCreditsResponse: 消費結果

Raises:
    HTTPException: 残高不足の場合（400）
```


**リクエストボディ**:

Content-Type: `application/json`

```json
{
  "$ref": "#/components/schemas/ConsumeCreditsRequest"
}
```

**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/ConsumeCreditsResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

## external

### `GET` /api/v1/external/configs/

**概要**: List Configs

**詳細**:
```
設定一覧を取得

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
    - TODO: ページネーション
```



**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/ConfigListResponse"
}
```

---

### `POST` /api/v1/external/configs/

**概要**: Create Config

**詳細**:
```
設定を作成

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_id, user_id はAPI Keyから自動取得
```


**リクエストボディ**:

Content-Type: `application/json`

```json
{
  "$ref": "#/components/schemas/ConfigCreate"
}
```

**レスポンス**:

- **201**: Successful Response

```json
{
  "$ref": "#/components/schemas/ConfigResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `GET` /api/v1/external/configs/{config_id}

**概要**: Get Config

**詳細**:
```
設定を取得

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `config_id` | string | path | ✓ | - |


**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/ConfigResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `PUT` /api/v1/external/configs/{config_id}

**概要**: Update Config

**詳細**:
```
設定を更新

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `config_id` | string | path | ✓ | - |

**リクエストボディ**:

Content-Type: `application/json`

```json
{
  "$ref": "#/components/schemas/ConfigUpdate"
}
```

**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/ConfigResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `DELETE` /api/v1/external/configs/{config_id}

**概要**: Delete Config

**詳細**:
```
設定を削除

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `config_id` | string | path | ✓ | - |


**レスポンス**:

- **204**: Successful Response

- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `POST` /api/v1/external/credits/consume

**概要**: Consume Credits

**詳細**:
```
クレジットを消費（テスト用）。

Args:
    request_body: クレジット消費リクエスト
    request: FastAPI Requestオブジェクト（ミドルウェアで使用）
    tenant_id: テナントID（API Key認証から取得）
    db: データベースセッション

Returns:
    ConsumeCreditsResponse: 消費結果

Raises:
    HTTPException: 残高不足の場合（400）
```


**リクエストボディ**:

Content-Type: `application/json`

```json
{
  "$ref": "#/components/schemas/ConsumeCreditsRequest"
}
```

**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/ConsumeCreditsResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `POST` /api/v1/external/jobs/

**概要**: Create Job

**詳細**:
```
ジョブを作成

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_id, user_id はAPI Keyから自動取得
    - config_idが省略された場合、デフォルトConfigを自動作成/使用
    - Job作成後に Worker を自動起動（Cloud Run Jobs またはポーリング）
```


**リクエストボディ**:

Content-Type: `application/json`

```json
{
  "$ref": "#/components/schemas/JobCreate"
}
```

**レスポンス**:

- **201**: Successful Response

```json
{
  "$ref": "#/components/schemas/JobResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `GET` /api/v1/external/jobs/

**概要**: List Jobs

**詳細**:
```
ジョブ一覧を取得

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
    - TODO: ページネーション
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `status_filter` |  | query |  | - |
| `type_filter` |  | query |  | - |


**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/JobListResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `GET` /api/v1/external/jobs/{job_id}

**概要**: Get Job

**詳細**:
```
ジョブを取得

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
    - TODO: progress情報の計算
    - TODO: summary_metrics の生成
    - TODO: dashboard_url の生成
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `job_id` | string | path | ✓ | - |


**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/JobResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `POST` /api/v1/external/jobs/{job_id}/cancel

**概要**: Cancel Job

**詳細**:
```
ジョブをキャンセル

実行中または待機中のジョブをキャンセルします。
完了済みまたは既にキャンセル済みのジョブはキャンセルできません。

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
    - TODO: Worker停止シグナル送信（Cloud Run Jobs API）
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `job_id` | string | path | ✓ | - |


**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/JobCancelResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `GET` /api/v1/external/reports/{report_id}

**概要**: Get Report

**詳細**:
```
レポートを取得

Args:
    report_id: レポートID (= Job ID)
    tenant_id: Tenant ID (API Keyから自動取得)
    view: 表示レベル
        - summary: CI判定用の指標のみ
        - details: 失敗ケース上位N件 + カテゴリ別集計

Returns:
    レポート情報

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - report_id = job_id (Executionテーブルから動的生成)
    - 完了済みJobのみレポート取得可能
    - PIIマスキングは実装済み（各フィールドで処理）
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `report_id` | string | path | ✓ | - |
| `view` | string | query |  | 表示レベル |


**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/ReportResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

## jobs

### `POST` /api/v1/external/jobs/

**概要**: Create Job

**詳細**:
```
ジョブを作成

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_id, user_id はAPI Keyから自動取得
    - config_idが省略された場合、デフォルトConfigを自動作成/使用
    - Job作成後に Worker を自動起動（Cloud Run Jobs またはポーリング）
```


**リクエストボディ**:

Content-Type: `application/json`

```json
{
  "$ref": "#/components/schemas/JobCreate"
}
```

**レスポンス**:

- **201**: Successful Response

```json
{
  "$ref": "#/components/schemas/JobResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `GET` /api/v1/external/jobs/

**概要**: List Jobs

**詳細**:
```
ジョブ一覧を取得

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
    - TODO: ページネーション
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `status_filter` |  | query |  | - |
| `type_filter` |  | query |  | - |


**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/JobListResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `GET` /api/v1/external/jobs/{job_id}

**概要**: Get Job

**詳細**:
```
ジョブを取得

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
    - TODO: progress情報の計算
    - TODO: summary_metrics の生成
    - TODO: dashboard_url の生成
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `job_id` | string | path | ✓ | - |


**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/JobResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

### `POST` /api/v1/external/jobs/{job_id}/cancel

**概要**: Cancel Job

**詳細**:
```
ジョブをキャンセル

実行中または待機中のジョブをキャンセルします。
完了済みまたは既にキャンセル済みのジョブはキャンセルできません。

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - tenant_idはAPI Keyから自動取得
    - TODO: Worker停止シグナル送信（Cloud Run Jobs API）
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `job_id` | string | path | ✓ | - |


**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/JobCancelResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---

## reports

### `GET` /api/v1/external/reports/{report_id}

**概要**: Get Report

**詳細**:
```
レポートを取得

Args:
    report_id: レポートID (= Job ID)
    tenant_id: Tenant ID (API Keyから自動取得)
    view: 表示レベル
        - summary: CI判定用の指標のみ
        - details: 失敗ケース上位N件 + カテゴリ別集計

Returns:
    レポート情報

Note:
    - Project API Key認証必須（X-API-Key ヘッダー）
    - report_id = job_id (Executionテーブルから動的生成)
    - 完了済みJobのみレポート取得可能
    - PIIマスキングは実装済み（各フィールドで処理）
```

**パラメータ**:

| 名前 | 型 | 場所 | 必須 | 説明 |
|------|-----|------|------|------|
| `report_id` | string | path | ✓ | - |
| `view` | string | query |  | 表示レベル |


**レスポンス**:

- **200**: Successful Response

```json
{
  "$ref": "#/components/schemas/ReportResponse"
}
```
- **422**: Validation Error

```json
{
  "$ref": "#/components/schemas/HTTPValidationError"
}
```

---


## スキーマ定義

以下は、API で使用される主要なデータモデルです。

### ApiKeyCreate

APIキー作成スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | string |  | APIキー名 |


---

### ApiKeyCreateResponse

APIキー作成応答スキーマ（作成時のみ生キーを返す）

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `id` | string | ✓ | - |
| `name` | string | ✓ | - |
| `key` | string | ✓ | APIキー（この応答でのみ表示、以後は取得不可） |
| `key_prefix` | string | ✓ | - |
| `created_at` | string | ✓ | - |


---

### ApiKeyListResponse

APIキー一覧応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `api_keys` | array | ✓ | - |
| `total` | integer | ✓ | - |


---

### ApiKeyResponse

APIキー応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | string |  | APIキー名 |
| `id` | string | ✓ | APIキーID（UUID） |
| `key_prefix` | string | ✓ | キープレフィックス（表示用） |
| `last_used_at` | object |  | 最終使用日時 |
| `created_at` | string | ✓ | - |
| `updated_at` | string | ✓ | - |


---

### ApiKeyUpdate

APIキー更新スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | object |  | APIキー名 |


---

### ApiSettingsResponse

API設定応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `api_endpoint` | string | ✓ | API endpoint URL |
| `auth_type` | string | ✓ | 認証タイプ（bearer/api_key/none） |
| `auth_header` | object |  | 認証ヘッダー名 |
| `auth_token` | object |  | 認証トークン |
| `request_format` | object |  | リクエストフォーマット |
| `response_format` | object |  | レスポンスフォーマット |
| `id` | string | ✓ | - |
| `config_id` | string | ✓ | - |
| `created_at` | string | ✓ | - |
| `updated_at` | string | ✓ | - |


---

### BalanceResponse

残高応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `total_credited` | string | ✓ | 累計付与クレジット（全てのトップアップ・調整の合計） |
| `consumed` | string | ✓ | 消費済みクレジット（total_credited - available_balance） |
| `available_balance` | string | ✓ | 利用可能残高（現在残高） |
| `credits_per_usd` | integer | ✓ | 現在のレート（1 USD = N credits） |


---

### CategoryBreakdown

カテゴリ別内訳

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `category` | string | ✓ | - |
| `success_rate` | object |  | - |
| `compliance_rate` | object |  | - |
| `count` | integer | ✓ | - |
| `violations` | object |  | - |


---

### CheckoutRequest

Checkout作成リクエストスキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `amount_usd_cents` | integer | ✓ | 金額（USDセント） |
| `currency` | string |  | 通貨 |
| `success_url` | string | ✓ | 成功時リダイレクトURL |
| `cancel_url` | string | ✓ | キャンセル時リダイレクトURL |


---

### CheckoutResponse

Checkout作成応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `session_id` | string | ✓ | Stripe Checkout Session ID |
| `url` | string | ✓ | Checkout URL（リダイレクト先） |


---

### ConfigCreate

Config作成スキーマ（全テーブルの情報を含む）

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | string | ✓ | 設定名 |
| `description` | object |  | 説明 |
| `locale` | string |  | 言語（ja/en-US） |
| `api_endpoint` | string | ✓ | API endpoint URL |
| `auth_type` | string | ✓ | 認証タイプ |
| `auth_header` | object |  | 認証ヘッダー名 |
| `auth_token` | object |  | 認証トークン |
| `request_format` | object |  | リクエストフォーマット |
| `response_format` | object |  | レスポンスフォーマット |
| `evaluation_metrics` | object |  | 評価メトリクス |
| `total_prompt_count` | object |  | プロンプト総数 |
| `prompt_category_ratios` | object |  | カテゴリ比率 |
| `manual_prompts` | object |  | 手動プロンプト |
| `evaluation_success_rate_threshold` | object |  | 評価成功率閾値（％） |
| `redteam_objectives` | object |  | RedTeam目標 |
| `redteam_max_turns` | object |  | 最大ターン数 |
| `redteam_defense_rate_threshold` | object |  | 防御率閾値（％） |
| `compliance_frameworks` | object |  | コンプライアンスフレームワーク |
| `policy_compliance_rate_threshold` | object |  | ポリシー準拠率閾値（％） |


---

### ConfigListResponse

Config一覧応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `configs` | array | ✓ | - |
| `total` | integer | ✓ | - |


---

### ConfigResponse

Config応答スキーマ（全関連テーブルを含む）

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | string | ✓ | 設定名 |
| `description` | object |  | 説明 |
| `locale` | string |  | 言語（ja/en-US） |
| `id` | string | ✓ | - |
| `tenant_id` | string | ✓ | - |
| `user_id` | string | ✓ | - |
| `created_at` | string | ✓ | - |
| `updated_at` | string | ✓ | - |
| `api_settings` | object |  | - |
| `rag_quality_config` | object |  | - |
| `redteam_config` | object |  | - |
| `policy_check_config` | object |  | - |


---

### ConfigUpdate

Config更新スキーマ（全テーブルの更新を許可）

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | object |  | - |
| `description` | object |  | - |
| `locale` | object |  | - |
| `api_endpoint` | object |  | - |
| `auth_type` | object |  | - |
| `auth_header` | object |  | - |
| `auth_token` | object |  | - |
| `request_format` | object |  | - |
| `response_format` | object |  | - |
| `evaluation_metrics` | object |  | - |
| `total_prompt_count` | object |  | - |
| `prompt_category_ratios` | object |  | - |
| `manual_prompts` | object |  | - |
| `evaluation_success_rate_threshold` | object |  | - |
| `redteam_objectives` | object |  | - |
| `redteam_max_turns` | object |  | - |
| `redteam_defense_rate_threshold` | object |  | - |
| `compliance_frameworks` | object |  | - |
| `policy_compliance_rate_threshold` | object |  | - |


---

### ConsumeCreditsRequest

クレジット消費リクエスト

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `amount` | object | ✓ | 消費するクレジット数（正の値） |
| `description` | object |  | 消費の説明 |


---

### ConsumeCreditsResponse

クレジット消費レスポンス

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `consumed` | string | ✓ | 消費したクレジット数 |
| `remaining_balance` | string | ✓ | 残りのクレジット残高 |
| `message` | string | ✓ | メッセージ |


---

### DailyUsage

日別使用量

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `date` | string | ✓ | - |
| `credits` | number | ✓ | クレジット消費量 |
| `requests` | integer | ✓ | リクエスト数 |


---

### DailyUsageResponse

日別使用量応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `data` | array | ✓ | - |


---

### EndpointUsage

エンドポイント別使用量

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `endpoint` | string | ✓ | - |
| `credits` | number | ✓ | クレジット消費量 |
| `requests` | integer | ✓ | リクエスト数 |


---

### EndpointUsageResponse

エンドポイント別使用量応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `data` | array | ✓ | - |


---

### EvaluationSummary

評価サマリ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `success_rate` | number | ✓ | - |
| `total_tests` | integer | ✓ | - |
| `passed` | integer | ✓ | - |
| `failed` | integer | ✓ | - |
| `category_breakdown` | array |  | - |


---

### FailedCase

失敗ケース

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `case_id` | string | ✓ | - |
| `input` | string | ✓ | 入力（PIIマスキング済み） |
| `expected` | object |  | 期待値 |
| `actual` | string | ✓ | 実際の出力（PIIマスキング済み） |
| `reason` | string | ✓ | - |
| `category` | string | ✓ | - |
| `severity` | string | ✓ | - |


---

### HTTPValidationError


**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `detail` | array |  | - |


---

### InvoiceListResponse

請求書一覧応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `invoices` | array | ✓ | - |
| `total` | integer | ✓ | - |


---

### InvoiceResponse

請求書応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `id` | string | ✓ | - |
| `stripe_invoice_id` | string | ✓ | - |
| `amount_usd_cents` | integer | ✓ | - |
| `status` | string | ✓ | - |
| `invoice_pdf_url` | object | ✓ | - |
| `created_at` | string | ✓ | - |


---

### JobCancelResponse

Jobキャンセル応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `job_id` | string | ✓ | キャンセルされたJob ID |
| `status` | string | ✓ | キャンセル後のステータス（cancelled） |
| `cancelled_at` | string | ✓ | キャンセル日時 |
| `message` | string | ✓ | キャンセル結果メッセージ |


---

### JobCreate

Job作成スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `config_id` | object |  | Config ID（省略時はデフォルトConfigを使用） |
| `execution_type` | string | ✓ | 実行タイプ（oss/quick_evaluate/redteam/policy_check） |
| `checkpoint_data` | object |  | チェックポイントデータ（quick_evaluate時の評価データなど） |


---

### JobListResponse

Job一覧応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `jobs` | array | ✓ | - |
| `total` | integer | ✓ | - |


---

### JobProgress

Job進捗情報スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `percentage` | number | ✓ | 進捗率（0.0〜100.0） |
| `message` | string | ✓ | 進捗メッセージ |


---

### JobResponse

Job応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `id` | string | ✓ | - |
| `tenant_id` | string | ✓ | - |
| `user_id` | string | ✓ | - |
| `config_id` | string | ✓ | - |
| `execution_type` | string | ✓ | - |
| `status` | string | ✓ | - |
| `current_step` | object |  | - |
| `progress_count` | integer | ✓ | - |
| `total_count` | integer | ✓ | - |
| `progress` | object |  | 進捗情報（推奨）。progress_count/total_countよりこちらを使用してください。 |
| `results` | object |  | - |
| `error_message` | object |  | - |
| `started_at` | object |  | - |
| `completed_at` | object |  | - |
| `created_at` | string | ✓ | - |
| `updated_at` | string | ✓ | - |


---

### ManualTopupRequest

手動トップアップリクエストスキーマ（開発用）

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `amount_usd_cents` | integer | ✓ | 金額（USDセント） |
| `description` | object |  | 説明 |


---

### ManualTopupResponse

手動トップアップ応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `credits_granted` | string | ✓ | - |
| `new_balance` | string | ✓ | - |


---

### PaymentMethodListResponse

支払い方法一覧応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `payment_methods` | array | ✓ | - |
| `total` | integer | ✓ | - |


---

### PaymentMethodResponse

支払い方法応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `id` | string | ✓ | - |
| `stripe_payment_method_id` | string | ✓ | - |
| `type` | string | ✓ | - |
| `last4` | object | ✓ | - |
| `brand` | object | ✓ | - |
| `exp_month` | object | ✓ | - |
| `exp_year` | object | ✓ | - |
| `is_default` | boolean | ✓ | - |
| `created_at` | string | ✓ | - |


---

### PolicyCheckConfigResponse

ポリシーチェック設定応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `compliance_frameworks` | array | ✓ | コンプライアンスフレームワーク |
| `policy_compliance_rate_threshold` | object |  | ポリシー準拠率閾値（％） |
| `id` | string | ✓ | - |
| `config_id` | string | ✓ | - |


---

### PolicySummary

ポリシーサマリ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `compliance_rate` | number | ✓ | - |
| `total_checks` | integer | ✓ | - |
| `violations_count` | integer | ✓ | - |
| `framework_breakdown` | array |  | - |


---

### PurchaseListResponse

購入履歴一覧応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `purchases` | array | ✓ | - |
| `total` | integer | ✓ | - |


---

### PurchaseResponse

購入履歴応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `id` | string | ✓ | - |
| `amount_usd_cents` | integer | ✓ | - |
| `credits_granted` | string | ✓ | - |
| `credits_per_usd_snapshot` | integer | ✓ | - |
| `status` | string | ✓ | - |
| `stripe_payment_intent_id` | object | ✓ | - |
| `created_at` | string | ✓ | - |


---

### RagQualityConfigResponse

RAG品質評価設定応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `evaluation_metrics` | object | ✓ | 評価メトリクス |
| `total_prompt_count` | integer | ✓ | プロンプト総数 |
| `prompt_category_ratios` | object | ✓ | カテゴリ比率 |
| `manual_prompts` | array |  | 手動プロンプト |
| `evaluation_success_rate_threshold` | object |  | 評価成功率閾値（％） |
| `id` | string | ✓ | - |
| `config_id` | string | ✓ | - |


---

### RedTeamSummary

RedTeamサマリ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `attack_success_rate` | number | ✓ | - |
| `risk_level` | string | ✓ | - |
| `total_attacks` | integer | ✓ | - |
| `successful_attacks` | integer | ✓ | - |
| `category_breakdown` | array |  | - |


---

### RedteamConfigResponse

RedTeam設定応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `redteam_objectives` | array | ✓ | RedTeam目標 |
| `redteam_max_turns` | integer |  | 最大ターン数 |
| `redteam_defense_rate_threshold` | object |  | 防御率閾値（％） |
| `id` | string | ✓ | - |
| `config_id` | string | ✓ | - |


---

### ReportDetails

レポート詳細（view=details用）

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `failed_cases` | array |  | 失敗ケース（最大10件） |
| `top_violations` | array |  | 重大違反（上位） |
| `recommendations` | array |  | 改善推奨事項 |


---

### ReportResponse

Report応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `report_id` | string | ✓ | - |
| `job_id` | string | ✓ | - |
| `config_id` | object | ✓ | - |
| `type` | string | ✓ | - |
| `status` | string | ✓ | - |
| `created_at` | string | ✓ | - |
| `summary` | object | ✓ | - |
| `details` | object |  | - |


---

### ReportSummary

レポートサマリ（全タイプ共通）

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `evaluation` | object |  | - |
| `redteam` | object |  | - |
| `policy` | object |  | - |


---

### SetupIntentCompleteRequest

SetupIntent完了通知リクエストスキーマ（PaymentMethod attach用）

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `setup_intent_id` | string | ✓ | Stripe SetupIntent ID (seti_...) |
| `set_as_default` | boolean |  | 完了した支払い方法をデフォルトに設定するか |


---

### SetupIntentCompleteResponse

SetupIntent完了通知応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `payment_method` | object | ✓ | - |


---

### SetupIntentResponse

SetupIntent作成応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `customer_id` | string | ✓ | - |
| `setup_intent_client_secret` | string | ✓ | - |


---

### TenantCreate

テナント作成スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | string | ✓ | テナント名 |


---

### TenantCreateResponse

POST /tenants 応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `tenant` | object | ✓ | - |


---

### TenantMeResponse

GET /tenants/me 応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `tenant` | object | ✓ | - |


---

### TenantResponse

テナント応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | string | ✓ | テナント名 |
| `id` | string | ✓ | テナントID（UUID） |
| `created_at` | string | ✓ | - |
| `updated_at` | string | ✓ | - |


---

### TenantUpdate

テナント更新スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | object |  | テナント名 |


---

### UsageExportResponse

使用量エクスポート応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `download_url` | string | ✓ | ダウンロードURL |
| `expires_at` | string | ✓ | URL有効期限 |
| `format` | string | ✓ | - |


---

### UsageSummaryResponse

使用量サマリ応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `total_requests` | integer | ✓ | 総リクエスト数 |
| `total_credits_used` | number | ✓ | 総クレジット消費量 |
| `total_spend_usd_cents` | integer | ✓ | 合計支出（USD cents）。total_credits_used と credits_per_usd からバックエンドで換算（四捨五入） |
| `currency` | string |  | 通貨（現状はusd固定） |
| `period_start` | string | ✓ | 集計開始日 |
| `period_end` | string | ✓ | 集計終了日 |


---

### UserCreate

ユーザー作成スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | object |  | ユーザー名 |
| `organization_name` | object |  | 組織名 |


---

### UserMeResponse

GET /users/me 応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `user` | object | ✓ | - |


---

### UserResponse

ユーザー応答スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | object |  | ユーザー名 |
| `organization_name` | object |  | 組織名 |
| `id` | string | ✓ | ユーザーID（UUID） |
| `email` | object |  | メールアドレス |
| `tenant_id` | string | ✓ | テナントID |
| `created_at` | string | ✓ | - |
| `updated_at` | string | ✓ | - |


---

### UserUpdate

ユーザー更新スキーマ

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `name` | object |  | ユーザー名 |
| `organization_name` | object |  | 組織名 |


---

### ValidationError


**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `loc` | array | ✓ | - |
| `msg` | string | ✓ | - |
| `type` | string | ✓ | - |


---

### Violation

違反情報

**フィールド**:

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| `violation_id` | string | ✓ | - |
| `rule` | string | ✓ | - |
| `description` | string | ✓ | - |
| `severity` | string | ✓ | - |
| `evidence` | string | ✓ | 証跡（PIIマスキング済み） |


---


---

**生成日時**: now  
**自動生成**: このドキュメントは `scripts/doc_generator/main.py` により自動生成されました。
