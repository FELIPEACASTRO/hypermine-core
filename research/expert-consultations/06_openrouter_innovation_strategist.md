ERRO OpenRouter: HTTP 400: {"error":{"message":"google/gemini-2.5-flash-preview is not a valid model ID","code":400},"user_id":"user_33RTiSpX3sAeGxtWShMxD7Fsb8L"}
Traceback (most recent call last):
  File "/home/ubuntu/expert_consultation_v2.py", line 309, in call_openrouter
    raise Exception(f"HTTP {resp.status_code}: {resp.text[:500]}")
Exception: HTTP 400: {"error":{"message":"google/gemini-2.5-flash-preview is not a valid model ID","code":400},"user_id":"user_33RTiSpX3sAeGxtWShMxD7Fsb8L"}
