import json, os, subprocess, sys

video, clips_json, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out_dir, exist_ok=True)

with open(clips_json) as f:
    clips = json.load(f)

for i, c in enumerate(clips, 1):
    out = f"{out_dir}/clip_{i:02d}_score{c['score']}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(c["start"]), "-i", video,
        "-t", str(c["end"] - c["start"]),
        # Crop the centre to 9:16 and scale to 720x1280
        "-vf", "crop=ih*9/16:ih,scale=720:1280",
        "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac",
        out,
    ], check=True)
    print("Wrote", out, "-", c["reason"])
