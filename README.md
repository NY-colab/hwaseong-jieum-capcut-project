# 화성 AI 영상 · 지음업싸이클링 CapCut 프로젝트

이 저장소는 편집 가능한 CapCut 프로젝트를 다른 Windows PC로 전달하기 위한 설치 도구입니다. 영상·음성·이미지·참조 글꼴·효과·UHD 처리 결과는 Git 기록 대신 **Releases**의 `hwaseong-jieum-capcut.zip`에 포함됩니다. GitHub의 `Source code (zip)`에는 편집 미디어가 들어 있지 않습니다.

[프로젝트 ZIP 다운로드](https://github.com/NY-colab/hwaseong-jieum-capcut-project/releases/latest/download/hwaseong-jieum-capcut.zip) · [Release 및 체크섬](https://github.com/NY-colab/hwaseong-jieum-capcut-project/releases/latest)

현재 공유본은 **84.77초**, 메인 트랙 **19개 클립의 UHD 품질 보정**, #3 코리요 한숨 장면, 분리된 #7 장면, 보강된 제목 음영·엔딩 글자와 BGM을 포함합니다. 전체 패키지 파일 해시·ZIP 무결성·323개 미디어/리소스 경로와 19개 UHD 캐시를 검증했습니다. 설치 스크립트는 별도 시험 데이터와 실제 패키지의 격리 설치로 검증했습니다. 격리 시험에서는 불변 미디어를 하드링크해 공간 사용을 줄였고, 기존 프로젝트 보존·새 이름/ID 등록·설치 후 324개 참조와 UHD 캐시 연결을 확인했습니다. 다른 PC에서 CapCut을 열어 재생하는 검수는 별도로 필요합니다.

## Codex에 붙여 넣을 요청

> https://github.com/NY-colab/hwaseong-jieum-capcut-project 에서 README와 설치 스크립트를 확인하고 최신 Release의 CapCut 프로젝트를 내 Windows PC에 설치해 주세요. 먼저 CapCut 실행 여부를 확인하고 실행 중이면 저장·종료를 요청해 주세요. 모든 다운로드의 SHA-256과 패키지 내부 파일 해시를 검증하고, 기존 프로젝트를 보존하면서 고유한 이름과 draft_id로 새 프로젝트를 등록해 주세요. 설치 후 누락된 미디어와 타임라인 연결을 오프라인으로 검증하고 실제 설치 경로를 알려 주세요. 앱을 자동 실행하지 마세요.

## Windows 설치

1. **Windows용 CapCut 9.6 이상**과 Python 3.10 이상을 준비합니다. 실제 확인에서 CapCut 9.5는 이 초안의 버전이 높아 열기를 거부했고 9.6에서 정상적으로 열렸습니다. 패키지 manifest에 기록된 `content_version`은 문서 형식 값이며 앱 버전과 다를 수 있습니다.
2. 열려 있는 CapCut 작업을 저장하고 **CapCut을 완전히 종료**합니다. 설치 스크립트는 실행 중인 앱을 종료하지 않습니다.
3. 이 저장소의 `download_install.ps1`을 저장한 폴더에서 실행합니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\download_install.ps1
```

다른 위치에 프로젝트를 저장하는 설정이면 `-DraftRoot "D:\실제\com.lveditor.draft"`를 지정합니다. 다운로드만 하려면 `-DownloadOnly`를 붙입니다. 특정 Release는 `-Tag "v2026.10.21"`처럼 지정합니다.

ZIP을 직접 받은 경우 같은 Release의 `SHA256SUMS.txt`와 SHA-256을 비교한 뒤 압축을 풀고 실행합니다.

```powershell
python .\install_project.py --verify-only
python .\install_project.py
```

설치기는 `원래이름_공유본`처럼 사용하지 않는 새 폴더를 만들며 기존 프로젝트를 덮어쓰지 않습니다. 새 `draft_id`를 발급하고 `root_meta_info.json`의 기존 항목과 증가 카운터를 보존합니다. 인덱스 변경 전에 백업을 만들고 경로·미디어·타임라인을 확인합니다. 설치 결과에 새 프로젝트 경로와 인덱스 백업 경로가 표시됩니다. 그다음 사용자가 CapCut을 열어 홈에서 해당 프로젝트를 선택합니다.

## 포함 범위와 확인

현재 타임라인 JSON, 실제 참조 미디어, 제목·크레딧 이미지, 사용 중인 UHD `Resources/videoAlg`, 음성, 참조 효과·전환 리소스와 글꼴 파일을 포함합니다. 렌더된 단일 영상으로 평면화하지 않습니다. 계정 연결·암호 키 저장소·기록·이전 백업·관계없는 프로젝트는 배포하지 않습니다. 비활성 음성 보정의 존재하지 않는 캐시 경로는 비웁니다. 활성 UHD 결과나 원본이 빠져 있으면 제작 패키징이 중단됩니다.

글꼴은 프로젝트 내부 참조용으로 배치하며 Windows에 전역 설치하지 않습니다. CapCut의 온라인 효과나 구독 기능은 받는 사람의 앱 버전·로그인·이용 권한에 따라 달라질 수 있습니다. 설치 스크립트의 오프라인 검증은 앱 재생·내보내기 검수를 대체하지 않습니다.

제작자는 저장 완료 후 고정된 스냅샷으로 패키징합니다. Release에는 ZIP(2 GiB 이상인 경우 분할 파일)과 `SHA256SUMS.txt`를 함께 올립니다. 미디어 권리 자체를 공개 라이선스로 양도하는 저장소가 아니며 별도 허락 없이 재배포하지 마세요.
