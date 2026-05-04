# API 依赖分析器

[English](README.md) | **中文**

> 自动扫描并分析代码库中的 API 依赖关系。检测 REST、GraphQL、gRPC、WebSocket 调用，识别提供商，发现安全问题，估算成本。

## 功能特性

- 🔍 **多语言支持**: JavaScript, TypeScript, Python, Java, Go, Ruby, PHP, C#, Swift, Kotlin
- 📡 **多协议支持**: REST API、GraphQL、gRPC、WebSocket、Server-Sent Events (SSE)
- 🏢 **自动识别提供商**: 自动识别 50+ 常见 API 提供商（GitHub、OpenAI、Stripe 等）
- 🔒 **安全分析**: 检测不安全的 HTTP、缺失的身份验证、硬编码密钥
- 💰 **成本估算**: 估算第三方 API 使用成本
- 📊 **多种输出格式**: JSON、Markdown、CSV 报告

## 快速开始

### 命令行使用

```bash
# pip 安装
pip install api-dependency-analyzer

# 分析项目
api-analyze --path /path/to/your/project

# 或者直接运行
python -m api_analyzer --path .
```

### 作为 Python 库使用

```python
from api_analyzer import APIDependencyAnalyzer

analyzer = APIDependencyAnalyzer('/path/to/project')
report = analyzer.analyze()

print(f"发现 {report['stats']['total_apis']} 个 API 调用")
```

## 使用方法

### CLI 选项

```bash
api-analyze --path <项目路径> [选项]

选项:
  --path PATH          要分析的项目路径（必需）
  --output DIR         输出目录（默认：./api-analysis）
  --format FORMAT      输出格式：json, markdown, csv, all（默认：all）
  --help               显示帮助信息
```

### 示例输出

```markdown
# API 依赖分析报告

## 概览

| 指标 | 数量 |
|------|------|
| API 调用总数 | 42 |
| 扫描文件数 | 156 |
| 发现问题 | 7 |

## API 类型分布

| 类型 | 数量 |
|------|------|
| REST | 35 |
| GraphQL | 5 |
| WebSocket | 2 |
```

## 支持的语言和框架

| 语言 | 检测到的框架 |
|------|-------------|
| JavaScript/TypeScript | fetch, axios, superagent, got, node-fetch, Apollo, Socket.IO |
| Python | requests, httpx, aiohttp, urllib, gql, Strawberry |
| Java | HttpClient, OkHttp, RestTemplate, Feign, gRPC |
| Go | net/http, fasthttp, grpc, req |
| Ruby | Net::HTTP, Faraday, HTTParty |
| PHP | Guzzle, cURL |
| C# | HttpClient, RestSharp |
| Swift | URLSession, Alamofire |
| Kotlin | Ktor, Fuel, OkHttp |

## 检测到的 API 提供商

工具自动识别以下常见 API 提供商：

- **AI/ML**: OpenAI、Anthropic Claude、Google Gemini、Cohere
- **云服务**: AWS S3、Google Cloud Storage、Azure Blob
- **支付**: Stripe、PayPal、支付宝、微信支付
- **社交**: GitHub、Twitter/X、Facebook、LinkedIn、Discord
- **通信**: Twilio、SendGrid、Slack
- **地图**: Google Maps、Mapbox、高德地图
- **监控**: Datadog、New Relic、Amplitude

## 安全检查

| 问题 | 严重性 | 描述 |
|------|--------|------|
| `insecure_http` | 高 | 使用 HTTP 而非 HTTPS |
| `insecure_ws` | 高 | 使用不安全的 WebSocket (ws://) |
| `missing_auth` | 中 | 未检测到身份验证 |
| `no_timeout` | 低 | 未配置超时 |
| `hardcoded_secret` | 严重 | 可能存在硬编码密钥 |

## 安装

### 通过 pip 安装

```bash
pip install api-dependency-analyzer
```

### 从源码安装

```bash
git clone https://github.com/your-username/api-dependency-analyzer.git
cd api-dependency-analyzer
pip install -e .
```

## GitHub Actions 集成

```yaml
name: API 依赖分析

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: 设置 Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: 安装分析器
        run: pip install api-dependency-analyzer
      - name: 分析 API
        run: api-analyze --path . --output ./api-report
      - name: 上传报告
        uses: actions/upload-artifact@v3
        with:
          name: api-report
          path: ./api-report
```

## 开发

```bash
# 克隆仓库
git clone https://github.com/your-username/api-dependency-analyzer.git
cd api-dependency-analyzer

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest

# 本地运行
python -m api_analyzer --path . --output ./test-report
```

## 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- 灵感来源于微服务架构中对更好的 API 依赖管理的需求
- 为关心代码质量和安全的开发者而构建 ❤️
