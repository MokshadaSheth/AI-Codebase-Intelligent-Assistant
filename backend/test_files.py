from services.file_service import get_source_files, read_file
from services.chunk_service import chunk_code


repo_path = "./repositories/test-repo"

files = get_source_files(repo_path)

print("Total source files:", len(files))


for file in files:

    content = read_file(file)

    if not content:
        continue

    chunks = chunk_code(content)

    print("\n" + "=" * 60)
    print("FILE:", file)
    print("CHUNKS:", len(chunks))
    print("=" * 60)

    for i, chunk in enumerate(chunks[:2]):

        print("\nCHUNK", i + 1)
        print("-" * 40)
        print(chunk[:500])  