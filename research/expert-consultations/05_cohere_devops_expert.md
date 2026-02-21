ERRO Cohere: HTTP 401: {"id":"9dbba636-b22e-44ac-a8b9-a063852bf26f","message":"invalid api token"}
Traceback (most recent call last):
  File "/home/ubuntu/expert_consultation_v2.py", line 247, in call_cohere
    raise Exception(f"HTTP {resp.status_code}: {resp.text[:500]}")
Exception: HTTP 401: {"id":"9dbba636-b22e-44ac-a8b9-a063852bf26f","message":"invalid api token"}
