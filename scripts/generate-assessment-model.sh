#!/usr/bin/env bash
set -euo pipefail
# Input is exported by Platform scripts/export_assessment_schema.py.
cd "$(dirname "$0")/.."
uvx --from datamodel-code-generator==0.33.0 datamodel-codegen \
  --input contracts/assessment-v3.schema.json --input-file-type jsonschema \
  --output src/genflux/models/assessment.py --output-model-type pydantic_v2.BaseModel \
  --target-python-version 3.11 --use-standard-collections --use-union-operator \
  --use-annotated --enum-field-as-literal all --extra-fields forbid \
  --enable-faux-immutability --disable-timestamp --enable-version-header
uv run python - <<'PY'
from pathlib import Path

path = Path('src/genflux/models/assessment.py')
source = path.read_text()
old = '    collection_receipt: BffTargetCollectionReceipt | None = None\n'
assert source.count(old) == 1
path.write_text(source.replace(old, '    collection_receipt: BffTargetCollectionReceipt | None = Field(\n        default=None, exclude_if=lambda value: value is None\n    )\n'))
PY
uvx --from datamodel-code-generator==0.33.0 datamodel-codegen \
  --input contracts/accepted-assessment-plan-v1.schema.json --input-file-type jsonschema \
  --output src/genflux/models/assessment_plan.py --output-model-type pydantic_v2.BaseModel \
  --target-python-version 3.11 --use-standard-collections --use-union-operator \
  --use-annotated --enum-field-as-literal all --extra-fields forbid \
  --enable-faux-immutability --disable-timestamp --enable-version-header
