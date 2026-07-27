import os
import re
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="LLM Intent Recognition Microservice",
    description="FastAPI based Intent Parsing & Response Generation Container Service for Kiosk Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


def parse_kiosk_intent(text: str) -> tuple[str, float, dict, str]:
    text_clean = text.strip()
    
    # 1. Order Intent Matching
    order_keywords = ["주문", "주세요", "한 잔", "두 잔", "세 잔", "아메리카노", "라떼", "음료", "아이스", "따뜻한"]
    if any(k in text_clean for k in order_keywords):
        # Extract temp option
        temp = "ice" if "아이스" in text_clean or "차거운" in text_clean else "hot"
        
        # Extract item
        item = "아메리카노"
        if "라떼" in text_clean:
            item = "카페라떼"
        elif "에이드" in text_clean:
            item = "자몽에이드"
        elif "티" in text_clean or "차" in text_clean:
            item = "유자차"

        # Quantity parsing using exact patterns to prevent substring false positives (e.g. '세' in '안녕하세요')
        qty = 1
        if re.search(r'(두\s*잔|두\s*개|둘|2\s*잔|2\s*개)', text_clean):
            qty = 2
        elif re.search(r'(세\s*잔|세\s*개|셋|3\s*잔|3\s*개)', text_clean):
            qty = 3
        elif re.search(r'(네\s*잔|네\s*개|넷|4\s*잔|4\s*개)', text_clean):
            qty = 4
        elif re.search(r'(다섯\s*잔|다섯\s*개|5\s*잔|5\s*개)', text_clean):
            qty = 5
        elif re.search(r'(한\s*잔|한\s*개|하나|1\s*잔|1\s*개)', text_clean):
            qty = 1
        else:
            num_match = re.search(r'(\d+)\s*(잔|개)', text_clean)
            if num_match:
                qty = int(num_match.group(1))

        parsed = {"items": [{"item": item, "temperature": temp, "quantity": qty}]}
        temp_str = "아이스" if temp == "ice" else "따뜻한"
        response_text = f"{temp_str} {item} {qty}잔 주문 접수되었습니다. 카드를 결제기에 꽂아주세요."
        return "ORDER", 0.95, parsed, response_text

    # 2. Recommendation Intent Matching
    recommend_keywords = ["추천", "인기", "잘 나가는", "무슨 메뉴", "뭐가 맛있"]
    if any(k in text_clean for k in recommend_keywords):
        parsed = {"recommendation_type": "best_seller"}
        response_text = "저희 매장의 시그니처 인기 메뉴는 아이스 연유라떼와 클래식 샌드위치입니다. 어떤 것으로 준비해드릴까요?"
        return "RECOMMEND", 0.92, parsed, response_text

    # 3. Store Info Intent Matching
    info_keywords = ["화장실", "주차", "영업시간", "와이파이", "위치"]
    if any(k in text_clean for k in info_keywords):
        if "화장실" in text_clean:
            info_type = "restroom"
            response_text = "화장실은 매장 우측 통로 끝에 위치해 있으며, 비밀번호는 1234번입니다."
        elif "주차" in text_clean:
            info_type = "parking"
            response_text = "결제 후 영수증 하단의 바코드로 출차 시 2시간 무료 주차 정산이 가능합니다."
        else:
            info_type = "general"
            response_text = "카운터 직원이 안내해드리겠습니다. 잠시만 기다려주세요."
        parsed = {"info_type": info_type}
        return "INFO", 0.90, parsed, response_text

    # 4. Fallback General Conversation
    parsed = {"fallback": True}
    response_text = f"말씀하신 '{text_clean}' 처리 항목을 확인 중입니다. 카운터에서 도와드리겠습니다."
    return "GENERAL", 0.70, parsed, response_text


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "llm-service",
        "engine": "Kiosk Rule-based & LLM Intent Engine"
    }


@app.post("/api/v1/intent", response_model=IntentResponse)
async def analyze_intent(request: IntentRequest):
    if not request.user_text or not request.user_text.strip():
        raise HTTPException(status_code=400, detail="User text is empty.")

    start_time = time.time()
    intent, confidence, parsed_data, response_text = parse_kiosk_intent(request.user_text)
    processing_time = time.time() - start_time

    return IntentResponse(
        status="success",
        user_text=request.user_text,
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
