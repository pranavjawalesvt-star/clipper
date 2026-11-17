import json, os, subprocess, sys
from groq import Groq

video, out_json = sys.argv[1], sys.argv[2]

# 1. Extract audio, small enough for the free upload limit
subprocess.run(["ffmpeg", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000",
                "-b:a", "32k", "work/audio.mp3"], check=True)

client = Groq(api_key=os.environ["GROQ_API_KEY"])

# 2. Transcribe with word timestamps
with open("work/audio.mp3", "rb") as f:
    tr = client.audio.transcriptions.create(
        file=("audio.mp3", f.read()),
        model="whisper-large-v3-turbo",
        response_format="verbose_json",
        timestamp_granularities=["segment"],
    )
segments = [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in tr.segments]
transcript = "\n".join(f'[{s["start"]:.1f}-{s["end"]:.1f}] {s["text"]}' for s in segments)

# 3. Ask the LLM for the best clips
prompt = f"""From this timestamped transcript, pick the 5 most engaging 20-60 second clips.
Return ONLY JSON in this shape:
{{"clips": [{{"start": 12.3, "end": 45.0, "score": 8, "reason": "short why"}}]}}
Use timestamps from the transcript. No text outside the JSON.

Transcript:
{transcript[:20000]}"""

resp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},
)
clips = json.loads(resp.choices[0].message.content)["clips"]

with open(out_json, "w") as f:
    json.dump(clips, f, indent=2)
print(f"Found {len(clips)} clips")
