import argparse
import sys
import time
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from services.container import rag_service


TEST_CASES = [
    {
        "question": "Where is the repository indexed?",
        "expected_files": ["services/index_service.py"],
    },
    {
        "question": "How does hybrid search work?",
        "expected_files": ["services/vector_service.py"],
    },
    {
        "question": "How are code chunks created?",
        "expected_files": ["services/chunk_service.py"],
    },
    {
        "question": "How does reranking work?",
        "expected_files": ["services/reranker_service.py"],
    },
    {
        "question": "How is the Gemini response generated?",
        "expected_files": ["services/llm_service.py"],
    },
    {
        "question": "How does the chat API work?",
        "expected_files": ["api/chat.py"],
    },
    {
        "question": "Where is conversation history handled?",
        "expected_files": ["services/llm_service.py"],
    },
]


def _matches_expected(source_file: str, expected_file: str) -> bool:
    source_path = Path(source_file).as_posix().lower()
    expected_path = Path(expected_file).as_posix().lower()
    return source_path == expected_path or source_path.endswith(
        "/" + expected_path
    )


def _source_hit(source_files, expected_files):
    if not expected_files:
        return None

    return any(
        _matches_expected(source_file, expected_file)
        for source_file in source_files
        for expected_file in expected_files
    )


def evaluate(repo_id: str):
    results = []
    latencies = []
    source_counts = []
    source_hit_values = []

    for test_case in TEST_CASES:
        question = test_case["question"]
        expected_files = test_case.get("expected_files", [])
        started = time.perf_counter()

        result = {
            "question": question,
            "expected_files": expected_files,
            "answer": None,
            "sources": [],
            "number_of_sources": 0,
            "source_files": [],
            "expected_source_hit": None,
            "latency": None,
            "error": None,
        }

        try:
            response = rag_service.ask(
                question=question,
                repo_id=repo_id,
            )
            sources = response.get("sources", [])
            source_files = [
                source.get("file", "unknown")
                for source in sources
            ]

            result.update({
                "answer": response.get("answer"),
                "sources": sources,
                "number_of_sources": len(sources),
                "source_files": source_files,
                "expected_source_hit": _source_hit(
                    source_files,
                    expected_files,
                ),
            })
        except Exception as error:
            result["error"] = str(error)

        result["latency"] = time.perf_counter() - started
        results.append(result)
        latencies.append(result["latency"])
        source_counts.append(result["number_of_sources"])

        if result.get("expected_source_hit") is not None:
            source_hit_values.append(result["expected_source_hit"])

    return {
        "results": results,
        "query_count": len(results),
        "average_latency": sum(latencies) / len(latencies),
        "average_sources": sum(source_counts) / len(source_counts),
        "source_hit_rate": (
            sum(source_hit_values) / len(source_hit_values)
            if source_hit_values
            else None
        ),
        "source_hit_count": sum(source_hit_values),
        "source_hit_queries": len(source_hit_values),
    }


def _print_result(result):
    print(f"Query: {result['question']}")

    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        expected_files = result.get("expected_files", [])
        if expected_files:
            print(f"Expected: {', '.join(expected_files)}")
        print(f"Retrieved: {', '.join(result['source_files']) or 'none'}")
        if result.get("expected_source_hit") is not None:
            status = "PASS" if result["expected_source_hit"] else "FAIL"
            print(f"Source Hit: {status}")

    print(f"Sources: {result['number_of_sources']}")
    print(f"Latency: {result['latency']:.2f}s")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Run representative questions against the existing RAG service."
    )
    parser.add_argument(
        "repo_id",
        help="Repository ID used by the existing Qdrant retrieval pipeline.",
    )
    args = parser.parse_args()

    report = evaluate(args.repo_id)

    print("RAG Evaluation")
    print("==============")
    print()
    for result in report["results"]:
        _print_result(result)

    print("Summary")
    print("-------")
    print(f"Queries: {report['query_count']}")
    print(f"Average latency: {report['average_latency']:.2f}s")
    print(f"Average sources: {report['average_sources']:.2f}")
    if report["source_hit_rate"] is None:
        print("Source hit rate: unavailable (no expected files supplied)")
    else:
        print(
            "Source hit rate: "
            f"{report['source_hit_rate'] * 100:.2f}% "
            f"({report['source_hit_count']}/{report['source_hit_queries']})"
        )


if __name__ == "__main__":
    main()
