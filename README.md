# Dockerized Obsidian Vault management REST API
This project creates a small dockerized REST API allowing you to interact with you obsidian Vault programmatically

At the moment, the following functionality is exposed via REST:
 * Check if a file exists
 * Append text to a file   
 * Get a file's content
 * Get a file's metadata


## Installation

Install via docker:

```bash
docker pull guillaumeredoules/obsidian-api
docker run -d -p 5000:8080 -v /path/to/your/vault:/vault -e SECRET_KEY=your-secret-key -e USER=your-username -e PASSWORD=your-password -e ACCESS_TOKEN_EXPIRE_MINUTES=30 obsidian-api 
```

## Usage

Environment variables:
* `SECRET_KEY` (optionnal): secret key used to encrypt the files. If no SECRET_KEY is provided, one will be generated at launch
* `USER` : username for basic auth
* `PASSWORD` : password for basic auth
* `ACCESS_TOKEN_EXPIRE_MINUTES` : expiration time for the access token (default: 30 minutes, no expiration if set to -1)

### Access Swagger documentation

```bash
curl -X GET http://localhost:8080/docs
```

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
