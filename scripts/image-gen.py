#!/usr/bin/env python3
"""
image-gen.py - Gemini Image API 调用脚本
用于 Claude Code image-gen skill，封装 API 调用和配置管理。

输出协议:
  成功: OK:/absolute/path/to/image.png
  失败: ERROR:TYPE:message

退出码: 0=成功, 1=网络错误, 2=API错误, 3=配置错误, 4=解码/IO错误
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse


def load_config(config_path):
    """读取配置文件，环境变量优先。"""
    config = {}

    # 从配置文件读取
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR:CONFIG:Invalid JSON in {config_path}: {e}", file=sys.stdout)
            sys.exit(3)
        except IOError as e:
            print(f"ERROR:CONFIG:Cannot read {config_path}: {e}", file=sys.stdout)
            sys.exit(3)

    # 环境变量优先覆盖
    if os.environ.get('IMAGE_GEN_URL'):
        config['api_url'] = os.environ['IMAGE_GEN_URL']
    if os.environ.get('IMAGE_GEN_API_KEY'):
        config['api_key'] = os.environ['IMAGE_GEN_API_KEY']
    if os.environ.get('IMAGE_GEN_PROXY'):
        config['proxy'] = os.environ['IMAGE_GEN_PROXY']

    # 验证必填字段
    if not config.get('api_url'):
        print("ERROR:CONFIG:Missing api_url (set in config file or IMAGE_GEN_URL env var)", file=sys.stdout)
        sys.exit(3)
    if not config.get('api_key'):
        print("ERROR:CONFIG:Missing api_key (set in config file or IMAGE_GEN_API_KEY env var)", file=sys.stdout)
        sys.exit(3)

    # 默认值
    config.setdefault('image_size', '1K')

    return config


def call_api(config, prompt):
    """调用 Gemini Image API，返回 base64 图片数据。"""
    request_body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"imageSize": config.get('image_size', '1K')}
        }
    }

    data = json.dumps(request_body).encode('utf-8')

    parsed_url = urllib.parse.urlparse(config['api_url'])
    host = parsed_url.hostname

    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'x-goog-api-key': config['api_key'],
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36',
        'host': host,
    }

    req = urllib.request.Request(config['api_url'], data=data, headers=headers, method='POST')

    # 代理支持：优先使用配置文件中的 proxy；无 proxy 时显式禁用以避免系统代理干扰
    proxy = config.get('proxy')
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({
            'http': proxy,
            'https': proxy,
        })
        opener = urllib.request.build_opener(proxy_handler)
    else:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    try:
        with opener.open(req, timeout=180) as response:
            response_data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = ''
        try:
            body = e.read().decode('utf-8', errors='replace')
        except Exception:
            pass
        print(f"ERROR:API:{e.code} {e.reason} - {body[:200]}", file=sys.stdout)
        sys.exit(2)
    except urllib.error.URLError as e:
        print(f"ERROR:NETWORK:{e.reason}", file=sys.stdout)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR:NETWORK:{e}", file=sys.stdout)
        sys.exit(1)

    # 从响应中提取图片数据
    try:
        candidates = response_data.get('candidates', [])
        if not candidates:
            print("ERROR:API:No candidates in response", file=sys.stdout)
            sys.exit(2)

        parts = candidates[0].get('content', {}).get('parts', [])
        for part in parts:
            inline_data = part.get('inlineData', {})
            mime_type = inline_data.get('mimeType', '')
            if mime_type.startswith('image/'):
                return inline_data['data'], mime_type

        print("ERROR:API:No image in response", file=sys.stdout)
        sys.exit(2)
    except (KeyError, IndexError) as e:
        print(f"ERROR:API:Unexpected response structure: {e}", file=sys.stdout)
        sys.exit(2)


def save_image(base64_data, output_path):
    """解码 base64 并保存为图片文件。"""
    try:
        image_bytes = base64.b64decode(base64_data)
    except Exception as e:
        print(f"ERROR:DECODE:Invalid base64 data: {e}", file=sys.stdout)
        sys.exit(4)

    # 确保输出目录存在
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
    except IOError as e:
        print(f"ERROR:IO:Cannot write to {output_path}: {e}", file=sys.stdout)
        sys.exit(4)

    return os.path.abspath(output_path)


def main():
    parser = argparse.ArgumentParser(description='Gemini Image API caller for image-gen skill')
    parser.add_argument('--prompt', required=True, help='Image generation prompt')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--config', default=os.path.expanduser('~/.claude/image-gen.json'),
                        help='Config file path (default: ~/.claude/image-gen.json)')
    args = parser.parse_args()

    config = load_config(args.config)
    base64_data, mime_type = call_api(config, args.prompt)
    abs_path = save_image(base64_data, args.output)
    print(f"OK:{abs_path}", file=sys.stdout)


if __name__ == '__main__':
    main()
