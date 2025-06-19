# 🍎 Auto Maple macOS 시작 가이드

## 🚀 빠른 시작

### 1. 터미널에서 프로젝트 폴더로 이동
```bash
cd /Users/ogf2002/macro/auto-maple-mac
```

### 2. 설치 및 실행 (원클릭)
```bash
./run.sh
```

또는 단계별로:

### 3. 수동 설치
```bash
# 의존성 설치
./install.sh

# 시스템 테스트
python3 test_system.py

# 실행
python3 main.py
```

## 🔑 접근성 권한 설정

**반드시 필요한 단계입니다!**

1. `시스템 환경설정` 열기
2. `보안 및 개인 정보 보호` 클릭
3. `개인 정보 보호` 탭 선택
4. 왼쪽에서 `손쉬운 사용` 클릭
5. 🔒 자물쇠 클릭하고 비밀번호 입력
6. `터미널` 앱을 목록에 추가 (+ 버튼)
7. 체크박스 활성화

## 🎮 사용법

### 기본 컨트롤
- **F1** 또는 **`** (백틱): 봇 활성화/비활성화
- **ESC**: 프로그램 종료

### GUI 사용
1. "Load Command Book" - 캐릭터 명령어 파일 로드
2. "Load Routine" - 매크로 루틴 파일 로드
3. "Enable Bot" 체크박스로 봇 시작/정지

## 📁 파일 구조

```
auto-maple-mac/
├── run.sh              # 원클릭 실행 스크립트
├── install.sh          # 설치 스크립트  
├── test_system.py      # 시스템 테스트
├── main.py             # 메인 프로그램
├── requirements.txt    # 파이썬 의존성
├── README.md           # 상세 문서
└── src/                # 소스 코드
    ├── modules/        # 핵심 모듈들
    └── common/         # 공통 유틸리티
```

## 🛠️ 문제 해결

### 권한 오류가 발생하는 경우
```bash
chmod +x *.sh *.py
```

### Python 모듈 오류가 발생하는 경우
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 화면 캡처가 안 되는 경우
1. 접근성 권한 다시 확인
2. 시스템 환경설정에서 `화면 기록` 권한도 확인

### 게임 창을 찾을 수 없는 경우
- 메이플스토리/메이플랜드가 실행 중인지 확인
- 창이 최소화되지 않았는지 확인

## 🎯 다음 단계

1. **명령어 파일 작성**: `resources/command_books/` 폴더에 캐릭터별 스킬 정의
2. **루틴 파일 작성**: `resources/routines/` 폴더에 매크로 시퀀스 정의
3. **템플릿 교체**: `assets/` 폴더의 더미 이미지를 실제 게임 이미지로 교체

## 📞 지원

문제가 있으면:
1. `python3 test_system.py` 실행하여 상태 확인
2. 터미널 출력 메시지 확인
3. 접근성 권한 재설정

---

**준비 완료!** 🎉 
`./run.sh` 실행하고 메이플 매크로를 시작하세요!
