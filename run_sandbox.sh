curl 'http://localhost:8080/run_code' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "code": "def add(a, b):\n    return a + b\n\ndef test_add():\n    assert add(1, 2) == 3\n    assert add(-1, 1) == 0",
    "language": "pytest"
  }'


curl 'http://localhost:8080/run_code' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "language": "pytest",
    "code": "def add(a, b):\n    if a > 0: return a + b\n    return b\n\ndef test_add():\n    assert add(1, 2) == 3",
    "args": ["--cov-branch", "--json-report", "--json-report-file=report.json"],
    "fetch_files": ["report.json"]
  }'