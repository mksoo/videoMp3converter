# MP4 → MP3 변환기 (CLI)

ffmpeg를 사용하여 MP4 파일(동영상)에서 오디오를 추출해 MP3로 변환하는 간단한 Python 스크립트입니다.

## 사전 요구사항
- ffmpeg 설치 필수
  - macOS (Homebrew): `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y ffmpeg`
  - Windows (scoop): `scoop install ffmpeg`
  - Windows (Chocolatey): `choco install ffmpeg`

## 사용법
```bash
# 기본 사용 (./video 디렉터리의 mp4를 ./audio로 변환)
python3 main.py

# 재귀적으로 하위 폴더까지 검색
python3 main.py -r

# 단일 파일 변환
python3 main.py path/to/video.mp4

# 출력 디렉터리 지정
python3 main.py path/to/video.mp4 -o out_dir

# 디렉터리 내 모든 mp4 일괄 변환
python3 main.py path/to/input_dir -r

# 비트레이트 지정 (기본 192k)
python3 main.py path/to/video.mp4 -b 256k

# 이미 존재하는 출력 파일 덮어쓰기
python3 main.py -y
```

## 옵션
- `input`: 입력 MP4 파일 또는 디렉터리 (기본값: ./video)
- `-o, --output-dir`: 출력 MP3 저장 디렉터리 (기본값: ./audio)
- `-b, --bitrate`: 오디오 비트레이트 (예: 128k, 192k, 256k, 기본값: 192k)
- `-r, --recursive`: 디렉터리 입력 시 하위 폴더까지 검색
- `-y, --overwrite`: 동일 이름의 파일이 있을 때 덮어쓰기

## 작동 원리
- ffmpeg로 비디오 스트림을 제거(`-vn`), `libmp3lame` 코덱으로 인코딩합니다.
- 기본 비트레이트는 `192k`이며, 필요 시 옵션으로 변경 가능합니다.

## 문제 해결
- `ffmpeg: command not found` 오류: ffmpeg 설치 후 쉘을 재시작하거나 PATH 환경변수를 확인하세요.
- 출력 파일이 이미 존재하여 스킵되는 경우: `-y` 옵션으로 덮어쓰세요.
