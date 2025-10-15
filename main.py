#!/usr/bin/env python3
"""
MP4 파일을 MP3로 변환하는 간단한 CLI 도구

사용 예시:
  - 단일 파일 변환:
      python3 convert_mp4_to_mp3.py input/video.mp4

  - 출력 디렉터리 지정:
      python3 convert_mp4_to_mp3.py input/video.mp4 -o output_dir

  - 디렉터리 내 모든 MP4 일괄 변환:
      python3 convert_mp4_to_mp3.py input_dir -r

  - 비트레이트 지정(기본: 192k):
      python3 convert_mp4_to_mp3.py input/video.mp4 -b 256k

사전 요구사항:
  - 시스템에 ffmpeg가 설치되어 있어야 합니다.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List


def ensure_ffmpeg_available() -> None:
    """ffmpeg 실행 가능 여부 확인.

    Raises:
        SystemExit: ffmpeg 미설치 시 사용자 안내와 함께 종료
    """
    if shutil.which("ffmpeg") is None:
        message_lines = [
            "ffmpeg가 설치되어 있지 않습니다.",
            "설치 방법:",
            "- macOS (Homebrew): brew install ffmpeg",
            "- Ubuntu/Debian:   sudo apt-get update && sudo apt-get install -y ffmpeg",
            "- Windows (scoop):  scoop install ffmpeg",
            "- Windows (choco):  choco install ffmpeg",
            "설치 후 다시 시도하세요.",
        ]
        print("\n".join(message_lines), file=sys.stderr)
        raise SystemExit(127)


def find_mp4_files(target: Path, recursive: bool) -> List[Path]:
    """대상 경로에서 변환할 mp4 파일 목록을 찾습니다."""
    if target.is_file():
        return [target] if target.suffix.lower() == ".mp4" else []

    pattern = "**/*.mp4" if recursive else "*.mp4"
    return sorted([p for p in target.glob(pattern) if p.is_file()])


def build_output_path(input_path: Path, output_dir: Path | None) -> Path:
    """입력 파일 기준으로 출력 mp3 경로를 생성."""
    if output_dir is None:
        return input_path.with_suffix(".mp3")

    output_dir.mkdir(parents=True, exist_ok=True)
    return (output_dir / input_path.name).with_suffix(".mp3")


def convert_one(input_path: Path, output_path: Path, bitrate: str, overwrite: bool) -> int:
    """ffmpeg를 호출하여 단일 파일을 변환.

    Returns:
        int: 프로세스 반환 코드 (0이 성공)
    """
    # -vn: 비디오 스트림 제거, -acodec libmp3lame: mp3 인코더, -b:a: 비트레이트
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y" if overwrite else "-n",
        "-i",
        str(input_path),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-b:a",
        bitrate,
        str(output_path),
    ]

    # ffmpeg는 -n일 때 이미 존재하면 1을 반환하므로, 그 경우 사용자에게 안내
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("ffmpeg 실행 파일을 찾을 수 없습니다. 설치를 확인하세요.", file=sys.stderr)
        return 127


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MP4를 MP3로 변환",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input",
        type=Path,
        help="입력 MP4 파일 또는 디렉터리",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="출력 MP3를 저장할 디렉터리 (지정하지 않으면 입력 파일과 동일한 위치)",
    )
    parser.add_argument(
        "-b",
        "--bitrate",
        default="192k",
        help="오디오 비트레이트 (예: 128k, 192k, 256k)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="디렉터리 입력 시 하위 폴더까지 재귀적으로 검색",
    )
    parser.add_argument(
        "-y",
        "--overwrite",
        action="store_true",
        help="출력 파일이 존재하면 덮어쓰기",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    ensure_ffmpeg_available()

    target: Path = args.input
    if not target.exists():
        print(f"입력 경로를 찾을 수 없습니다: {target}", file=sys.stderr)
        return 2

    inputs = find_mp4_files(target, args.recursive)
    if not inputs:
        print("변환할 MP4 파일을 찾지 못했습니다.", file=sys.stderr)
        return 1

    total = len(inputs)
    failures = 0

    for idx, src in enumerate(inputs, start=1):
        dst = build_output_path(src, args.output_dir)
        print(f"[{idx}/{total}] 변환 중: {src} -> {dst}")
        code = convert_one(src, dst, args.bitrate, args.overwrite)
        if code == 0:
            continue
        elif code == 1 and not args.overwrite and dst.exists():
            print(f"스킵: 출력 파일이 이미 존재합니다 (덮어쓰지 않음): {dst}")
        else:
            failures += 1
            print(f"실패 (코드 {code}): {src}", file=sys.stderr)

    if failures:
        print(f"완료: 성공 {total - failures} / 실패 {failures}")
        return 1

    print(f"완료: 총 {total}개 파일 변환 성공")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


