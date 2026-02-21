ERRO Anthropic: HTTP 400: {"type":"error","error":{"type":"invalid_request_error","message":"Your credit balance is too low to access the Anthropic API. Please go to Plans & Billing to upgrade or purchase credits."},"request_id":"req_011CYMu62XNvP8NQ6k83AyJS"}
Traceback (most recent call last):
  File "/home/ubuntu/expert_consultation_v2.py", line 201, in call_anthropic
    raise Exception(f"HTTP {resp.status_code}: {resp.text[:500]}")
Exception: HTTP 400: {"type":"error","error":{"type":"invalid_request_error","message":"Your credit balance is too low to access the Anthropic API. Please go to Plans & Billing to upgrade or purchase credits."},"request_id":"req_011CYMu62XNvP8NQ6k83AyJS"}
