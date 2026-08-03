import json
import re
import requests
import config

class LLMOrderParser:
    def __init__(self, engine_type=config.LLM_ENGINE, model_name=config.LLM_MODEL_NAME):
        self.engine_type = engine_type
        self.model_name = model_name
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self):
        menu_str = ", ".join(config.KIOSK_MENU)
        return f"""당신은 무인 키오스크의 음성 주문 처리 AI 시스템입니다.
고객이 음성(STT 텍스트)으로 주문하면, 판매 메뉴 목록에서 상품명과 수량을 분석하여 정확한 JSON 데이터로만 응답하세요.

[판매 메뉴 목록]
{menu_str}

[응답 규칙]
1. 반드시 아래의 JSON 포맷으로만 응답해야 하며, 그 외의 추가 설명이나 마크다운 백틱(```json 등)은 절대 붙이지 마세요.
2. 주문 텍스트에서 매칭되는 상품과 정확한 수량을 추출하세요. 메뉴에 없는 항목은 제외하세요.
3. response_text에는 고객에게 안내할 친절하고 명확한 안내음성 문장을 작성하세요.
   (예: "아이스 아메리카노 2잔, 아이스 카페라떼 1잔 맞으신가요? 카드리더기에 카드를 꽂아주세요.")

[JSON 출력 형식]
{{
  "orders": [
    {{"item": "메뉴이름", "quantity": 수량(숫자)}}
  ],
  "response_text": "고객 안내음성 문장"
}}
"""

    def parse_order(self, user_text):
        """
        STT로 인식된 고객 텍스트를 입력받아 메뉴/수량 JSON 및 TTS 안내문 생성
        """
        if not user_text.strip():
            return {
                "orders": [],
                "response_text": "죄송합니다. 음성이 잘 들리지 않았습니다. 다시 말씀해 주시겠어요?"
            }

        print(f"🧠 [LLM] 의도 파악 및 주문 분석 요청중... ({self.engine_type}: {self.model_name})")

        if self.engine_type == "ollama":
            return self._call_ollama(user_text)
        elif self.engine_type == "openai_api":
            return self._call_openai(user_text)
        else:
            # 기본 폴백: 간단한 규칙 기반 파서 (Ollama/API 미구동 시 예시)
            return self._fallback_rule_parser(user_text)

    def _call_ollama(self, user_text):
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"고객 주문: \"{user_text}\""}
                ],
                "stream": False,
                "format": "json"
            }
            response = requests.post(config.OLLAMA_API_URL, json=payload, timeout=10)
            if response.status_code == 200:
                content = response.json().get("message", {}).get("content", "")
                return self._clean_and_parse_json(content)
            else:
                print(f"⚠️ [Ollama Error] HTTP {response.status_code}. 규칙 기반 폴백을 사용합니다.")
                return self._fallback_rule_parser(user_text)
        except Exception as e:
            print(f"⚠️ [Ollama Error] {e}. 규칙 기반 폴백으로 전환합니다.")
            return self._fallback_rule_parser(user_text)

    def _call_openai(self, user_text):
        try:
            headers = {
                "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_text}
                ],
                "response_format": {"type": "json_object"}
            }
            res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"]
                return self._clean_and_parse_json(content)
            else:
                return self._fallback_rule_parser(user_text)
        except Exception as e:
            print(f"⚠️ [OpenAI API Error] {e}")
            return self._fallback_rule_parser(user_text)

    def _clean_and_parse_json(self, raw_content):
        try:
            cleaned = re.sub(r'```(?:json)?', '', raw_content).strip('` \n')
            data = json.loads(cleaned)
            return data
        except json.JSONDecodeError:
            print(f"❌ [JSON Parse Error] raw response: {raw_content}")
            return {
                "orders": [],
                "response_text": "주문 내용을 정확히 이해하지 못했습니다. 메뉴판을 확인 후 다시 말씀해 주세요."
            }

    def _fallback_rule_parser(self, user_text):
        """
        LLM 서버가 없거나 네트워크 오프라인 상태일 때 작동하는 엣지 폴백 파서
        """
        orders = []
        # 숫자 키워드 매핑
        num_map = {"한": 1, "1": 1, "두": 2, "2": 2, "세": 3, "3": 3, "네": 4, "4": 4, "다섯": 5, "5": 5}
        
        for item in config.KIOSK_MENU:
            if item in user_text:
                qty = 1
                for k, v in num_map.items():
                    if f"{item} {k}" in user_text or f"{item} {k}잔" in user_text:
                        qty = v
                        break
                orders.append({"item": item, "quantity": qty})

        if orders:
            summary = ", ".join([f"{o['item']} {o['quantity']}잔" for o in orders])
            response_text = f"{summary} 맞으신가요? 카드리더기에 카드를 꽂아주세요."
        else:
            response_text = "주문하신 메뉴를 확인하지 못했습니다. 다시 한번 말씀해 주세요."

        return {
            "orders": orders,
            "response_text": response_text
        }
