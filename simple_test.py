import requests
import json

# 测试DeepSeek API
def test_deepseek():
    api_key = "sk-7aeb9d632ece46688c945e19cf9bb7ce"
    base_url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "请用一句话介绍人工智能"}
        ],
        "max_tokens": 100
    }
    
    print("🔧 测试DeepSeek API连接...")
    print(f"📍 API地址: {base_url}")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    print("-" * 50)
    
    try:
        response = requests.post(base_url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print("✅ API连接成功!")
            print(f"📝 回答: {answer}")
            print(f"📊 使用tokens: {result.get('usage', {}).get('total_tokens', 'N/A')}")
            return True
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_deepseek()
