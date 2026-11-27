#!/usr/bin/env python3
"""Quality-control a rendered video — video-studio QC gate.

Checks: container/streams, resolution/fps, decode integrity (full null-decode),
loudness (EBU R128 via ebur128), silence ratio, and optional subtitle sanity.
Writes QC.md with PASS/WARN/FAIL per check. Never presents unvalidated output.

Usage:
  vs_qc.py video.mp4 [--srt subs.srt] [--target-i -14] [--max-silence 2.0]
                     [--out QC.md]
Exit: 0 = all checks pass, 1 = at least one FAIL.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def ff() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        print("missing dependency: imageio-ffmpeg — run: pip install imageio-ffmpeg",
              file=sys.stderr)
        sys.exit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--srt", default=None)
    ap.add_argument("--target-i", type=float, default=-14.0)
    ap.add_argument("--max-silence", type=float, default=2.0)
    ap.add_argument("--out", default="QC.md")
    args = ap.parse_args()

    ffmpeg = ff()
    v = Path(args.video)
    if not v.exists():
        print(f"not found: {v}", file=sys.stderr)
        return 1

    checks: list[tuple[str, str, str]] = []  # (name, status, detail)

    # 1) probe streams
    pr = subprocess.run([ffmpeg, "-i", str(v)], capture_output=True, text=True)
    err = pr.stderr
    has_video = "Video:" in err
    has_audio = "Audio:" in err
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", err)
    dur = float(m.group(1)) * 3600 + float(m.group(2)) * 60 + float(m.group(3)) if m else 0
    m = re.search(r"Video: \w+.*? (\d+)x(\d+)", err, re.DOTALL)
    res = f"{m.group(1)}x{m.group(2)}" if m else "?"
    m = re.search(r"([\d.]+) fps", err)
    fps = m.group(1) if m else "?"
    checks.append(("streams", "PASS" if has_video else "FAIL",
                   f"video={has_video} audio={has_audio} {res}@{fps}fps {dur:.1f}s"))

    # 2) full decode integrity
    dec = subprocess.run([ffmpeg, "-v", "error", "-i", str(v), "-f", "null", "-"],
                         capture_output=True, text=True)
    clean = dec.returncode == 0 and not dec.stderr.strip()
    checks.append(("decode", "PASS" if clean else "FAIL",
                   "full decode clean" if clean else dec.stderr.strip()[-120:]))

    # 3) loudness (EBU R128)
    if has_audio:
        r = subprocess.run([ffmpeg, "-i", str(v), "-af", "ebur128=peak=true",
                            "-f", "null", "-"], capture_output=True, text=True)
        # ebur128 prints per-window readings; the summary is the LAST one
        m_all = re.findall(r"I:\s*(-?[\d.]+) LUFS", r.stderr)
        mpeak_all = re.findall(r"Peak:\s*(-?[\d.]+) dBFS", r.stderr)
        m = m_all[-1] if m_all else None
        mpeak = mpeak_all[-1] if mpeak_all else None
        if m:
            li = float(m)
            tol = 1.0
            status = "PASS" if abs(li - args.target_i) <= tol else "WARN"
            checks.append(("loudness", status,
                           f"I={li} LUFS (target {args.target_i}, "
                           f"{'peak ' + mpeak + ' dBFS' if mpeak else 'peak ?'})"))
        else:
            checks.append(("loudness", "WARN", "could not measure (silent audio?)"))
    else:
        checks.append(("loudness", "WARN", "no audio stream"))

    # 4) silence ratio
    if has_audio:
        r = subprocess.run([ffmpeg, "-i", str(v), "-af",
                            f"silencedetect=noise=-40dB:d={args.max_silence}",
                            "-f", "null", "-"], capture_output=True, text=True)
        silent = re.findall(r"silence_start: ([\d.]+)", r.stderr)
        checks.append(("silence", "PASS" if not silent else "WARN",
                       f"{len(silent)} silence gap(s) > {args.max_silence}s"
                       + (f" (first at {silent[0]}s)" if silent else "")))

    # 5) subtitle sanity
    if args.srt:
        sp = Path(args.srt)
        if not sp.exists():
            checks.append(("subtitles", "FAIL", f"missing {sp}"))
        else:
            txt = sp.read_text(encoding="utf-8", errors="replace")
            times = re.findall(r"(\d+):(\d+):(\d+) -->", txt)
            last_end = 0.0
            bad = 0
            for hh, mm, ss in times:
                st = int(hh) * 3600 + int(mm) * 60 + int(ss)
                if st < last_end - 0.5:
                    bad += 1
                last_end = max(last_end, st)
            checks.append(("subtitles", "PASS" if not bad else "WARN",
                           f"{len(times)} cues, {bad} overlapping, "
                           f"last start {last_end}s vs duration {dur:.1f}s"))

    # report
    npass = sum(1 for _, s, _ in checks if s == "PASS")
    nfail = sum(1 for _, s, _ in checks if s == "FAIL")
    lines = [f"# QC — {v.name}", "",
             f"- file: `{v}` ({v.stat().st_size // 1024} KB)",
             f"- result: **{npass} PASS / {len(checks) - npass - nfail} WARN / {nfail} FAIL**",
             "", "| Check | Status | Detail |", "|---|---|---|"]
    lines += [f"| {n} | {s} | {d} |" for n, s, d in checks]
    out = Path(args.out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {out}")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
