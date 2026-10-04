"""Submit a collected extraction dataset through the public jobs API.

The target system is not contacted by this example. Creating the Platform job
does run paid evaluation; use an explicitly enabled tenant and a stable UUID.
"""

import argparse
import json
from pathlib import Path
from uuid import UUID

from genflux import Genflux, JobFailedError


def main() -> None:
    """Submit once with a durable UUID and optionally save the terminal result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--request-id", type=UUID, required=True, help="Reuse this UUID after an uncertain response")
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--output", type=Path, help="New JSON output file; requires --wait")
    args = parser.parse_args()
    if args.output is not None and not args.wait:
        parser.error("--output requires --wait")
    if args.output is not None and args.output.exists():
        parser.error("Choose a new output path; existing evaluation results are not overwritten")
    raw = args.dataset.read_bytes()
    if len(raw) > 8_000_000:
        parser.error("Dataset exceeds 8 MB")
    data = json.loads(raw)
    with Genflux() as client:
        job = client.jobs.create(
            execution_type="extraction_evaluate",
            data=data,
            client_request_id=str(args.request_id),
        )
        print(json.dumps({"job_id": job.id, "status": job.status}))
        if not args.wait:
            return
        try:
            job = client.jobs.wait(job.id, timeout=args.timeout)
        except JobFailedError:
            # Failed measurements remain inspectable; they are never replaced by zero.
            job = client.jobs.get(job.id)
        if args.output:
            value = {
                "job_id": job.id,
                "status": job.status,
                "results": job.results,
                "assessment_bundle": job.assessment_bundle.model_dump(mode="json") if job.assessment_bundle else None,
            }
            with args.output.open("x", encoding="utf-8") as target:
                json.dump(value, target, ensure_ascii=False, indent=2, allow_nan=False)
                target.write("\n")
        print(json.dumps({"job_id": job.id, "status": job.status}))


if __name__ == "__main__":
    main()
