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
curl -X GET http://localhost:5000/exists?path=README.md
```

### Append to a file

```bash
curl -X POST -H "Content-Type: text/plain" -d "Hello World" http://localhost:5000/append?path=README.md
```

### Get a file's content

```bash
curl -X GET http://localhost:5000/content?path=README.md
```

### Get a file's metadata

```bash
curl -X GET http://localhost:5000/metadata?path=README.md
```

### Create a file

```bash 
curl -X POST -H "Content-Type: text/plain" -d "Hello World" http://localhost:5000/create?path=README.md
```