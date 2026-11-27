#!/usr/bin/env python3
"""Self-test the whole super-skill package — run before shipping any update.

Usage:  python3 scripts/selftest.py [--fast] [--network]
Output: PASS/FAIL table + summary. Exit 0 = package healthy.
--fast    skips slow demos (video). --network adds live URL checks.
"""
import argparse
import py_compile
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
results: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def sh(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, check=False)


def test_syntax() -> None:
    for py in sorted(SCRIPTS.glob("*.py")):
        try:
            py_compile.compile(str(py), doraise=True)
            record(f"compile {py.name}", True)
        except py_compile.PyCompileError as exc:
            record(f"compile {py.name}", False, str(exc)[:80])
    for shf in sorted(SCRIPTS.glob("*.sh")):
        r = sh(["bash", "-n", str(shf)])
        record(f"bash -n {shf.name}", r.returncode == 0)


def test_deps() -> None:
    """Optional deps for the bundled scripts — warn clearly instead of cryptic failures."""
    optional = {"PIL": "pillow", "imageio_ffmpeg": "imageio-ffmpeg",
                "imageio": "imageio", "docx": "python-docx",
                "openpyxl": "openpyxl", "matplotlib": "matplotlib"}
    missing = [pkg for mod, pkg in optional.items()
               if not _module_available(mod)]
    if missing:
        hint = "pip install -r requirements.txt  (or: pip install " + " ".join(missing) + ")"
        print(f"⚠️  optional deps missing: {', '.join(missing)}\n   → {hint}\n")
        record("optional deps", False, "missing: " + ", ".join(missing))
    else:
        record("optional deps", True, "all present")


def _module_available(mod: str) -> bool:
    import importlib.util
    try:
        return importlib.util.find_spec(mod) is not None
    except Exception:
        return False


def test_manifest() -> None:
    """MANIFEST.json integrity — catches tampered/partial copies."""
    r = sh([sys.executable, str(SCRIPTS / "make_manifest.py"), "--verify"])
    record("manifest verify", r.returncode == 0, r.stdout.strip()[-80:])


def test_router() -> None:
    cases = [
        ("ye CSV ka analysis karo", "data-ai-memory"),
        ("kuch design kro", "creative-media"),
        ("security review karo", "security"),
        ("landing page banao", "coding-dev"),
        ("research karo sources ke saath", "research-web"),
        ("youtube seo karo is video ka", "video-youtube"),
    ]
    for task, expect in cases:
        r = sh([sys.executable, str(SCRIPTS / "choose_playbook.py"), task])
        ok = expect in r.stdout
        record(f"route '{task[:24]}'", ok, f"want {expect}" if not ok else "")


def test_scripts_fast() -> None:
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        # office_validate
        (t / "x.py").write_text(
            "import openpyxl; wb=openpyxl.Workbook(); wb.active['A1']='t'; wb.save(r'%s')" % (t / "a.xlsx"))
        sh([sys.executable, str(t / "x.py")])
        r = sh([sys.executable, str(SCRIPTS / "office_validate.py"), str(t / "a.xlsx")])
        record("office_validate ok-file", r.returncode == 0)
        r = sh([sys.executable, str(SCRIPTS / "office_validate.py"), str(t / "missing.docx")])
        record("office_validate missing-file fails", r.returncode == 1)
        # csv_profile + chart
        csv = t / "s.csv"
        csv.write_text("name,age\nA,30\nB,25\n")
        r = sh([sys.executable, str(SCRIPTS / "csv_profile.py"), str(csv)])
        record("csv_profile", r.returncode == 0)
        r = sh([sys.executable, str(SCRIPTS / "chart.py"), str(csv), "--col", "age",
                "--x", "name", "--out", str(t / "c.png")])
        record("chart", r.returncode == 0 and (t / "c.png").exists())
        # palette
        r = sh([sys.executable, str(SCRIPTS / "palette.py"), "#7c3aed", "--svg", str(t / "p.svg")])
        record("palette", r.returncode == 0 and (t / "p.svg").exists())
        # html_template
        r = sh([sys.executable, str(SCRIPTS / "html_template.py"), "T", str(t / "h.html")])
        record("html_template", r.returncode == 0 and (t / "h.html").exists())
        # docx_report
        md = t / "r.md"; md.write_text("# H\n\n- a\n- b\n")
        r = sh([sys.executable, str(SCRIPTS / "docx_report.py"), str(md), str(t / "r.docx")])
        record("docx_report", r.returncode == 0 and (t / "r.docx").exists())
        # secrets_scan exit codes
        (t / "bad.py").write_text('password = "hunter2secret"\n')
        (t / "ok.py").write_text("x = 1\n")
        r1 = sh([sys.executable, str(SCRIPTS / "secrets_scan.py"), str(t / "bad.py")])
        r2 = sh([sys.executable, str(SCRIPTS / "secrets_scan.py"), str(t / "ok.py")])
        record("secrets_scan detect/clean", r1.returncode == 1 and r2.returncode == 0)
        # git_commit_msg in temp repo
        sh(["git", "init", "-q"], cwd=t)
        sh(["git", "config", "user.email", "t@t"], cwd=t)
        sh(["git", "config", "user.name", "t"], cwd=t)
        (t / "m.py").write_text("a=1\n")
        sh(["git", "add", "-A"], cwd=t)
        sh(["git", "commit", "-qm", "init"], cwd=t)
        (t / "m.py").write_text("a=2\n")
        sh(["git", "add", "-A"], cwd=t)
        r = sh([sys.executable, str(SCRIPTS / "git_commit_msg.py")], cwd=t)
        record("git_commit_msg", r.returncode == 0 and "SUGGESTED" in r.stdout)
        # run_checks list
        (t / "package.json").write_text("{}")
        r = sh([sys.executable, str(SCRIPTS / "run_checks.py"), str(t), "--list"])
        record("run_checks --list", r.returncode == 0)
        # new_skill.sh
        r = sh(["bash", str(SCRIPTS / "new_skill.sh"), "selftest-skill", "desc"], cwd=t)
        ok1 = r.returncode == 0 and (t / "selftest-skill" / "SKILL.md").exists()
        r2 = sh(["bash", str(SCRIPTS / "new_skill.sh"), "Bad_Name"], cwd=t)
        record("new_skill create+reject", ok1 and r2.returncode == 1)
        # health_check local (expect down port fail = exit1 with one target)
        r = sh([sys.executable, str(SCRIPTS / "health_check.py"), "--tcp", "localhost:1"],
               timeout=20)
        record("health_check down-port", r.returncode == 1)
        # soffice graceful (127 or success if libreoffice present)
        r = sh(["bash", str(SCRIPTS / "soffice_convert.sh"), str(t / "r.docx"), "pdf"],
               timeout=60)
        record("soffice graceful", r.returncode in (0, 127))
        # youtube_seo kit (no clips)
        r = sh([sys.executable, str(SCRIPTS / "youtube_seo.py"),
                "Test Topic", "--out", str(t / "seo.md")])
        record("youtube_seo kit", r.returncode == 0 and (t / "seo.md").exists()
               and "Titles" in (t / "seo.md").read_text())
        # make_srt from wav+txt pairs
        import struct, math, wave as _wave
        (t / "a").mkdir(); (t / "t").mkdir()
        for n, secs in ((1, 0.4), (2, 0.3)):
            w = _wave.open(str(t / "a" / f"s{n:02d}.wav"), "wb")
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
            w.writeframes(b"".join(
                struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / 8000)))
                for i in range(int(8000 * secs))))
            w.close()
            (t / "t" / f"s{n:02d}.txt").write_text(
                "Hello world test line. Doosra sentence yahan hai.", encoding="utf-8")
        r = sh([sys.executable, str(SCRIPTS / "make_srt.py"), "--audio", str(t / "a"),
                "--text", str(t / "t"), "--out", str(t / "s.srt")])
        record("make_srt", r.returncode == 0 and "-->" in (t / "s.srt").read_text())
        # concat_video on two tiny demo clips
        for n in (1, 2):
            sh([sys.executable, str(SCRIPTS / "make_video.py"), "--demo",
                "--duration", "0.2", "--fps", "6", "--size", "160x90",
                "--out", str(t / f"j{n}.mp4")], timeout=60)
        r = sh([sys.executable, str(SCRIPTS / "concat_video.py"),
                str(t / "j1.mp4"), str(t / "j2.mp4"), "--out", str(t / "j.mp4")],
               timeout=60)
        record("concat_video", r.returncode == 0 and (t / "j.mp4").exists())


def test_video(fast: bool) -> None:
    if fast:
        record("make_video (skipped --fast)", True)
        return
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "v.mp4"
        r = sh([sys.executable, str(SCRIPTS / "make_video.py"), "--demo",
                "--duration", "0.3", "--fps", "8", "--size", "320x180",
                "--out", str(out)], timeout=90)
        record("make_video demo", r.returncode == 0 and out.exists() and out.stat().st_size > 0)


def test_network() -> None:
    r = sh(["bash", str(SCRIPTS / "check_urls.sh"), "https://example.com"], timeout=30)
    record("check_urls live", r.returncode == 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--network", action="store_true")
    args = ap.parse_args()

    print("super-skill self-test\n" + "=" * 46)
    test_deps()
    test_syntax()
    test_manifest()
    test_router()
    test_scripts_fast()
    test_video(args.fast)
    if args.network:
        test_network()

    fails = 0
    for name, ok, detail in results:
        mark = "✅" if ok else "❌"
        print(f"{mark} {name}" + (f"  — {detail}" if (detail and not ok) else ""))
        if not ok:
            fails += 1
    print("=" * 46)
    total = len(results)
    print(f"{total - fails}/{total} passed" + (" — PACKAGE HEALTHY ✅" if fails == 0
                                               else f" — {fails} FAILURE(S) ❌"))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
