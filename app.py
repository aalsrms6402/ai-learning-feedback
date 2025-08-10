from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    name = data['name']
    results = data['results']

    prompt = f"{name} 학생의 시험 결과:\n{results}\n위 내용을 분석하고 맞춤 학습 전략을 제시해 주세요."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        feedback = response.choices[0].message['content']
    except Exception as e:
        feedback = f"오류 발생: {e}"

    return jsonify({"feedback": feedback})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
