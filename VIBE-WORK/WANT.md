

## 마이크로서비스(MSA) 아키텍처 설계 : 

- Docker·FastAPI 기반 Whisper STT API 서버를 독립 컨테이너로 구축
- 키오스크 마이크입력 → STT → LLM(의도 파악) → TTS로 이어지는 음성 비서 파이프라인을 모듈화

- 보이스 클로닝 기술 검증 : Qwen3-TTS-12Hz-1.7B 모델과 In-Context Learning(ICL) 기법을 적용해 수 초 분량의 참조 음성만으로
zero-shot 음성 복제를 검증, 점주·브랜드 모델 목소리를 활용한 맞춤형 음성 인터페이스 구현 가능성 확인

- 최첨단 GPU 환경 트러블슈팅 : RTX 5090(Blackwell) 아키텍처 및 CUDA 12.8/13.0, PyTorch 환경을 구성하고, 라이브러리 파라미
터 충돌 이슈를 코드 패치로 직접 해결하여 신뢰성 높은 백엔드 운용 능력 확보

- 확장성 있는 서비스 설계 : STT/TTS 서버를 독립 컨테이너로 분리해 다수 키오스크 단말의 동시 요청에도 부하 분산·스케일 아웃
이 유연한 백엔드 구조로 설계

## 파일 구성

> 모든 docker 이미지와 컨테이너 이름은 stts-* 로

- .env.example : 환경변수 샘플
- .env : 환경변수 (git에 포함하지 않음) <= docker-compose.yml 에서 사용
- docker : 도커 관련 폴더
- docker/build.sh : docker/images 하위폴더의 docker 이미지 빌드
- docker/start.sh : docker compose 시작
- docker/stop.sh : docker compose 중지
- docker/reset.sh : docker compose 중지 및 컨테이너 삭제
- docker/compose/docker-compose.yml
- docker/images/{필요도커들}/Dockerfile : docker 파일
- docker/images/{필요도커들}/VERSION : 버전파일 (YYMMDD-hhmm 형식) 소스가 변경될 때마다 현재 시각으로 업데이트

