SEEDS_2 = [
    {
        "id": "eval_input",
        "code": '''def __FN__(expression):
    result = eval(expression)
    return result''',
        "issues": [{
            "title": "Use of eval on untrusted input",
            "category": "security",
            "severity": "Critical",
            "line": 2,
            "problem": "eval executes arbitrary Python code contained in the input string.",
            "why_it_matters": "An attacker can run any code on your server, leading to full compromise.",
            "suggested_fix": "Use ast.literal_eval for literals, or parse the expression with a safe parser.",
        }],
        "fixed_code": '''import ast

def __FN__(expression):
    return ast.literal_eval(expression)''',
    },
    {
        "id": "shell_true",
        "code": '''import subprocess

def __FN__(path):
    subprocess.run("ls " + path, shell=True)''',
        "issues": [{
            "title": "Command injection via shell=True",
            "category": "security",
            "severity": "High",
            "line": 4,
            "problem": "User-controlled input is concatenated into a shell command.",
            "why_it_matters": "Input such as '; rm -rf /' could execute extra commands.",
            "suggested_fix": "Pass arguments as a list and avoid shell=True.",
        }],
        "fixed_code": '''import subprocess

def __FN__(path):
    subprocess.run(["ls", path], check=True)''',
    },
    {
        "id": "pickle_loads",
        "code": '''import pickle

def __FN__(data):
    return pickle.loads(data)''',
        "issues": [{
            "title": "Unsafe deserialization with pickle",
            "category": "security",
            "severity": "High",
            "line": 4,
            "problem": "pickle.loads can execute arbitrary code while loading crafted data.",
            "why_it_matters": "If the data comes from an untrusted source, an attacker can take control of the process.",
            "suggested_fix": "Use a safe format such as JSON for untrusted data.",
        }],
        "fixed_code": '''import json

def __FN__(data):
    return json.loads(data)''',
    },
    {
        "id": "yaml_load",
        "code": '''import yaml

def __FN__(text):
    return yaml.load(text)''',
        "issues": [{
            "title": "Unsafe yaml.load",
            "category": "security",
            "severity": "High",
            "line": 4,
            "problem": "yaml.load without a safe loader can construct arbitrary Python objects.",
            "why_it_matters": "Malicious YAML can trigger code execution.",
            "suggested_fix": "Use yaml.safe_load.",
        }],
        "fixed_code": '''import yaml

def __FN__(text):
    return yaml.safe_load(text)''',
    },
    {
        "id": "weak_hash",
        "code": '''import hashlib

def __FN__(password):
    return hashlib.md5(password.encode()).hexdigest()''',
        "issues": [{
            "title": "Weak hashing algorithm for passwords",
            "category": "security",
            "severity": "High",
            "line": 4,
            "problem": "MD5 is fast and unsalted here, so passwords can be cracked quickly.",
            "why_it_matters": "If the hashes leak, many passwords can be recovered in short order.",
            "suggested_fix": "Use a salted, slow password hash such as bcrypt, argon2, or PBKDF2.",
        }],
        "fixed_code": '''import hashlib
import os

def __FN__(password):
    salt = os.urandom(16)
    return salt + hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)''',
    },
    {
        "id": "eq_none",
        "code": '''def __FN__(value):
    if value == None:
        return "missing"
    return value''',
        "issues": [{
            "title": "Comparison to None with ==",
            "category": "quality",
            "severity": "Low",
            "line": 2,
            "problem": "None should be compared by identity, not equality.",
            "why_it_matters": "Objects can override ==, which may give unexpected results.",
            "suggested_fix": "Use 'is None'.",
        }],
        "fixed_code": '''def __FN__(value):
    if value is None:
        return "missing"
    return value''',
    },
    {
        "id": "off_by_one",
        "code": '''def __FN__(items):
    total = 0
    for i in range(1, len(items)):
        total += items[i]
    return total''',
        "issues": [{
            "title": "Loop skips the first element",
            "category": "bug",
            "severity": "Medium",
            "line": 3,
            "problem": "range(1, len(items)) starts at index 1, so items[0] is never added.",
            "why_it_matters": "The result is silently wrong for every input.",
            "suggested_fix": "Iterate over the items directly or use sum().",
        }],
        "fixed_code": '''def __FN__(items):
    return sum(items)''',
    },
    {
        "id": "div_zero",
        "code": '''def __FN__(values):
    return sum(values) / len(values)''',
        "issues": [{
            "title": "Division by zero on empty input",
            "category": "bug",
            "severity": "Medium",
            "line": 2,
            "problem": "An empty list makes len(values) zero and raises ZeroDivisionError.",
            "why_it_matters": "A single empty input can crash the caller.",
            "suggested_fix": "Handle the empty case explicitly.",
        }],
        "fixed_code": '''def __FN__(values):
    if not values:
        return 0.0
    return sum(values) / len(values)''',
    },
    {
        "id": "unused_code",
        "code": '''import os

def __FN__(name):
    greeting = "Hello, " + name
    unused = 42
    return greeting''',
        "issues": [
            {
                "title": "Unused import",
                "category": "quality",
                "severity": "Low",
                "line": 1,
                "problem": "The os module is imported but never used.",
                "why_it_matters": "Dead imports add clutter and can slow startup slightly.",
                "suggested_fix": "Remove the import.",
            },
            {
                "title": "Unused variable",
                "category": "quality",
                "severity": "Low",
                "line": 5,
                "problem": "The variable 'unused' is assigned but never read.",
                "why_it_matters": "It suggests leftover or incomplete code and confuses readers.",
                "suggested_fix": "Remove the assignment.",
            },
        ],
        "fixed_code": '''def __FN__(name):
    greeting = "Hello, " + name
    return greeting''',
    },
    {
        "id": "clean_strip",
        "code": '''def __FN__(items):
    return [item.strip() for item in items if item]''',
        "issues": [],
        "fixed_code": '''def __FN__(items):
    return [item.strip() for item in items if item]''',
    },
]