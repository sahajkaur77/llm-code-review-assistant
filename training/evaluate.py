import argparse
import json
import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen2.5-Coder-1.5B-Instruct"


def extract_json(text):
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", default="data/processed/test.jsonl")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--out", default="data/processed/eval_base.json")
    args = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(
        BASE, torch_dtype=torch.float16, device_map="auto"
    )
    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()

    with open(args.test, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f][: args.limit]

    valid = tp = fp = fn = clean_total = clean_fp = 0
    results = []

    for r in rows:
        system, user, assistant = r["messages"]
        expected = json.loads(assistant["content"])["issues"]
        exp_lines = {str(i["line"]) for i in expected}

        prompt = tok.apply_chat_template(
            [system, user], tokenize=False, add_generation_prompt=True
        )
        inputs = tok(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=512, do_sample=False)
        text = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

        parsed = extract_json(text)
        pred_lines = set()
        is_valid = isinstance(parsed, dict) and isinstance(parsed.get("issues"), list)
        if is_valid:
            valid += 1
            pred_lines = {
                str(i.get("line")) for i in parsed["issues"] if isinstance(i, dict)
            }

        tp += len(pred_lines & exp_lines)
        fp += len(pred_lines - exp_lines)
        fn += len(exp_lines - pred_lines)
        if not expected:
            clean_total += 1
            if pred_lines:
                clean_fp += 1

        results.append({"code": user["content"], "expected": expected, "output": text})

    n = len(rows)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    print(f"\nExamples evaluated:      {n}")
    print(f"Valid JSON structure:    {valid}/{n} ({valid / n:.0%})")
    print(f"Issue precision (line):  {precision:.2f}")
    print(f"Issue recall (line):     {recall:.2f}")
    print(f"False alarms on clean:   {clean_fp}/{clean_total}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Raw outputs saved to {args.out}")


if __name__ == "__main__":
    main()