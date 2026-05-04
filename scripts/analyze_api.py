#!/usr/bin/env python3
"""
API Dependency Analyzer
扫描项目代码，提取 API 调用并生成依赖分析报告

支持语言: JavaScript, TypeScript, Python, Java, Go, Ruby, PHP, C#, Swift, Kotlin
支持协议: REST, GraphQL, gRPC, WebSocket, Server-Sent Events (SSE)
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime

VERSION = "1.0.0"


@dataclass
class APICall:
    """单个 API 调用信息"""
    url: str
    type: str  # rest, graphql, grpc, websocket, sse
    file: str
    line: int
    method: str
    provider: str
    issues: List[str]
    code_snippet: str = ""


# API 调用检测模式 - 按语言组织
API_PATTERNS = {
    "rest": [
        # JavaScript/TypeScript: fetch, axios, superagent, got, node-fetch
        (r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts', 'jsx', 'tsx']),
        (r'axios\.(get|post|put|delete|patch|head|options)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts', 'jsx', 'tsx']),
        (r'axios\s*\(\s*\{[^}]*url\s*:\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts', 'jsx', 'tsx']),
        (r'got\s*\(?[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        (r'request\s*\(?[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        (r'http\.(get|post|put|delete|patch)\s*\(?[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        (r'new\s+Request\s*\(?[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        
        # Python: requests, httpx, aiohttp, urllib
        (r'requests\.(get|post|put|delete|patch|head|options)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['py']),
        (r'httpx\.(get|post|put|delete|patch|head|options)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['py']),
        (r'urllib\.request\.urlopen\s*\(\s*[\'"]([^\'"]+)[\'"]', ['py']),
        (r'aiohttp\.ClientSession\(\)\.get\s*\(\s*[\'"]([^\'"]+)[\'"]', ['py']),
        
        # Java: HttpClient, OkHttp, RestTemplate, Feign
        (r'HttpClient\.newBuilder\(\)\.build\(\)\.(get|post|put|delete|patch)\s*\(\s*URI\.create\s*\(\s*[\'"]([^\'"]+)[\'"]', ['java']),
        (r'OkHttpClient\s*\(\)\.newCall\s*\(\s*new\s+Request\.Builder\(\)\.url\s*\(\s*[\'"]([^\'"]+)[\'"]', ['java']),
        (r'RestTemplate\s*\(\)\.getForObject\s*\(\s*[\'"]([^\'"]+)[\'"]', ['java']),
        (r'@RequestMapping\s*\([^)]*value\s*=\s*[\'"]([^\'"]+)[\'"]', ['java']),
        
        # Go: net/http, fasthttp, req
        (r'http\.(Get|Post|Put|Delete|Patch|Head)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['go']),
        (r'fasthttp\.(Get|Post|Put|Delete)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['go']),
        (r'req\.(R|Get|Post|Put|Delete)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['go']),
        
        # Ruby: net/http, faraday, httparty
        (r'Net::HTTP\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['rb']),
        (r'Faraday\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['rb']),
        (r'HTTParty\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['rb']),
        
        # PHP: guzzle, curl, file_get_contents
        (r'GuzzleHttp[^\;]*->(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['php']),
        (r'curl_setopt\s*\(\s*\$ch\s*,\s*CURLOPT_URL\s*,\s*[\'"]([^\'"]+)[\'"]', ['php']),
        
        # C#: HttpClient, RestSharp
        (r'HttpClient\s*\(\)\.(GetAsync|PostAsync|PutAsync|DeleteAsync|PatchAsync)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['cs']),
        (r'RestClient\.(Get|Post|Put|Delete)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['cs']),
        
        # Swift: URLSession, Alamofire
        (r'URLSession\.shared\.(dataTask|uploadTask)\s*\(\s*URL\s*\(\s*string:\s*[\'"]([^\'"]+)[\'"]', ['swift']),
        (r'Alamofire\.(request|get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['swift']),
        
        # Kotlin: ktor, fuel, OkHttp
        (r'client\.get\s*\(\s*[\'"]([^\'"]+)[\'"]', ['kt']),
        (r'Fuel\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]', ['kt']),
        
        # 通用: URL/endpoint/uri 变量
        (r'(?:url|endpoint|uri|apiUrl|baseURL|apiEndpoint)\s*[=:]\s*[\'"](https?://[^\'"]+)[\'"]', ['js', 'ts', 'py', 'java', 'go', 'rb', 'php', 'cs', 'swift', 'kt']),
        (r'[\'"](https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}/[^\'"]+)[\'"]', ['js', 'ts', 'py', 'java', 'go', 'rb', 'php', 'cs', 'swift', 'kt']),
    ],
    
    "graphql": [
        # JavaScript/TypeScript
        (r'gql\s*`[^`]+`', ['js', 'ts', 'jsx', 'tsx']),
        (r'apollo\.client\.query\s*\(\s*\{[^}]*query', ['js', 'ts']),
        (r'apolloProvider\.defaultClient\.query\s*\(\s*\{[^}]*query', ['js', 'ts']),
        (r'new\s+ApolloClient\s*\([^)]*link:\s*HttpLink\s*\([^)]*uri:\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        (r'useQuery\s*\(\s*gql\s*`', ['ts', 'tsx']),
        (r'useLazyQuery\s*\(\s*gql\s*`', ['ts', 'tsx']),
        (r'fetchPolicy.*network-only', ['ts', 'tsx']),
        
        # Python
        (r'gql\s*\(["\'].+?["\']\)', ['py']),
        (r'strawberry\.graphql\s*\(', ['py']),
        (r'@strawberry\.type.*\n.*def\s+\w+:', ['py']),
        
        # GraphQL 端点
        (r'graphqlEndpoint\s*[=:]\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts', 'py']),
        (r'GQL_ENDPOINT\s*[=:]\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts', 'py']),
    ],
    
    "grpc": [
        # Python
        (r'stub\s*=\s*[a-zA-Z]+\.Stub\s*\([a-zA-Z]+\.[a-zA-Z]+\(\)', ['py']),
        (r'stub\.([a-zA-Z]+)\s*\(', ['py']),
        
        # Go
        (r'grpc\.Dial\s*\(\s*[\'"]([^\'"]+)[\'"]', ['go']),
        (r'client\s*:=\s*New[A-Za-z]+Client\s*\(', ['go']),
        (r'conn,\s*err\s*:=\s*grpc\.Dial\s*\(', ['go']),
        
        # JavaScript/TypeScript
        (r'new\s+grpc\.Client\s*\([^)]*[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        (r'@grpc\/grpc-js', ['js', 'ts']),
        (r'const\s+\w+\s*=\s*new\s+\w+Client\s*\([^)]*\)', ['js', 'ts']),
        
        # Java
        (r'ManagedChannel\s*\.\s*forTarget\s*\(\s*[\'"]([^\'"]+)[\'"]', ['java']),
        (r'ManagedChannelBuilder\.forAddress\s*\(\s*[\'"]([^\'"]+)[\'"]', ['java']),
    ],
    
    "websocket": [
        # JavaScript/TypeScript
        (r'new\s+WebSocket\s*\(\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts', 'jsx', 'tsx']),
        (r'socket\.io\s*\(\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        (r'io\s*\(\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        (r'new\s+Socket\s*\(\s*\{[^}]*url:\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        (r'ws\s*=\s*new\s+WebSocket\s*\(\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        
        # Python
        (r'websockets\.connect\s*\(\s*[\'"]([^\'"]+)[\'"]', ['py']),
        (r'asyncio\.run\s*\(\s*websockets\.connect\s*\(\s*[\'"]([^\'"]+)[\'"]', ['py']),
        (r'socketio\.Client\s*\(\)\.connect\s*\(\s*[\'"]([^\'"]+)[\'"]', ['py']),
        
        # Java
        (r'new\s+OkHttpClient\s*\(\)\.newWebSocket\s*\(\s*Request\s*\(\s*\)\.url\s*\(\s*[\'"]([^\'"]+)[\'"]', ['java']),
        
        # Go
        (r'websocket\.Dial\s*\(\s*ctx\s*,\s*[\'"]([^\'"]+)[\'"]', ['go']),
    ],
    
    "sse": [
        # Server-Sent Events
        (r'new\s+EventSource\s*\(\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        (r'EventSourcePolyfill\s*\(\s*[\'"]([^\'"]+)[\'"]', ['js', 'ts']),
        (r'@microsoft/fetch-event-source', ['js', 'ts']),
    ],
}

# 常见的第三方 API 域名
KNOWN_API_PROVIDERS = {
    # AI/ML APIs
    "api.openai.com": "OpenAI API",
    "api.anthropic.com": "Anthropic Claude API",
    "api.cohere.ai": "Cohere API",
    "api.replicate.com": "Replicate API",
    "generativelanguage.googleapis.com": "Google Gemini API",
    
    # Cloud Provider APIs
    "api.github.com": "GitHub API",
    "api.gitlab.com": "GitLab API",
    "api.bitbucket.org": "Bitbucket API",
    
    # Payment APIs
    "api.stripe.com": "Stripe API",
    "api-sandbox.dwolla.com": "Dwolla API",
    "api-m.sandbox.paypal.com": "PayPal Sandbox API",
    "api-m.paypal.com": "PayPal API",
    
    # Social Media APIs
    "api.twitter.com": "Twitter/X API v2",
    "graph.facebook.com": "Facebook Graph API",
    "api.linkedin.com": "LinkedIn API",
    
    # Communication APIs
    "api.twilio.com": "Twilio API",
    "api.sendgrid.net": "SendGrid API",
    "api.mailchimp.com": "Mailchimp API",
    "slack.com/api": "Slack API",
    "discord.com/api": "Discord API",
    
    # Map/Location APIs
    "maps.googleapis.com": "Google Maps API",
    "api.mapbox.com": "Mapbox API",
    "restapi.amap.com": "高德地图 API",
    
    # Cloud Storage APIs
    "s3.amazonaws.com": "AWS S3",
    "storage.googleapis.com": "Google Cloud Storage",
    "blob.core.windows.net": "Azure Blob Storage",
    
    # Chinese APIs
    "api.weixin.qq.com": "微信 API",
    "qyapi.weixin.qq.com": "企业微信 API",
    "api.alipay.com": "支付宝开放平台 API",
    "api-dashboard.dproducts.cn": "支付宝代扣",
    "api.didiyunapi.com": "滴滴云 API",
    "bdapi.haoservice.com": "好服务聚合API",
    
    # Monitoring/Analytics
    "api.datadoghq.com": "Datadog API",
    "api.newrelic.com": "New Relic API",
    "api.amplitude.com": "Amplitude API",
    "api.mixpanel.com": "Mixpanel API",
    "logs.segments.com": "Segment Logs API",
    
    # Search/APIs
    "api.algolia.com": "Algolia Search API",
    "api.searchstack.io": "SearchStack API",
    "api.meilisearch.com": "Meilisearch API",
    "universe.meili.com": "Meilisearch Cloud",
    
    # Database/Backend APIs
    "api.parse.com": "Parse API",
    "api.back4app.com": "Back4app API",
    "graphql.fauna.com": "Fauna GraphQL API",
    "us-east-1.aws.h牙orm.tv.amazondaws.com": "AppSync API",
}

# 需要跳过的目录
SKIP_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv', 
    'dist', 'build', 'coverage', '.next', '.nuxt', 'vendor',
    '.idea', '.vscode', '.eggs', '*.egg-info', '.tox', '.pytest_cache',
    'bin', 'obj', 'packages', '.nuget', 'target', '*.class',
}

# 文件扩展名到语言的映射
EXT_TO_LANG = {
    '.js': 'js', '.jsx': 'jsx', '.ts': 'ts', '.tsx': 'tsx',
    '.py': 'py', '.java': 'java', '.go': 'go', '.rs': 'rs',
    '.rb': 'rb', '.php': 'php', '.cs': 'cs', '.swift': 'swift', '.kt': 'kt',
    '.cjs': 'js', '.mjs': 'js', '.vue': 'vue', '.svelte': 'svelte',
}


class APIDependencyAnalyzer:
    """API 依赖分析器"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.apis: List[APICall] = []
        self.stats = {
            "total_apis": 0,
            "by_type": defaultdict(int),
            "by_provider": defaultdict(int),
            "by_method": defaultdict(int),
            "by_language": defaultdict(int),
            "files_analyzed": 0,
            "issues_found": defaultdict(int),
        }
        
    def analyze(self) -> Dict:
        """分析项目并返回结果"""
        print(f"Starting analysis of: {self.project_path}")
        
        for file_path in self._find_source_files():
            self._analyze_file(file_path)
            
        self._compute_stats()
        
        print(f"Scanned {self.stats['files_analyzed']} files")
        print(f"Found {self.stats['total_apis']} API calls")
        
        return self._generate_report()
    
    def _find_source_files(self) -> List[Path]:
        """查找所有源码文件"""
        if self.project_path.is_file():
            ext = self.project_path.suffix.lower()
            if ext in EXT_TO_LANG:
                return [self.project_path]
            return []
        
        files = []
        for root, dirs, filenames in os.walk(self.project_path):
            # 跳过不需要的目录
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
            
            for filename in filenames:
                ext = Path(filename).suffix.lower()
                if ext in EXT_TO_LANG:
                    files.append(Path(root) / filename)
                    
        return files
    
    def _analyze_file(self, file_path: Path):
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            self.stats["files_analyzed"] += 1
            
            # 获取语言
            lang = EXT_TO_LANG.get(file_path.suffix.lower(), 'unknown')
            self.stats["by_language"][lang] += 1
            
            # 检测各种 API 调用
            for api_type, patterns in API_PATTERNS.items():
                for pattern, langs in patterns:
                    if lang not in langs:
                        continue
                    self._find_pattern_matches(content, pattern, api_type, file_path, lang)
                            
        except Exception as e:
            print(f"Warning: Failed to analyze {file_path}: {e}")
    
    def _find_pattern_matches(self, content: str, pattern: str, api_type: str, file_path: Path, lang: str):
        """查找正则匹配"""
        try:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                url = self._extract_url(match, api_type)
                if url:
                    # 获取代码片段
                    line_num = content[:match.start()].count('\n') + 1
                    snippet = self._get_code_snippet(content, match.start(), match.end())
                    
                    api = APICall(
                        url=url,
                        type=api_type,
                        file=str(file_path.relative_to(self.project_path)),
                        line=line_num,
                        method=self._detect_http_method(content, match.start()),
                        provider=self._identify_provider(url),
                        issues=self._check_issues(url, api_type, content, match.start()),
                        code_snippet=snippet
                    )
                    self.apis.append(api)
        except re.error as e:
            pass  # 忽略无效的正则表达式
    
    def _extract_url(self, match, api_type: str) -> Optional[str]:
        """从正则匹配中提取 URL"""
        try:
            if api_type == "grpc":
                return f"grpc://{match.group(1)}" if match.lastindex >= 1 else None
            
            # 尝试获取第一个捕获组
            url = match.group(1) if match.lastindex and match.lastindex >= 1 else None
            
            # 验证 URL 格式
            if url:
                url = url.strip()
                if (url.startswith('http://') or url.startswith('https://') or 
                    url.startswith('/') or '://' in url):
                    return url
        except:
            pass
        return None
    
    def _get_code_snippet(self, content: str, start: int, end: int, context: int = 50) -> str:
        """获取代码片段"""
        start = max(0, start - context)
        end = min(len(content), end + context)
        snippet = content[start:end]
        # 清理多行内容
        snippet = ' '.join(snippet.split())
        return snippet[:200]
    
    def _detect_http_method(self, content: str, pos: int) -> str:
        """检测 HTTP 方法"""
        context = content[max(0, pos-300):pos]
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        
        # 查找方法名
        for method in methods:
            if re.search(rf'\b{method}\b', context, re.IGNORECASE):
                return method
        
        # 推断方法
        if 'post' in context.lower():
            return 'POST'
        elif 'put' in context.lower():
            return 'PUT'
        elif 'delete' in context.lower():
            return 'DELETE'
        elif 'patch' in context.lower():
            return 'PATCH'
        
        return 'GET'  # 默认 GET
    
    def _identify_provider(self, url: str) -> str:
        """识别 API 提供商"""
        # 移除协议和路径，只保留域名
        url_lower = url.lower()
        for domain, name in KNOWN_API_PROVIDERS.items():
            if domain in url_lower:
                return name
        return "Unknown"
    
    def _check_issues(self, url: str, api_type: str, content: str, pos: int) -> List[str]:
        """检查潜在问题"""
        issues = []
        
        # 检查是否使用 HTTP（不安全）
        if url.startswith('http://'):
            issues.append('insecure_http')
        
        # 检查是否使用非安全的 WebSocket
        if api_type == 'websocket' and url.startswith('ws://'):
            issues.append('insecure_ws')
        
        # 检查是否有认证
        context = content[max(0, pos-1000):pos+1000]
        has_auth = any(keyword in context.lower() for keyword in [
            'authorization', 'bearer', 'apikey', 'api_key', 'x-api-key',
            'auth', 'token', 'credential', 'jwt', 'oauth', 'signature'
        ])
        if not has_auth:
            issues.append('missing_auth')
        
        # 检查是否有超时设置
        if 'timeout' not in context.lower() and 'timeout' not in content.lower():
            issues.append('no_timeout')
        
        # 检查是否使用硬编码凭证
        if re.search(r'(password|secret|key)\s*[:=]\s*[\'"][^\'"]{8,}', context, re.IGNORECASE):
            issues.append('hardcoded_secret')
        
        return issues
    
    def _compute_stats(self):
        """计算统计信息"""
        self.stats["total_apis"] = len(self.apis)
        for api in self.apis:
            self.stats["by_type"][api.type] += 1
            self.stats["by_provider"][api.provider] += 1
            self.stats["by_method"][api.method] += 1
            for issue in api.issues:
                self.stats["issues_found"][issue] += 1
    
    def _generate_report(self) -> Dict:
        """生成分析报告"""
        return {
            "project": str(self.project_path),
            "version": VERSION,
            "timestamp": datetime.now().isoformat(),
            "stats": dict(self.stats),
            "apis": [asdict(api) for api in self.apis],
        }


def write_markdown_report(report: Dict, output_path: Path):
    """生成 Markdown 报告"""
    stats = report['stats']
    apis = report['apis']
    
    # 按问题分组
    apis_by_issue = defaultdict(list)
    for api in apis:
        for issue in api['issues']:
            apis_by_issue[issue].append(api)
    
    # 按类型分组
    apis_by_type = defaultdict(list)
    for api in apis:
        apis_by_type[api['type']].append(api)
    
    md = f"""# API Dependency Analysis Report

**Project**: `{report['project']}`  
**Analyzed**: {report['timestamp']}  
**Tool Version**: {report['version']}

## Summary

| Metric | Count |
|--------|-------|
| Total API Calls | {stats['total_apis']} |
| Files Scanned | {stats['files_analyzed']} |
| Issues Found | {sum(stats['issues_found'].values())} |

## API Types Distribution

| Type | Count | Percentage |
|------|-------|------------|
"""
    for api_type, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
        pct = (count / stats['total_apis'] * 100) if stats['total_apis'] > 0 else 0
        md += f"| {api_type} | {count} | {pct:.1f}% |\n"
    
    md += f"""
## Language Distribution

| Language | Files |
|----------|-------|
"""
    for lang, count in sorted(stats['by_language'].items(), key=lambda x: -x[1]):
        md += f"| {lang} | {count} |\n"
    
    md += f"""
## Top API Providers

| Provider | Calls |
|----------|-------|
"""
    for provider, count in sorted(stats['by_provider'].items(), key=lambda x: -x[1])[:10]:
        md += f"| {provider} | {count} |\n"
    
    md += f"""
## HTTP Methods

| Method | Count |
|--------|-------|
"""
    for method, count in sorted(stats['by_method'].items(), key=lambda x: -x[1]):
        md += f"| {method} | {count} |\n"
    
    # 问题汇总
    if stats['issues_found']:
        md += f"""
## Issues Summary

| Issue | Count | Severity |
|-------|-------|----------|
"""
        issue_descriptions = {
            'insecure_http': ('Uses HTTP instead of HTTPS', 'HIGH'),
            'insecure_ws': ('Uses non-secure WebSocket (ws://)', 'HIGH'),
            'missing_auth': ('No authentication detected', 'MEDIUM'),
            'no_timeout': ('No timeout configuration', 'LOW'),
            'hardcoded_secret': ('Potential hardcoded secret detected', 'CRITICAL'),
        }
        for issue, count in sorted(stats['issues_found'].items(), key=lambda x: -x[1]):
            desc, severity = issue_descriptions.get(issue, (issue, 'UNKNOWN'))
            md += f"| {issue} | {count} | {severity} |\n"
    
    # 按类型列出 API
    md += "\n## API Calls by Type\n\n"
    for api_type, type_apis in sorted(apis_by_type.items()):
        md += f"### {api_type.upper()} ({len(type_apis)} calls)\n\n"
        for api in type_apis[:20]:  # 限制显示数量
            issues_str = ', '.join(f'`{i}`' for i in api['issues']) if api['issues'] else '✅'
            md += f"""**{api['url']}**

- File: `{api['file']}:{api['line']}`
- Method: `{api['method']}`
- Provider: {api['provider']}
- Issues: {issues_str}

```
{api['code_snippet'][:100]}...
```

"""
        if len(type_apis) > 20:
            md += f"_... and {len(type_apis) - 20} more {api_type} calls_\n\n"
    
    md += f"""
---
*Generated by [api-dependency-analyzer](https://github.com/your-username/api-dependency-analyzer) v{VERSION}*
"""
    
    (output_path / 'api-report.md').write_text(md, encoding='utf-8')
    print(f"Markdown report: {output_path / 'api-report.md'}")


def write_json_report(report: Dict, output_path: Path):
    """生成 JSON 报告"""
    json_path = output_path / 'dependencies.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"JSON report: {json_path}")


def write_csv_report(report: Dict, output_path: Path):
    """生成 CSV 报告"""
    import csv
    
    csv_path = output_path / 'dependencies.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Type', 'Method', 'Provider', 'File', 'Line', 'Issues'])
        
        for api in report['apis']:
            writer.writerow([
                api['url'],
                api['type'],
                api['method'],
                api['provider'],
                api['file'],
                api['line'],
                '; '.join(api['issues']) if api['issues'] else ''
            ])
    
    print(f"CSV report: {csv_path}")


def main():
    parser = argparse.ArgumentParser(
        description='API Dependency Analyzer - Scan and analyze API dependencies in your codebase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan current directory
  python analyze_api.py --path .

  # Scan specific project
  python analyze_api.py --path /path/to/project --output ./report

  # JSON output only
  python analyze_api.py --path . --format json
        """
    )
    parser.add_argument('--path', required=True, help='Project path to analyze')
    parser.add_argument('--output', default='./api-analysis', help='Output directory')
    parser.add_argument('--format', choices=['json', 'markdown', 'csv', 'all'], default='all',
                        help='Output format (default: all)')
    
    args = parser.parse_args()
    
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    analyzer = APIDependencyAnalyzer(args.path)
    report = analyzer.analyze()
    
    if args.format in ('json', 'all'):
        write_json_report(report, output_path)
    
    if args.format in ('markdown', 'all'):
        write_markdown_report(report, output_path)
    
    if args.format in ('csv', 'all'):
        write_csv_report(report, output_path)
    
    print(f"\nAnalysis complete! Results saved to: {output_path}")


if __name__ == '__main__':
    main()
