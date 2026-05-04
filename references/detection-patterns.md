# API 检测模式参考

本文档说明 API Dependency Analyzer 支持的 API 调用检测模式。

## REST API 检测模式

### JavaScript / TypeScript

```javascript
// fetch API
fetch('https://api.example.com/users')
fetch(`https://api.example.com/users/${id}`)
fetch(url, { method: 'POST' })

// Axios
axios.get('https://api.example.com/data')
axios.post('/api/submit', data)
axios.put(url, payload)
axios.delete('/api/resource/123')

// 通用 HTTP 库
http.get('https://api.example.com/items')
request.get('/api/data')

// URL 变量
const API_BASE = 'https://api.example.com'
const endpoint = '/users'
```

### Python

```python
import requests

requests.get('https://api.example.com/users')
requests.post(url, json=data)
response = httpx.get('https://api.example.com/data')
```

### Java

```java
// RestTemplate, OkHttp, etc.
restTemplate.getForObject("https://api.example.com/users", User.class);
```

## GraphQL 检测模式

```javascript
// Apollo Client
const { data } = await client.query({
  query: gql`
    query GetUsers {
      users {
        id
        name
      }
    }
  `
});

// 通用 GraphQL 请求
fetch('/graphql', {
  method: 'POST',
  body: JSON.stringify({ query: '{ users { id } }' })
});
```

## gRPC 检测模式

```python
# Python gRPC
stub = user_pb2_grpc.UserServiceStub(channel)
response = stub.GetUser(user_pb2.GetUserRequest(id=123))
```

```javascript
// Node.js gRPC
const client = new userService.UserService(
  'localhost:50051',
  grpc.credentials.createInsecure()
);
client.getUser({ id: 123 }, (error, response) => { ... });
```

## WebSocket 检测模式

```javascript
const ws = new WebSocket('wss://api.example.com/ws');
const socket = new WebSocketConnection('wss://...');
```

## 认证检测

Skill 会检查以下认证模式的存在：

- `Authorization` header
- `Bearer` token
- `API-Key` / `X-API-Key`
- Basic Auth (`username:password`)
- OAuth2 tokens
- JWT tokens

## 不安全协议检测

以下情况会被标记为 `insecure`：

- 使用 `http://` 而非 `https://`
- WebSocket 使用 `ws://` 而非 `wss://`
- API 端点缺少 TLS

## 自定义检测规则

如需添加自定义检测模式，可修改 `scripts/analyze_api.py` 中的 `API_PATTERNS` 字典：

```python
API_PATTERNS = {
    "your_api_type": [
        r'your_pattern\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
    ]
}
```
