# RAG Evaluation

This isolated utility measures the existing RAG pipeline against a small set of representative codebase questions. It does not change production services or create additional model instances.

## Measures

For each question it records the answer, returned sources, source file paths, source count, and end-to-end latency. Cases with `expected_files` also report an expected source hit when at least one expected file appears in the returned sources.

The summary reports query count, average latency, average returned source count, and source hit rate for cases that provide expected files. Source hit rate is not a quality score for the answer; it only measures whether retrieval returned at least one declared expected file.

## Run

From the `backend` directory, pass the repository ID used when indexing:

```powershell
python ..\evaluation\evaluate_rag.py <repo_id>
```

For example:

```powershell
python ..\evaluation\evaluate_rag.py 0123456789abcdef
```

The script uses `services.container.rag_service`, so it reuses the existing service and model instances. Each failed question is reported and the remaining questions continue to run.
