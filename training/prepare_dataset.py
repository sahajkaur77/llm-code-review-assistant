import json
import random
from pathlib import Path

from seed_examples import SEEDS

random.seed(42)

FN_NAMES = ["get_user", "fetch_record", "load_account", "find_customer", "process_item", "read_data"]
VAR_NAMES = ["user_id", "uid", "account_id", "customer_id", "item_id", "record_id"]
VARIANTS_PER_SEED = 30
TEST_FRACTION = 0.2

SYSTEM_PROMPT = (
    "You are a code review assistant. Review the Python code and reply with JSON only, "
    'in the form {"issues": [...], "fixed_code": "..."}. Each issue has: title, category, '
    "severity (Critical, High, Medium, or Low), line, problem, why_it_matters, suggested_fix. "
    "If the code has no issues, return an empty issues list."
)

def fill(text, fn, var):
    return text.replace("__FN__", fn).replace("__VAR__", var)

def build_record(seed, fn, var):
    code = fill(seed["code"], fn, var)
    answer = {"issues": seed["issues"], "fixed_code": fill(seed["fixed_code"], fn, var)}
    return {
        "seed_id": seed["id"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": code},
            {"role": "assistant", "content": json.dumps(answer, indent=2)},
        ],
    }

def main():
    seeds = SEEDS[:]
    random.shuffle(seeds)
    n_test = max(1, int(len(seeds) * TEST_FRACTION))
    test_seeds, train_seeds = seeds[:n_test], seeds[n_test:]

    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, group in [("train", train_seeds), ("test", test_seeds)]:
        seen, rows = set(), []
        for seed in group:
            for _ in range(VARIANTS_PER_SEED):
                rec = build_record(seed, random.choice(FN_NAMES), random.choice(VAR_NAMES))
                key = rec["messages"][1]["content"]
                if key not in seen:
                    seen.add(key)
                    rows.append(rec)
        random.shuffle(rows)
        with open(out_dir / f"{name}.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"{name}: {len(rows)} examples from {len(group)} seeds")

if __name__ == "__main__":
    main()