import threading
import asyncio
import httpx
import json
import subprocess


def speak(text):

    def _run():
        asyncio.run(_speak_async(text))

    threading.Thread(target=_run, daemon=True).start()


async def _speak_async(text):
    url = "http://localhost:50021"
    async with httpx.AsyncClient() as client:
        query_res = await client.post(f"{url}/audio_query",
                                      params={
                                          "text": text,
                                          "speaker": 3
                                      })
        synth_res = await client.post(f"{url}/synthesis",
                                      params={"speaker": 3},
                                      content=json.dumps(query_res.json()))
        with open("test.wav", "wb") as f:
            f.write(synth_res.content)
        subprocess.Popen(["aplay", "test.wav"])
