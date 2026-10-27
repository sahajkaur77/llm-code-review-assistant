SEEDS = [
    {
        "id": "sql_injection",
        "code": '''def __FN__(__VAR__):
    query = "SELECT * FROM users WHERE id = " + __VAR__
    return execute_query(query)''',
        "issues": [{
            "title": "Potential SQL injection",
            "category": "security",
            "severity": "High",
            "line": 2,
            "problem": "User-controlled input is concatenated into an SQL query.",
            "why_it_matters": "An attacker may manipulate the query to read or modify data.",
            "suggested_fix": "Use a parameterized query supported by your database driver.",
        }],
        "fixed_code": '''def __FN__(__VAR__):
    query = "SELECT * FROM users WHERE id = ?"
    return execute_query(query, (__VAR__,))''',
    },
    {
        "id": "hardcoded_password",
        "code": '''def __FN__():
    password = "admin123"
    return connect(host="localhost", user="admin", password=password)''',
        "issues": [{
            "title": "Hardcoded credentials",
            "category": "security",
            "severity": "High",
            "line": 2,
            "problem": "A password is written directly in the source code.",
            "why_it_matters": "Anyone with access to the repository can see the secret, and rotating it requires a code change.",
            "suggested_fix": "Load the password from an environment variable or a secrets manager.",
        }],
        "fixed_code": '''import os

def __FN__():
    password = os.environ["DB_PASSWORD"]
    return connect(host="localhost", user="admin", password=password)''',
    },
    {
        "id": "mutable_default",
        "code": '''def __FN__(item, items=[]):
    items.append(item)
    return items''',
        "issues": [{
            "title": "Mutable default argument",
            "category": "bug",
            "severity": "Medium",
            "line": 1,
            "problem": "The default list is created once and shared across all calls.",
            "why_it_matters": "Data leaks between calls, causing surprising results that are hard to debug.",
            "suggested_fix": "Default to None and create a new list inside the function.",
        }],
        "fixed_code": '''def __FN__(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items''',
    },
    {
        "id": "bare_except_open",
        "code": '''def __FN__(path):
    try:
        return open(path).read()
    except:
        return None''',
        "issues": [
            {
                "title": "Bare except clause",
                "category": "bug",
                "severity": "Medium",
                "line": 4,
                "problem": "A bare except catches every exception, including KeyboardInterrupt, and hides the real error.",
                "why_it_matters": "Failures are silently swallowed, which makes debugging difficult.",
                "suggested_fix": "Catch the specific exception you expect, such as OSError.",
            },
            {
                "title": "File not closed explicitly",
                "category": "quality",
                "severity": "Low",
                "line": 3,
                "problem": "The file is opened without a context manager.",
                "why_it_matters": "The file handle may stay open longer than needed.",
                "suggested_fix": "Use a with statement.",
            },
        ],
        "fixed_code": '''def __FN__(path):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return None''',
    },
    {
        "id": "clean_add",
        "code": '''def __FN__(a, b):
    return a + b''',
        "issues": [],
        "fixed_code": '''def __FN__(a, b):
    return a + b''',
    },
]