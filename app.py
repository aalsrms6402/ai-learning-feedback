from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import openai

app = Flask(__name__)
CORS(app)  # 모든 도메인에 대해 CORS 허용 (배포 시 제한 권장)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise RuntimeError('OPENAI_API_KEY 환경변수가 설정되지 않았습니다.')
openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = (
    "You are an educational diagnostic assistant for high school students. "
    "Given a short text describing wrong answers and brief context, return a JSON object with keys:"
    " weak_units (array of strings), plan (string, step-by-step study plan), tips (array of short tips)."
)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    raw = data.get('rawInput', '')
    student = data.get('studentName', '학생')

    if not raw.strip():
        return jsonify({'ok': False, 'error': 'rawInput required'}), 400

    user_prompt = (
        f"Student name: {student}\n"
        f"Problem notes:\n{raw}\n\n"
        "Instructions: Identify the top 3 weakest units/topics with brief reason, "
        "and produce a concise study plan (1-week) and 3 quick tips. Return only valid JSON."
    )

    try:
        resp = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800,
            temperature=0.2,
        )

        text = resp['choices'][0]['message']['content'].strip()

        try:
            payload = json.loads(text)
        except Exception:
            payload = {'weak_units': [], 'plan': text, 'tips': []}

        return jsonify({
            'ok': True,
            'diagnosis': payload.get('weak_units', []),
            'plan': payload.get('plan', text),
            'tips': payload.get('tips', []),
            'raw_model': text
        })

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

