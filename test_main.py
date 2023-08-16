from fastapi.testclient import TestClient
import os
from main import app
client = TestClient(app)


def test_file_exists():
    os.environ["VAULT_PATH"] = "./test_vault"
    response = client.get("/exists?path=file1.md")
    assert response.status_code == 200
    assert response.json() == {"file exists":True}
    response = client.get("/exists?path=file3.md")
    assert response.status_code == 200
    assert response.json() == {"file exists":False}
    response = client.get("/exists")
    assert response.status_code == 400
    assert response.json() == {"detail":"Path not provided"}
    

def test_append_to_file():
    initial_file_content = ""
    fake_data = {"path": "file1.md", "text": "Hello World"}
    os.environ["VAULT_PATH"] = "./test_vault"
    with open(os.path.join(os.environ["VAULT_PATH"], fake_data["path"]), "r", encoding="UTF-8") as f:
        initial_file_content = f.read()
    
    response = client.post(
        "/append",
        json=fake_data,
        )
       
    with open(os.path.join(os.environ["VAULT_PATH"], fake_data["path"]), "r", encoding="UTF-8") as f:
        assert f.read() == initial_file_content + "\n" + fake_data["text"]
    assert response.status_code == 200
    assert response.json() == {"action": f'added {fake_data["text"]} to {fake_data["path"]}'}
    with open(os.path.join(os.environ["VAULT_PATH"], fake_data["path"]), "w", encoding="UTF-8") as f:
        f.write(initial_file_content)
    #TODO: maybe add test cases where the file does not exist or the path is not provided


def test_file_content():
    os.environ["VAULT_PATH"] = "./test_vault"
    response = client.get("/content?path=file1.md")
    assert response.status_code == 200
    assert response.json() == {"content": "# File 1\n---\ntag: tag1, tag2\nkeywords: keyword1, keyword2\n---"}

    response = client.get("/content?path=file3.md")
    assert response.status_code == 400
    assert response.json() == {"detail": "File does not exist"}


def test_file_metadata():
    os.environ["VAULT_PATH"] = "./test_vault"
    response = client.get("/metadata?path=file1.md")
    assert response.status_code == 200
    assert response.json() == {"metadata": {"tag": 'tag1, tag2', 'keywords': 'keyword1, keyword2'}}

    response = client.get("/metadata?path=file1_metadata_lower_in_the_page.md")
    assert response.status_code == 200
    assert response.json() == {"metadata": {"tag": 'tag1, tag2', 'keywords': 'keyword1, keyword2'}}
    response = client.get("/metadata?path=file2.md")
    assert response.status_code == 200
    assert response.json() == {"metadata": {}}

    response = client.get("/metadata?path=file3.md")
    assert response.status_code == 400
    assert response.json() == {"detail": "File does not exist"}