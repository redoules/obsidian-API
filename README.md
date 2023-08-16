# obsidian-API
Interact with you obsidian Vault using an API


## Installation

Install via docker:

```bash
docker build -t obsidian-api .
docker run -d -p 5000:80 -v /path/to/your/vault:/vault obsidian-api
```

## Usage

### Check if a file exists

```bash 
curl -X GET http://localhost:8080/exists?path=README.md
```

### Append to a file
Provide the path and the text to be added in the body of the request 

```bash
curl -X POST -H "Content-Type: application/json" -d '{"path":"myfile.md", "text":"hello world"}' http://localhost:8080/append
``` 
### Get a file's content

```bash
curl -X GET http://localhost:8080/content?path=README.md
```

### Get a file's metadata

```bash
curl -X GET http://localhost:8080/metadata?path=README.md
```
