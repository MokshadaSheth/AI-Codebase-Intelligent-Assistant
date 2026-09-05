from services.repository_service import clone_repository


url = "https://github.com/Vasu7389/react-project-ideas"

path = "./repositories/test-repo"

result = clone_repository(url, path)

print(result)