from fastapi.testclient import TestClient
import os
from main import app, create_access_token

client = TestClient(app)


async def override_login(q: str | None = None):
    return {
        "access_token": create_access_token(
            data={"sub": "test_user"}, expires_delta=None
        ),
        "token_type": "bearer",
    }


# app.dependency_overrides[token] = override_login


def get_bearer_token():
    return {
        "access_token": create_access_token(
            data={"sub": "test_user"}, expires_delta=None
        ),
        "token_type": "bearer",
    }
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNjkyMjE0NzIxfQ.uM4XR2Yqndbzwb6KM5fu5_TXmJ-C8SJ3mjuWDd7wXE"
    return os.environ["BEARER_TOKEN"]


def test_file_exists():
    os.environ["VAULT_PATH"] = "./test_vault"
    response = client.get(
        "/api/v1/exists?path=file1.md",
        headers={"Authorization": f"Bearer {get_bearer_token()}"},
    )
    assert response.status_code == 200
    assert response.json() == {"file exists": True}
    response = client.get(
        "/api/v1/exists?path=file3.md",
        headers={"Authorization": f"Bearer {get_bearer_token()}"},
    )
    assert response.status_code == 200
    assert response.json() == {"file exists": False}
    response = client.get(
        "/api/v1/exists", headers={"Authorization": f"Bearer {get_bearer_token()}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Path not provided"}


def test_append_to_file():
    initial_file_content = ""
    fake_data = {"path": "file1.md", "text": "Hello World"}
    os.environ["VAULT_PATH"] = "./test_vault"
    with open(
        os.path.join(os.environ["VAULT_PATH"], fake_data["path"]), "r", encoding="UTF-8"
    ) as f:
        initial_file_content = f.read()

    response = client.post(
        "/api/v1/append",
        json=fake_data,
        headers={"Authorization": f"Bearer {get_bearer_token()}"},
    )

    with open(
        os.path.join(os.environ["VAULT_PATH"], fake_data["path"]), "r", encoding="UTF-8"
    ) as f:
        assert f.read() == initial_file_content + "\n" + fake_data["text"]
    assert response.status_code == 200
    assert response.json() == {
        "action": f'added {fake_data["text"]} to {fake_data["path"]}'
    }
    with open(
        os.path.join(os.environ["VAULT_PATH"], fake_data["path"]), "w", encoding="UTF-8"
    ) as f:
        f.write(initial_file_content)
    # TODO: maybe add test cases where the file does not exist or the path is not provided


def test_file_content():
    os.environ["VAULT_PATH"] = "./test_vault"
    response = client.get(
        "/api/v1/content?path=file1.md",
        headers={"Authorization": f"Bearer {get_bearer_token()}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "content": "# File 1\n---\ntag: tag1, tag2\nkeywords: keyword1, keyword2\n---"
    }

    response = client.get(
        "/api/v1/content?path=file3.md",
        headers={"Authorization": f"Bearer {get_bearer_token()}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "File does not exist"}


def test_file_metadata():
    os.environ["VAULT_PATH"] = "./test_vault"
    response = client.get(
        "/api/v1/metadata?path=file1.md",
        headers={"Authorization": f"Bearer {get_bearer_token()}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"tag": "tag1, tag2", "keywords": "keyword1, keyword2"}
    }

    response = client.get(
        "/api/v1/metadata?path=file1_metadata_lower_in_the_page.md",
        headers={"Authorization": f"Bearer {get_bearer_token()}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"tag": "tag1, tag2", "keywords": "keyword1, keyword2"}
    }
    response = client.get(
        "/api/v1/metadata?path=file2.md",
        headers={"Authorization": f"Bearer {get_bearer_token()}"},
    )
    assert response.status_code == 200
    assert response.json() == {"metadata": {}}

    response = client.get(
        "/api/v1/metadata?path=file3.md",
        headers={"Authorization": f"Bearer {get_bearer_token()}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "File does not exist"}
