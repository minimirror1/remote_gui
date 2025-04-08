import requests
import json
import time
import random
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API 엔드포인트 및 인증 설정
BASE_URL = "https://robot-monitor-dev.systemiic.com"
API_ENDPOINT = "/v1/service/stores/log"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-token-here"  # 실제 토큰으로 교체 필요
}

# 상점 및 PC 구성
STORE_ID = "store123"
PC_ID = "pc1"

# 성공한 이벤트 요청에 사용된 값들로 제한
# 성공 분석: 단순한 ON/OFF 이벤트만 성공함
EVENT_OPTIONS = ["ON", "OFF"]
OBJECT_STATUS_OPTIONS = ["ON", "OFF"]

def send_log():
    """
    성공한 패턴을 기반으로 로그 전송 함수 구현
    """
    # 로봇 ID
    robot_id = f"robot_{random.randint(1, 5)}"
    
    # 이벤트와 상태는 단순화 - 성공한 패턴만 사용
    event_type = random.choice(EVENT_OPTIONS)
    object_status = random.choice(OBJECT_STATUS_OPTIONS)
    
    # 가장 단순한 형태의 페이로드 구성
    payload = {
        "storeId": STORE_ID,
        "pcId": PC_ID,
        "objectInfo": {
            "objectId": robot_id,
            "objectStatus": object_status,
            "electricCurrent": str(random.uniform(0.5, 4.5)),
            "error": "",
            "operatingStatus": "PLAY"
        },
        "event": event_type
    }
    
    url = BASE_URL + API_ENDPOINT
    
    try:
        # JSON 문자열로 변환
        payload_str = json.dumps(payload)
        logger.debug(f"전송 페이로드: {payload_str}")
        
        response = requests.post(
            url, 
            data=payload_str,
            headers=HEADERS
        )
        
        if response.status_code == 200 or response.status_code == 201:
            logger.info(f"로그 전송 성공: {payload['objectInfo']['objectId']}, 이벤트: {payload['event']}")
            return True
        else:
            logger.error(f"로그 전송 실패, 상태 코드: {response.status_code}, 응답: {response.text}")
            logger.error(f"전송된 데이터: {payload_str}")
            return False
    except Exception as e:
        logger.error(f"요청 중 오류 발생: {str(e)}")
        return False

def main():
    """
    메인 함수: 1초마다 로그 전송
    """
    logger.info(f"로그 전송 시작: {STORE_ID}/{PC_ID}")
    logger.info(f"단순화된 페이로드 형식으로 전송 (성공한 패턴 기반)")
    
    try:
        while True:
            send_log()
            time.sleep(1)  # 1초 대기
    except KeyboardInterrupt:
        logger.info("사용자에 의해 프로그램 종료")
    except Exception as e:
        logger.error(f"프로그램 오류: {str(e)}")

if __name__ == "__main__":
    main() 