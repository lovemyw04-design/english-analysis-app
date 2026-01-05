import streamlit as st
import google.generativeai as genai
import json
import re

# --- 설정 (Gemini API 연결) ---
# 여기에 발급받은 API 키를 입력하세요.
GEN_AI_API_KEY = "YOUR_GEMINI_API_KEY" 
genai.configure(api_key=GEN_AI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 앱 UI 구성 ---
st.set_page_config(layout="wide", page_title="AI 영어 지문 분석기")

st.title("📝 AI 영어 지문 분석기")
st.write("영어 지문을 입력하면 전문적인 문장 분석지를 생성합니다.")

# 입력창
user_input = st.text_area("영어 지문을 입력하세요:", height=200, placeholder="여기에 영어 본문을 붙여넣으세요...")

# --- 프롬프트 설정 ---
SYSTEM_PROMPT = """
당신은 영어 교육 전문가입니다. 입력된 지문을 분석하여 교육용 HTML 분석지 데이터를 생성해야 합니다.
결과는 반드시 아래의 JSON 형식을 엄격히 지켜서 출력하세요.

JSON 구조 예시:
{
  "title": "주제 영문제목",
  "subtitle": "주제 한글소제목",
  "full_en": "영어 본문 전체",
  "full_ko": "한글 번역 전체",
  "sentences": [
    {
      "no": 1,
      "en": "영어 문장",
      "ko": "한글 해석",
      "grammar": "핵심 문법 설명 (HTML태그 사용 가능)",
      "structure": [
        {"role": "S", "en": "주어부분", "ko": "설명"},
        {"role": "V", "en": "동사부분", "ko": "설명"}
      ]
    }
  ],
  "summary": "글의 요지",
  "logic_flow": ["단계1", "단계2"],
  "vocab": [{"word": "단어", "meaning": "뜻"}]
}
"""

if st.button("분석지 생성하기"):
    if not user_input:
        st.error("지문을 입력해주세요.")
    else:
        with st.spinner("AI가 지문을 정밀 분석 중입니다..."):
            # Gemini 호출
            response = model.generate_content([SYSTEM_PROMPT, user_input])
            
            try:
                # JSON 데이터 추출 (마크다운 태그 제거)
                json_data = re.search(r'\{.*\}', response.text, re.DOTALL).group()
                data = json.loads(json_data)

                # --- HTML 템플릿 렌더링 ---
                html_template = f"""
                <style>
                    .page {{ padding: 24px; background: #ffffff; font-family: sans-serif; color: #111827; border: 1px solid #e5e7eb; border-radius: 12px; }}
                    .divider-main {{ border-top: 2px solid #111827; margin: 12px 0; }}
                    .title {{ font-size: 20px; font-weight: 700; }}
                    .layout {{ display: flex; gap: 20px; }}
                    .left {{ flex: 3; }}
                    .right {{ flex: 1.5; }}
                    .block {{ border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin-bottom: 15px; }}
                    .sentence-item {{ border-bottom: 1px dashed #e5e7eb; padding: 10px 0; }}
                    .sent-no {{ color: #2563eb; font-weight: bold; margin-right: 8px; }}
                    .structure-table {{ width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 5px; }}
                    .structure-table th, .structure-table td {{ border: 1px solid #e5e7eb; padding: 5px; text-align: left; }}
                    .vocab-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
                    .vocab-table td {{ border: 1px solid #e5e7eb; padding: 4px; }}
                </style>

                <div class="page">
                    <div class="title">{data['title']} <span style="font-size:14px; color:#4b5563;">| {data['subtitle']}</span></div>
                    <div class="divider-main"></div>
                    
                    <div class="layout">
                        <div class="left">
                            <div class="block">
                                <strong>[본문 전체]</strong><br><br>
                                <div style="font-size:13px; line-height:1.6;">{data['full_en']}</div>
                                <hr>
                                <div style="font-size:13px; color:#4b5563; background:#f9fafb; padding:10px;">{data['full_ko']}</div>
                            </div>

                            <div class="block">
                                <strong>[문장별 정밀 분석]</strong>
                """

                for s in data['sentences']:
                    html_template += f"""
                    <div class="sentence-item">
                        <div><span class="sent-no">{s['no']}</span> {s['en']}</div>
                        <div style="font-size:12px; color:#4b5563; margin:5px 0;">{s['ko']}</div>
                        <div style="font-size:11px; color:#dc2626;">💡 {s['grammar']}</div>
                        <table class="structure-table">
                            <tr style="background:#f3f4f6;"><th>역할</th><th>영어</th><th>설명</th></tr>
                    """
                    for st_item in s['structure']:
                        html_template += f"<tr><td><b>{st_item['role']}</b></td><td>{st_item['en']}</td><td>{st_item['ko']}</td></tr>"
                    html_template += "</table></div>"

                html_template += f"""
                            </div>
                        </div>
                        <div class="right">
                            <div class="block">
                                <strong>주제 및 요지</strong><br>
                                <p style="font-size:12px;">{data['summary']}</p>
                            </div>
                            <div class="block">
                                <strong>글의 흐름</strong><br>
                                <ul style="font-size:11px;">
                """
                for flow in data['logic_flow']:
                    html_template += f"<li>{flow}</li>"

                html_template += """
                                </ul>
                            </div>
                            <div class="block">
                                <strong>어휘 정리</strong><br>
                                <table class="vocab-table">
                """
                for v in data['vocab']:
                    html_template += f"<tr><td>{v['word']}</td><td>{v['meaning']}</td></tr>"

                html_template += """
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                """
                
                # 결과 출력
                st.html(html_template)
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")
                st.write(response.text) # AI가 준 원문 확인용
