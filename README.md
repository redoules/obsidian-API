# obsidian-API
Interact with you obsidian Vault using an API


## Installation

Install via docker:

```bash
docker build -t obsidian-api .
docker run -d -p 5000:80 -v /path/to/your/vault:/vault obsidian-api -e VAULT_PATH=/vault -e SECRET_KEY=your-secret-key
```

## Usage

Environment variables:
* `VAULT_PATH`: path to your vault
* `SECRET_KEY` (optionnal): secret key used to encrypt the files
* `USER` : username for basic auth
* `PASSWORD` : password for basic auth
* `ACCESS_TOKEN_EXPIRE_MINUTES` : expiration time for the access token (default: 30 minutes, no expiration if set to -1)
### Check if a file exists

```bash 
curl -X GET http://localhost:8080/api/v1/exists?path=README.md
```

### Append to a file
Provide the path and the text to be added in the body of the request 

```bash
curl -X POST -H "Content-Type: application/json" -d '{"path":"myfile.md", "text":"hello world"}' http://localhost:8080/api/v1/append
``` 
### Get a file's content

```bash
curl -X GET http://localhost:8080/api/v1/content?path=README.md
```

### Get a file's metadata

```bash
curl -X GET http://localhost:8080/api/v1/metadata?path=README.md
```
