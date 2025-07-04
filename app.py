# app.py
from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

# 儲存對話歷史
conversation_history = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_input = request.json.get('message', '')
        
        # 將用戶輸入添加到對話歷史
        conversation_history.append({"role": "user", "content": user_input})
        
        # 使用 OpenAI 客戶端調用 API
        completion = client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": "You are an expert software developer with deep knowledge across multiple programming languages, software architecture, and best practices. Your expertise includes:\n\n- Writing clean, efficient, and well-documented code\n- Debugging complex issues and optimizing performance\n- Following industry best practices and design patterns\n- Understanding tradeoffs between different technical approaches\n- Providing clear explanations of technical concepts\n- Testing, security, and code maintenance\n\nWhen responding to coding questions:\n1. First analyze the requirements carefully\n2. Consider multiple approaches and their tradeoffs\n3. Provide well-structured, production-ready code with comments\n4. Explain your implementation choices\n5. Include error handling and edge cases\n6. Suggest testing strategies when relevant."},
                *conversation_history  # 將對話歷史傳遞給模型
            ],
        )
        
        # 提取回應內容
        ai_response = completion.choices[0].message.content
        
        # 將 AI 回應添加到對話歷史
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        return jsonify({
            'success': True,
            'data': {
                'response': ai_response,
                'type': 'code' if '```' in str(ai_response) else 'text'
            },
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }), 500

if __name__ == '__main__':
    app.run(debug=True)