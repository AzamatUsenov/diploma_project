import subprocess
import sys
import json
import tempfile
import os
import time


TIMEOUT_SECONDS = 10
MAX_OUTPUT_LENGTH = 5000

HEADER = '''import json
import sys
import traceback
import io

_test_results = []
_stdout_backup = sys.stdout

def _run_test(name, func):
    sys.stdout = io.StringIO()
    try:
        func()
        _test_results.append({"name": name, "passed": True, "message": "OK"})
    except AssertionError as e:
        _test_results.append({"name": name, "passed": False, "message": str(e) or "Assertion failed"})
    except Exception as e:
        _test_results.append({"name": name, "passed": False, "message": f"{type(e).__name__}: {e}"})
    finally:
        sys.stdout = _stdout_backup

def _check(condition, msg="Assertion failed"):
    if not condition:
        raise AssertionError(msg)
'''

FOOTER = '''
sys.stdout = _stdout_backup
print(json.dumps({"results": _test_results, "all_passed": all(t["passed"] for t in _test_results)}))
'''


def execute_code(user_code: str, test_code: str) -> dict:
    full_code = HEADER + "\n# User code\n" + user_code + "\n\n# Tests\n" + test_code + "\n" + FOOTER

    tmp_file = None
    try:
        tmp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, encoding='utf-8'
        )
        tmp_file.write(full_code)
        tmp_file.close()

        start_time = time.time()
        result = subprocess.run(
            [sys.executable, '-u', tmp_file.name],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
        )
        execution_time_ms = int((time.time() - start_time) * 1000)

        if result.returncode != 0:
            stderr = result.stderr[:MAX_OUTPUT_LENGTH]
            clean_error = _clean_traceback(stderr)
            return {
                'status': 'error',
                'test_results': [],
                'tests_passed': 0,
                'tests_total': 0,
                'execution_time_ms': execution_time_ms,
                'output': result.stdout[:MAX_OUTPUT_LENGTH],
                'error_message': clean_error,
            }

        stdout = result.stdout.strip()
        try:
            last_line = stdout.split('\n')[-1]
            data = json.loads(last_line)
            test_results = data.get('results', [])
            tests_passed = sum(1 for t in test_results if t['passed'])
            tests_total = len(test_results)
            status = 'passed' if data.get('all_passed') else 'failed'
            return {
                'status': status,
                'test_results': test_results,
                'tests_passed': tests_passed,
                'tests_total': tests_total,
                'execution_time_ms': execution_time_ms,
                'output': '',
                'error_message': '',
            }
        except (json.JSONDecodeError, IndexError):
            return {
                'status': 'error',
                'test_results': [],
                'tests_passed': 0,
                'tests_total': 0,
                'execution_time_ms': execution_time_ms,
                'output': stdout[:MAX_OUTPUT_LENGTH],
                'error_message': 'Failed to parse test results',
            }

    except subprocess.TimeoutExpired:
        return {
            'status': 'timeout',
            'test_results': [],
            'tests_passed': 0,
            'tests_total': 0,
            'execution_time_ms': TIMEOUT_SECONDS * 1000,
            'output': '',
            'error_message': f'Execution timed out ({TIMEOUT_SECONDS}s limit)',
        }
    except Exception as e:
        return {
            'status': 'error',
            'test_results': [],
            'tests_passed': 0,
            'tests_total': 0,
            'execution_time_ms': 0,
            'output': '',
            'error_message': str(e),
        }
    finally:
        if tmp_file and os.path.exists(tmp_file.name):
            os.unlink(tmp_file.name)


def _clean_traceback(stderr: str) -> str:
    lines = stderr.strip().split('\n')
    cleaned = []
    skip_path = False
    for line in lines:
        if 'tmp' in line and '.py' in line:
            skip_path = True
            continue
        if skip_path and line.startswith('    '):
            cleaned.append(line)
            skip_path = False
        else:
            skip_path = False
            cleaned.append(line)
    return '\n'.join(cleaned[-10:])
