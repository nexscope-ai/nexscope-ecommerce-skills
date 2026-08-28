import json, sys, os, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api_client_base import GATEWAY_BASE_URL, GATEWAY_API_KEY, CURRENT_YEAR
import requests

query = "best coffee canister for fresh beans " + CURRENT_YEAR
system_prompt = "You are a helpful shopping assistant. Recommend specific products with prices and where to buy."

url = GATEWAY_BASE_URL + "/chat/completions"
headers = {"Authorization": "Bearer " + GATEWAY_API_KEY, "Content-Type": "application/json"}
payload = {
    "model": "global.anthropic.claude-sonnet-4-6",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ],
    "tools": [{"type": "web_search"}],
    "temperature": 0.7,
    "max_tokens": 4096
}

print("Calling API with web_search tool...")
resp = requests.post(url, headers=headers, json=payload, timeout=120)
print("Status:", resp.status_code)
data = resp.json()

with open("/tmp/raw_response_claude.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Top-level keys:", list(data.keys()))
if "choices" in data:
    msg = data["choices"][0].get("message", {})
    print("Message keys:", list(msg.keys()))
    if "annotations" in msg:
        anns = msg["annotations"]
        print("Annotations count:", len(anns))
        for a in anns[:3]:
            print("  ", json.dumps(a, ensure_ascii=False)[:200])
    if "tool_calls" in msg:
        tcs = msg["tool_calls"]
        print("Tool calls count:", len(tcs))
        for tc in tcs[:2]:
            print("  ", json.dumps(tc, ensure_ascii=False)[:300])
    content = msg.get("content", "")
    if isinstance(content, list):
        print("Content is LIST, blocks:", len(content))
        for i, block in enumerate(content[:10]):
            if isinstance(block, dict):
                btype = block.get("type", "unknown")
                print(f"  [{i}] type={btype} keys={list(block.keys())}")
                if "url" in str(block.get("type","")) or "search" in str(block.get("type","")) or "citation" in str(block.get("type","")):
                    print("      ", json.dumps(block, ensure_ascii=False)[:500])
            elif isinstance(block, str):
                print(f"  [{i}] text len={len(block)}")
    elif isinstance(content, str):
        print("Content is string, length=", len(content))
        urls = re.findall(r"https?://[^\s\)]+", content)
        print("URLs in text:", len(urls))
        for u in urls[:5]:
            print(" ", u)
    if "citations" in msg:
        print("msg.citations:", json.dumps(msg["citations"], ensure_ascii=False)[:500])

print("Full response saved to /tmp/raw_response_claude.json")
