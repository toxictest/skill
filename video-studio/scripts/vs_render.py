#!/usr/bin/env python3
"""Render a scene manifest into a real, edited MP4 — video-studio renderer.

Per scene: image → Ken Burns motion (zoompan) → on-screen title overlay.
Between scenes: crossfade transitions (xfade) on video + acrossfade on audio.
Audio: concatenated narration, optional background music (looped, ducked,
faded in/out), final loudness normalized to -14 LUFS / -1 dBTP (YouTube
standard). Output: H.264 yuv420p + AAC + faststart.

Usage:
  vs_render.py scene_manifest.json --out video.mp4
      [--images-dir dir] [--music track.mp3] [--xfade 0.5]
      [--bgm-volume 0.18] [--work workdir]
Images: scene's "image" path wins; else <images-dir>/scene_01.png etc.;
else a generated branded placeholder card (so the pipeline never dead-ends).
Exit: 0 = rendered (prints duration + size + decode check), 1 = fail.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def ff() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        print("missing dependency: imageio-ffmpeg — run: pip install imageio-ffmpeg",
              file=sys.stderr)
        sys.exit(1)


def find_font() -> str | None:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    try:
        import matplotlib
        p = (Path(matplotlib.__file__).parent / "mpl-data/fonts/ttf"
             / "DejaVuSans-Bold.ttf")
        if p.exists():
            return str(p)
    except ImportError:
        pass
    return None


def probe_dur(ffmpeg: str, path: Path) -> float:
    r = subprocess.run([ffmpeg, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    return float(m.group(1)) * 3600 + float(m.group(2)) * 60 + float(m.group(3)) \
        if m else -1.0


def make_placeholder(path: Path, title: str, w: int, h: int) -> Path:
    """Branded gradient card so the pipeline never dead-ends on missing art."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w * 2, h * 2))
    d = ImageDraw.Draw(img)
    for x in range(0, w * 2, 8):
        t = x / (w * 2)
        r = int(124 + (34 - 124) * t)
        g = int(58 + (211 - 58) * t)
        b = int(237 + (238 - 237) * t)
        d.rectangle([x, 0, x + 8, h * 2], fill=(r, g, b))
    d.ellipse([w * 0.4, h * 0.35, w * 1.6, h * 1.65], fill=(15, 17, 21))
    img = img.resize((w, h), Image.LANCZOS)
    img.save(path)
    return path


def scene_image(sc: dict, images_dir: Path | None, w: int, h: int) -> Path:
    if sc.get("image"):
        p = Path(sc["image"])
        if p.exists():
            return p
    if images_dir:
        for name in (f"scene_{sc['index']:02d}.png", f"scene_{sc['index']:02d}.jpg",
                     f"scene_{sc['index']:02d}.jpeg"):
            p = images_dir / name
            if p.exists():
                return p
    return None  # caller makes a placeholder


def anim_dir(sc: dict, images_dir: Path | None) -> Path | None:
    """If the scene's slide has a typewriter frame sequence, return that dir.

    Animation is keyed by the SLIDE number (scene_03.png -> anim_scene_03),
    not the scene index, so we parse the image path to find the right one.
    """
    if not images_dir:
        return None
    # derive slide number from the scene's image path (images/scene_03.png)
    slide_num = None
    if sc.get("image"):
        m = re.search(r"scene_(\d+)", Path(sc["image"]).name)
        if m:
            slide_num = int(m.group(1))
    if slide_num is None:
        # fall back to scene index only if no explicit image
        slide_num = sc["index"]
    p = images_dir / f"anim_scene_{slide_num:02d}"
    if p.is_dir() and any(p.glob("frame_*.png")):
        return p
    return None


def render_scene(ffmpeg: str, img: Path, out: Path, sc: dict, w: int, h: int,
                 fps: int, font: str | None, frames_dir: Path | None = None) -> int:
    dur = float(sc.get("duration") or 3.0)
    frames = max(int(dur * fps), 2)
    text = sc.get("title") or sc.get("name")
    txt_file = None
    if text and font:
        txt_file = out.with_suffix(".txt")
        txt_file.write_text(text, encoding="utf-8")
    if frames_dir:
        # typewriter animation: stretch the frame sequence to the scene duration
        frs = sorted(frames_dir.glob("frame_*.png"))
        if not frs:
            print(f"scene {sc['index']}: anim dir empty", file=sys.stderr)
            return 1
        in_fps = max(10.0, min(30.0, len(frs) / max(dur, 0.5)))
        vf = [f"scale={w}:{h}", f"fps={fps}", "format=yuv420p"]
        cmd = [ffmpeg, "-y", "-framerate", f"{in_fps:.3f}",
               "-i", str(frames_dir / "frame_%03d.png"),
               "-vf", ",".join(vf), "-an", "-c:v", "libx264", "-preset",
               "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps),
               "-t", f"{dur:.3f}", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
    else:
        # zoompan needs a bigger input to zoom into
        vf = [f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase",
              f"crop={w * 2}:{h * 2}"]
        direction = "in" if sc["index"] % 2 == 1 else "out"
        if direction == "in":
            zoom = f"min(zoom+0.0006,1.12)"
        else:
            zoom = "if(eq(on,0),1.12,max(zoom-0.0006,1.0))"
        vf.append(f"zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={frames}:s={w}x{h}:fps={fps}")
        vf_str = ",".join(vf)
        if text and font:
            box = ",".join(str(x) for x in (w // 2, h - 120, w // 2, h - 170))
            vf_str += (f",drawtext=fontfile='{font}':textfile='{txt_file}':"
                       f"x=(w-text_w)/2:y=h-th-90:fontsize=58:fontcolor=white:"
                       f"box=1:boxcolor=black@0.5:boxborderw=24:"
                       f"alpha='if(lt(t,0.35),0,min(1,max(0,(t-0.35)/0.3)))':"
                       f"enable='between(t,0.35,{dur - 0.5})'")
        cmd = [ffmpeg, "-y", "-i", str(img),
               "-vf", vf_str, "-an", "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
    if txt_file:
        txt_file.unlink(missing_ok=True)
    if r.returncode != 0 or not out.exists():
        print(f"scene {sc['index']} render failed:\n{(r.stdout + r.stderr)[-400:]}",
              file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--out", default="video.mp4")
    ap.add_argument("--images-dir", default=None)
    ap.add_argument("--music", default=None)
    ap.add_argument("--xfade", type=float, default=None)
    ap.add_argument("--bgm-volume", type=float, default=0.18)
    ap.add_argument("--work", default=None, help="work dir (default: temp)")
    args = ap.parse_args()

    ffmpeg = ff()
    mpath = Path(args.manifest)
    if not mpath.exists():
        print(f"not found: {mpath}", file=sys.stderr)
        return 1
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    w, h = int(manifest["width"]), int(manifest["height"])
    fps = int(manifest["fps"])
    xfade = float(args.xfade if args.xfade is not None else manifest.get("xfade", 0.5))
    scenes = manifest["scenes"]
    if len(scenes) < 1:
        print("manifest has no scenes", file=sys.stderr)
        return 1
    if xfade < 0:
        xfade = 0.0

    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="vs_render_"))
    work.mkdir(parents=True, exist_ok=True)
    images_dir = Path(args.images_dir) if args.images_dir else None
    font = find_font()

    # 1) render scene clips (video only)
    clips: list[Path] = []
    for sc in scenes:
        img = scene_image(sc, images_dir, w, h)
        if img is None:
            img = make_placeholder(work / f"scene_{sc['index']:02d}.png",
                                   sc.get("visual", ""), w, h)
            print(f"scene {sc['index']}: no image found → placeholder card")
        out = work / f"clip_{sc['index']:02d}.mp4"
        fr_dir = anim_dir(sc, images_dir)
        if render_scene(ffmpeg, img, out, sc, w, h, fps, font,
                        frames_dir=fr_dir) != 0:
            return 1
        if fr_dir:
            print(f"scene {sc['index']}: typewriter animation ({fr_dir.name})")
        clips.append(out)

    # 2) video: chained crossfades (or concat demuxer when xfade == 0)
    if xfade > 0 and len(clips) > 1:
        chain, offset = "", 0.0
        for i in range(len(clips) - 1):
            # offset = cumulative duration so far - (i+1) * xfade
            offset += float(scenes[i].get("duration") or 3.0) - xfade
            if i == 0:
                seg = (f"[0:v][1:v]xfade=transition=fade:duration={xfade}:"
                       f"offset={offset:.3f}[v1]")
            else:
                seg = (f"[v{i}][{i + 1}:v]xfade=transition=fade:duration={xfade}:"
                       f"offset={offset:.3f}[v{i + 1}]")
            chain = (chain + ";" if chain else "") + seg
        final = f"v{len(clips) - 1}"
        vf = f"{chain},[{final}]format=yuv420p[vout]"
        cmd = [ffmpeg, "-y"]
        for c in clips:
            cmd += ["-i", str(c)]
        cmd += ["-filter_complex", vf, "-map", "[vout]", "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                "-r", str(fps), str(work / "video_only.mp4")]
        r = subprocess.run(cmd, capture_output=True, text=True)
    else:
        listfile = work / "list.txt"
        listfile.write_text("".join(f"file '{c.resolve()}'\n" for c in clips),
                            encoding="utf-8")
        cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
               "-c", "copy", str(work / "video_only.mp4")]
        r = subprocess.run(cmd, capture_output=True, text=True)
        total_v = sum(float(s.get("duration") or 3.0) for s in scenes)
    if r.returncode != 0 or not (work / "video_only.mp4").exists():
        print(f"video assembly failed:\n{(r.stdout + r.stderr)[-400:]}", file=sys.stderr)
        return 1
    total_v = sum(float(s.get("duration") or 3.0) for s in scenes) - xfade * (len(clips) - 1)

    # 3) audio: narration acrossfade chain + optional BGM, loudnorm
    audio_paths = [Path(s["audio"]) for s in scenes if s.get("audio")]
    if audio_paths:
        if xfade > 0 and len(audio_paths) > 1:
            chain = ""
            for i in range(len(audio_paths) - 1):
                if i == 0:
                    seg = f"[0:a][1:a]acrossfade=d={xfade}[a1]"
                else:
                    seg = f"[a{i}][{i + 1}:a]acrossfade=d={xfade}[a{i + 1}]"
                chain = (chain + ";" if chain else "") + seg
            an_label = f"a{len(audio_paths) - 1}"
            cmd = [ffmpeg, "-y"]
            for a in audio_paths:
                cmd += ["-i", str(a)]
            cmd += ["-filter_complex", chain, "-map",
                    f"[{an_label}]", "-c:a", "aac", str(work / "narration.m4a")]
            r = subprocess.run(cmd, capture_output=True, text=True)
        else:
            listfile = work / "audiolist.txt"
            listfile.write_text("".join(f"file '{a.resolve()}'\n" for a in audio_paths),
                                encoding="utf-8")
            cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
                   "-c:a", "aac", str(work / "narration.m4a")]
            r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"narration assembly failed:\n{(r.stdout + r.stderr)[-400:]}",
                  file=sys.stderr)
            return 1
    else:
        print("no narration audio in manifest — output will be silent",
              file=sys.stderr)

    out = Path(args.out)
    music = Path(args.music) if args.music else None
    if music and music.exists():
        cmd = [ffmpeg, "-y", "-i", str(work / "video_only.mp4")]
        if (work / "narration.m4a").exists():
            cmd += ["-i", str(work / "narration.m4a")]
        cmd += ["-stream_loop", "-1", "-i", str(music),
                "-filter_complex",
                "[1:a]volume=1.0[n];[2:a]volume=" + f"{args.bgm_volume},"
                "afade=t=in:st=0:d=1.5,afade=t=out:st={TOTAL}:d=2[bg];"
                "[n][bg]amix=inputs=2:duration=first:dropout_transition=0,"
                "loudnorm=I=-14:TP=-1:LRA=11,volume=0.6dB,"
                "alimiter=limit=0.95[aout]".replace("{TOTAL}",
                                                    f"{total_v - 2:.1f}"),
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", str(out)]
    elif (work / "narration.m4a").exists():
        cmd = [ffmpeg, "-y", "-i", str(work / "video_only.mp4"),
               "-i", str(work / "narration.m4a"),
               "-map", "0:v", "-map", "1:a",
               "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1:LRA=11",
               "-c:a", "aac", "-b:a", "192k",
               "-movflags", "+faststart", str(out)]
    else:
        cmd = [ffmpeg, "-y", "-i", str(work / "video_only.mp4"),
               "-c:v", "copy", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        print(f"final mux failed:\n{(r.stdout + r.stderr)[-400:]}", file=sys.stderr)
        return 1

    # decode sanity check
    dec = subprocess.run([ffmpeg, "-v", "error", "-i", str(out), "-f", "null", "-"],
                         capture_output=True, text=True)
    ok = dec.returncode == 0 and not dec.stderr.strip()
    dur = probe_dur(ffmpeg, out)
    print(f"wrote {out} — {int(dur // 60)}:{int(dur % 60):02d}, "
          f"{out.stat().st_size // 1024} KB, {len(scenes)} scenes, "
          f"{w}x{h}@{fps}, xfade {xfade}s, decode {'clean ✅' if ok else 'ERRORS ❌'}")
    if not ok:
        print(dec.stderr[-300:], file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
