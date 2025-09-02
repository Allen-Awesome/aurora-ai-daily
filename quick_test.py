#!/usr/bin/env python3
"""快速测试DeepSeek API"""

def test_api():
    try:
        import requests
        print("✅ requests库已安装")
    except ImportError:
        print("❌ 需要安装requests库: pip install requests")
        return
    
    # API配置
    api_key = "sk-7aeb9d632ece46688c945e19cf9bb7ce"
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "你好，请简单介绍一下DeepSeek"}
        ],
        "max_tokens": 50
    }
    
    print("🔧 正在测试DeepSeek API...")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            tokens = data.get('usage', {}).get('total_tokens', 'N/A')
            
            print("✅ API测试成功!")
            print(f"📝 回复: {content}")
            print(f"📊 消耗tokens: {tokens}")
            
        else:
            print(f"❌ API调用失败")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_api()
