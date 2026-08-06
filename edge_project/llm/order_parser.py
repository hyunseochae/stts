import json
import re
import difflib
import requests
import config

class LLMOrderParser:
    def __init__(self, engine_type=config.LLM_ENGINE, model_name=config.LLM_MODEL_NAME):
        self.engine_type = engine_type
        self.model_name = model_name
        
        # 자주 발생하는 STT 뭉개짐/오타 직관 교정 사전
        self.phonetic_dict = {
            # 바닐라 라떼 뭉개짐/발음 오타 패턴
            "반일라럭대": "바닐라 라떼",
            "반일라 럭대": "바닐라 라떼",
            "반일날 어때": "바닐라 라떼",
            "반일날어때": "바닐라 라떼",
            "반일라어때": "바닐라 라떼",
            "반일라라떼": "바닐라 라떼",
            "반일라 라떼": "바닐라 라떼",
            "바닐라 어때": "바닐라 라떼",
            "바릴라랍때": "바닐라 라떼",
            "바닐라랍때": "바닐라 라떼",
            "바릴라라떼": "바닐라 라떼",
            "바닐라라떼": "바닐라 라떼",
            
            # 초코 라떼 뭉개짐/발음 오타 패턴
            "초코랫대": "초코 라떼",
            "초코렛대": "초코 라떼",
            "초코라대": "초코 라떼",
            "초코래떼": "초코 라떼",
            "초코라떼": "초코 라떼",
            
            # 기타 메뉴 오타 패턴
            "아이스틱": "아이스티",
            "아메리카나": "아메리카노",
            "레몬에이두": "레몬에이드",
            "레몬에이트": "레몬에이드"
        }
        
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self):
        menu_str = ", ".join(config.KIOSK_MENU)
        return f"""당신은 무인 키오스크의 음성 주문 처리 AI 전문가입니다.
고객이 음성(STT 텍스트)으로 주문하면, 판매 메뉴 목록에서 해당되는 메뉴와 수량을 정확한 JSON 데이터로 추출하세요.

[판매 메뉴 목록]
{menu_str}

[중요: STT 발음 오류 교정 가이드]
음성 인식(STT) 특성상 발음이 뭉개지거나 유사한 소리의 텍스트로 인식될 수 있습니다.
- 예시: '바릴라랍때' -> '바닐라 라떼'
- 예시: '아이스틱' -> '아이스티'
- 예시: '초코랫대', '초코렛대' -> '초코 라떼'

[응답 규칙]
1. 반드시 아래의 JSON 포맷으로만 응답해야 하며, 그 외의 설명이나 마크다운 백틱(```json 등)은 절대 붙이지 마세요.
2. response_text에는 고객에게 안내할 친절하고 명확한 안내음성 문장을 작성하세요.

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

        # 1차: 사전 기반 음성 오타 교정
        corrected_text = self._correct_stt_text(user_text)
        print(f"🧠 [LLM] 입력 원문: \"{user_text}\" ➔ 발음 교정: \"{corrected_text}\"")

        if self.engine_type == "ollama":
            return self._call_ollama(corrected_text)
        elif self.engine_type == "openai_api":
            return self._call_openai(corrected_text)
        else:
            return self._fallback_rule_parser(corrected_text)

    def _correct_stt_text(self, text):
        """
        음성 인식 오타 사전 및 정규식 패턴 기반 음성 뭉개짐 보정
        """
        result = text
        
        # 1. 정규식 패턴 보정 (동적 발음 변형 처리)
        result = re.sub(r'(바닐라|바릴라|반일라|반일날)\s*(랍|락|랩|라|럭)?\s*(대|때|데|태|어때)', '바닐라 라떼', result)
        result = re.sub(r'(초코|조코|쵸코)\s*(랍|락|랩|라|랫|렛|래)?\s*(대|때|데|태)', '초코 라떼', result)
        result = re.sub(r'(아이스|아이)\s*(티|틱|티이)', '아이스티', result)
        result = re.sub(r'(레몬|래몬)\s*(에이드|에이두|에이트)', '레몬에이드', result)
        result = re.sub(r'(아메리카노|아메리카나|아메리카누)', '아메리카노', result)

        # 2. 사전 기반 1:1 치환 보정
        for wrong, right in self.phonetic_dict.items():
            result = result.replace(wrong, right)
            
        return result

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
                return self._fallback_rule_parser(user_text)
        except Exception:
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
        except Exception:
            return self._fallback_rule_parser(user_text)

    def _clean_and_parse_json(self, raw_content):
        try:
            cleaned = re.sub(r'```(?:json)?', '', raw_content).strip('` \n')
            data = json.loads(cleaned)
            return data
        except json.JSONDecodeError:
            return {
                "orders": [],
                "response_text": "주문 내용을 정확히 이해하지 못했습니다. 메뉴판을 확인 후 다시 말씀해 주세요."
            }

    def _fallback_rule_parser(self, user_text):
        """
        메뉴 직접 매칭 및 위치 기반 정확한 수량 추출 알고리즘
        """
        num_map = {
            "한": 1, "1": 1, "하나": 1, "일": 1,
            "두": 2, "2": 2, "둘": 2, "이": 2,
            "세": 3, "3": 3, "셋": 3, "삼": 3,
            "네": 4, "4": 4, "넷": 4, "사": 4,
            "다섯": 5, "5": 5, "오": 5
        }

        text = user_text
        orders = []

        # 메뉴 목록 중 사용자의 텍스트에 포함된 메뉴 찾기
        for item in config.KIOSK_MENU:
            item_no_space = item.replace(' ', '')
            text_no_space = text.replace(' ', '')

            if item in text or item_no_space in text_no_space:
                qty = 1
                tokens = text.split()
                
                # 해당 메뉴가 위치한 토큰 인덱스 찾기
                for idx, tok in enumerate(tokens):
                    clean_tok = re.sub(r'[^\w]', '', tok)
                    if item_no_space in clean_tok or item.split()[-1] in clean_tok:
                        # 바로 뒤/앞 토큰 범위에서 수량 단어 탐색
                        search_scope = tokens[idx:idx+3] + tokens[max(0, idx-1):idx]
                        
                        qty_found = False
                        for s in search_scope:
                            s_clean = re.sub(r'[^\w]', '', s)
                            # '주세요'의 '세'가 숫자 3으로 잘못 오인되는 현상 방지
                            if any(ex in s_clean for ex in ['주세요', '하세요', '에이드', '아이스티', '아메리카노', '라떼']):
                                continue

                            for k, v in num_map.items():
                                if k in s_clean:
                                    qty = v
                                    qty_found = True
                                    break
                            if qty_found:
                                break
                        if qty_found:
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
