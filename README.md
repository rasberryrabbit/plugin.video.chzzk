# CHZZK Kodi Addon

네이버 CHZZK 라이브 스트리밍 서비스를 Kodi에서 시청할 수 있게 해주는 비공식 애드온입니다.

## 주요 기능

- **라이브 스트림 시청**: CHZZK의 모든 공개 라이브 방송 시청
- **VOD (다시보기) 재생**: 지난 방송 다시보기
- **클립 재생**: 짧은 클립 재생
- **추천 라이브**: CHZZK 추천 라이브 목록
- **팔로잉 라이브**: (로그인 시) 팔로잉 채널의 라이브
- **검색**: 라이브, 채널, 다시보기 검색
- **카테고리**: 카테고리별 라이브 탐색
- **고화질 지원**: 1080p 재생 (인증 시)
- **한국어/영어 UI**: 완전 다국어 지원

## 설치 방법

### 1단계: ZIP 파일 다운로드
`plugin.video.chzzk-0.1.0.zip` 파일을 다운로드합니다.

### 2단계: Kodi에 설치
1. Kodi 실행
2. **설정(톱니바퀴)** → **시스템** → **애드온** → **알 수 없는 소스** 활성화
3. **애드온** → **박스 아이콘(열린 상자)** → **zip 파일에서 설치**
4. 다운로드한 zip 파일 선택
5. "CHZZK add-on installed" 메시지 대기

### 3단계: (선택) 네이버 인증 설정
팔로잉 목록과 19금 콘텐츠를 보려면 네이버 인증이 필요합니다:

1. PC 브라우저에서 https://chzzk.naver.com 로그인
2. **F12** → **Application** 탭 → **Cookies** → `https://chzzk.naver.com`
3. `NID_AUT` 값 복사
4. `NID_SES` 값 복사
5. Kodi → CHZZK 애드온 설정 → **로그인 설정**
6. NID_AUT, NID_SES 필드에 각각 붙여넣기

## 사용 방법

### 메인 메뉴
1. **추천 라이브**: CHZZK 추천 라이브 스트림 표시
2. **팔로잉 라이브**: (로그인 필요) 팔로잉 채널의 라이브
3. **검색**: 라이브/채널/VOD 검색
4. **카테고리**: 카테고리별 라이브 탐색
5. **설정**: 애드온 설정

### 라이브 시청
1. 메인 메뉴 → **추천 라이브** 또는 **검색**
2. 시청할 스트림 선택
3. 자동으로 HLS 재생 시작

### VOD 시청
1. 메인 메뉴 → **검색** → **다시보기 검색**
2. 원하는 VOD 선택
3. 자동으로 재생

## 호환성

- **Kodi 19 (Matrix)** 이상
- **CoreELEC, LibreELEC, Android, Windows, Linux, macOS** 지원
- **InputStream Adaptive** 권장 (고화질 재생용)
- 1GB RAM 환경에서 작동 (CoreELEC X96 Mini 테스트 완료)

## 기술적 세부 사항

### API 엔드포인트
이 애드온은 CHZZK의 비공식 API를 사용합니다:
- `https://api.chzzk.naver.com/service/v2/channels/{channel_id}/live-detail`
- `https://api.chzzk.naver.com/service/v1/channels/{channel_id}/live-playback-json`
- `https://api.chzzk.naver.com/service/v2/videos/{video_id}`
- `https://api.chzzk.naver.com/service/v1/play-info/clip/{clip_id}`

### HLS 스트림 처리
CHZZK 라이브 스트림은 HLS 프로토콜을 사용하며, `__bgda__` 쿼리 파라미터가 필요합니다. 이 애드온은 streamlink의 CHZZK 플러그인에서 영감을 받아 동일한 처리 방식을 사용합니다.

## 제한 사항

1. **비공식 API**: CHZZK API가 변경되면 작동하지 않을 수 있습니다.
2. **지역 제한**: 한국 외에서 접근 시 일부 콘텐츠 제한될 수 있습니다.
3. **19금 콘텐츠**: 네이버 인증 필요
4. **채팅 미지원**: Kodi 특성상 채팅 참여는 불가능합니다.
5. **API 호출 제한**: 과도한 호출 시 차단될 수 있습니다.

## 문제 해결

### "라이브 정보를 가져올 수 없습니다"
- 채널 ID가 올바른지 확인
- 인터넷 연결 확인
- CHZZK 서비스가 정상인지 확인

### "19금 콘텐츠입니다"
- 설정에서 NID_AUT, NID_SES 입력
- 인증 값이 만료되지 않았는지 확인

### 재생이 안 됨
- inputstream.adaptive 애드온 설치 확인
- Kodi 재시작
- 네트워크 연결 확인

### 팔로잉 목록이 비어 있음
- NID_AUT, NID_SES 설정 확인
- 팔로우한 채널이 라이브 중인지 확인

## 라이선스

GPL-3.0-only

## 참고 자료

- [Streamlink CHZZK plugin](https://github.com/streamlink/streamlink/blob/master/src/streamlink/plugins/chzzk.py)
- [python-chzzk](https://github.com/jonghwanhyeon/python-chzzk)
- [CHZZK Wikipedia](https://en.wikipedia.org/wiki/CHZZK)

## 면책 조항

- 이 애드온은 비공식이며 CHZZK/네이버와 관련이 없습니다.
- CHZZK는 네이버의 상표입니다.
- 모든 콘텐츠의 저작권은 CHZZK와 각 스트리머에게 있습니다.
- 사용자의 국가/지역 법률을 준수하여 사용하세요.
