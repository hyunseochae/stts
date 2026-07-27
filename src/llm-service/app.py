import os
import json
import time
import httpx
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="LLM Intent Recognition Microservice (vLLM Engine)",
    description="FastAPI based LLM Intent Parsing Container Service powered by vLLM (openai/gpt-oss-20b)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VLLM_URL = os.getenv("VLLM_URL", "http://172.17.0.1:11434/v1")
VLLM_MODEL = os.getenv("VLLM_MODEL", "openai/gpt-oss-20b")

class IntentRequest(BaseModel):
    user_text: str
    context: Optional[Dict[str, Any]] = None

class IntentResponse(BaseModel):
    status: str
    user_text: str
    intent: str
    confidence: float
    parsed_data: Dict[str, Any]
    response_text: str
    voice_style: str
    processing_time_seconds: float


SYSTEM_PROMPT = """You are a smart, polite, and efficient AI Kiosk Assistant for a cafe/store.
Your task is to analyze the user's spoken input and return a JSON object with:
1. "intent": One of ["ORDER", "RECOMMEND", "INFO", "GENERAL"]
2. "confidence": float between 0.0 and 1.0
3. "parsed_data": Object containing details (e.g. items, options, quantities, info_type)
4. "response_text": A natural, polite Korean spoken response for the customer (Keep it clear and under 2 sentences).

Examples:
- Input: "아이스 아메리카노 한 잔 주세요"
  Output: {"intent": "ORDER", "confidence": 0.98, "parsed_data": {"items": [{"item": "아메리카노", "temperature": "ice", "quantity": 1}]}, "response_text": "아이스 아메리카노 한 잔 주문 접수되었습니다. 카드를 결제기에 꽂아주세요."}
- Input: "인기 메뉴 추천해 줘"
  Output: {"intent": "RECOMMEND", "confidence": 0.95, "parsed_data": {"recommendation_type": "best_seller"}, "response_text": "저희 매장의 시그니처 인기 메뉴는 아이스 연유라떼와 클래식 샌드위치입니다."}
- Input: "화장실 어디 있어요?"
  Output: {"intent": "INFO", "confidence": 0.95, "parsed_data": {"info_type": "restroom"}, "response_text": "화장실은 매장 우측 통로 끝에 위치해 있습니다."}

Respond strictly in valid JSON format only, without markdown codeblock syntax or any additional explanation.
"""


async def call_vllm_gptoss_20b(user_text: str) -> tuple[str, float, dict, str]:
    if not user_text or not user_text.strip():
        return "GENERAL", 0.50, {"empty_input": True}, "음성이 잘 들리지 않았습니다. 다시 말씀해 주시겠어요?"

    prompt_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"User spoken input: '{user_text}'"}
    ]

    payload = {
        "model": VLLM_MODEL,
        "messages": prompt_messages,
        "temperature": 0.1,
        "max_tokens": 256
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            url = f"{VLLM_URL.rstrip('/')}/chat/completions"
            res = await client.post(url, json=payload)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"].strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()
                data = json.loads(content)
                intent = data.get("intent", "GENERAL")
                confidence = float(data.get("confidence", 0.9))
                parsed_data = data.get("parsed_data", {})
                response_text = data.get("response_text", f"네, '{user_text}' 처리해 드리겠습니다.")
                return intent, confidence, parsed_data, response_text
        except Exception as e:
            print(f"[vLLM Error] Call to {VLLM_URL} failed: {e}. Falling back to Rule Parser.")

    return "GENERAL", 0.70, {"fallback": True}, f"말씀하신 '{user_text}' 내용 처리해 드리겠습니다."


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    vllm_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{VLLM_URL.rstrip('/')}/models")
            vllm_status = "connected" if r.status_code == 200 else f"http_{r.status_code}"
    except Exception as e:
        vllm_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "llm-service",
        "engine": f"vLLM ({VLLM_MODEL})",
        "vllm_url": VLLM_URL,
        "vllm_connection": vllm_status
    }


@app.post("/api/v1/intent", response_model=IntentResponse)
async def analyze_intent(request: IntentRequest):
    user_text = request.user_text.strip() if request.user_text else ""
    start_time = time.time()
    intent, confidence, parsed_data, response_text = await call_vllm_gptoss_20b(user_text)
    processing_time = time.time() - start_time

    return IntentResponse(
        status="success",
        user_text=user_text,
        intent=intent,
        confidence=confidence,
        parsed_data=parsed_data,
        response_text=response_text,
        voice_style="brand_owner_voice",
        processing_time_seconds=round(processing_time, 4)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=False)
