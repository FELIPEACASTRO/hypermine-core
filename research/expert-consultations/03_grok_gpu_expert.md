ERRO Grok: HTTP 403: {"code":"The caller does not have permission to execute the specified operation","error":"Your newly created team doesn't have any credits or licenses yet. You can purchase those on https://console.x.ai/team/f6648191-e37f-4d0f-9d50-569b11cb33f8."}
Traceback (most recent call last):
  File "/home/ubuntu/expert_consultation_v2.py", line 152, in call_grok
    raise Exception(f"HTTP {resp.status_code}: {resp.text[:500]}")
Exception: HTTP 403: {"code":"The caller does not have permission to execute the specified operation","error":"Your newly created team doesn't have any credits or licenses yet. You can purchase those on https://console.x.ai/team/f6648191-e37f-4d0f-9d50-569b11cb33f8."}
