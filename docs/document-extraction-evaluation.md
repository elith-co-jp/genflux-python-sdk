# 収集済み文書抽出結果を評価する

会社限定で有効にしたPlatformの`extraction_evaluate`ジョブを、既存の`jobs` APIで呼び出します。
SDKは評価ロジックや対象システムへのデータ投入を行いません。

```python
import json
from pathlib import Path
from genflux import Genflux

dataset = json.loads(Path("document-extraction-dataset-v1.json").read_text())
with Genflux() as client:
    job = client.jobs.create(
        execution_type="extraction_evaluate",
        data=dataset,
        client_request_id="8fb21390-34bc-4a43-a0c7-3b2fddc8e89d",
    )
    result = client.jobs.wait(job.id, timeout=3600)
    print(result.status)
```

API Keyと接続先は既存の`GENFLUX_API_KEY`・`GENFLUX_API_BASE_URL`設定を使用します。
受付応答を確認できなかった場合は、同じデータと同じ`client_request_id`で再送してください。
実際に新しい評価を行う場合は新しいUUIDを発行します。
会社の利用許可がない場合は403になります。SDK自身で会社を有効化することはできません。

`partial`は測定できない項目を含んだ終了状態です。`jobs.wait`はその結果を返しますが、`job.is_completed`はFalseです。
`failed`の場合は`JobFailedError`が発生し、`jobs.get(job.id)`で実行記録を確認できます。
取消には`jobs.cancel(job.id)`を使用します。

結果は`job.results`、型付きの原本・判定・使用量の記録は`job.assessment_bundle`にあります。
未測定・エラーの点数はnullです。初回結果と再試行をPDF名だけでまとめないでください。
決定的な件数・引用文等の比較は`screen_extraction_rules_v1`として記録し、課金されるリモート判定とは区別します。

[実行例](../examples/document_extraction_evaluation.py)は、安定したUUIDの指定と、既存ファイルを上書きしないJSON出力に対応しています。
Platformの変更と対応SDKを公開した後に使用してください。
