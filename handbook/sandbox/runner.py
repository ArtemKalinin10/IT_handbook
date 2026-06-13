import json
import sys
import subprocess
import threading
import time
import psutil


def run_test(code, test, time_limit, mem_limit):
    start = time.perf_counter()

    proc = subprocess.Popen(
        ["python", "-c", code],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    peak_memory = 0

    def monitor_memory():
        nonlocal peak_memory
        try:
            p = psutil.Process(proc.pid)
            while proc.poll() is None:
                try:
                    mem = p.memory_info().rss
                    if mem > peak_memory:
                        peak_memory = mem
                except psutil.NoSuchProcess:
                    break
                time.sleep(0.05)
        except Exception:
            pass

    monitor = threading.Thread(target=monitor_memory, daemon=True)
    monitor.start()

    try:
        out, err = proc.communicate(
            input=test["input_data"],
            timeout=time_limit
        )
        elapsed = time.perf_counter() - start
        monitor.join(timeout=0.2)

        if peak_memory > mem_limit:
            status = "MLE"
        elif out.strip() != test["expected_output"].strip():
            status = "WA"
        else:
            status = "OK"

        return {
            "test_id": test["id"],
            "status": status,
            "time": round(elapsed, 4),
            "memory": peak_memory,
            "stdin": test["input_data"].strip(),
            "stdout": out.strip(),
            "stderr": err.strip()
        }

    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        monitor.join(timeout=0.2)
        return {
            "test_id": test["id"],
            "status": "TLE",
            "time": time_limit,
            "memory": peak_memory
        }

    except Exception as e:
        proc.kill()
        return {
            "test_id": test["id"],
            "status": "ERROR",
            "error": str(e),
            "time": 0,
            "memory": 0
        }


def main():
    payload = json.loads(sys.stdin.readline())

    code = payload["code"]
    tests = payload["tests"]
    time_limit = payload.get("time_limit_code", 2)
    mem_limit = payload.get("mem_limit_code", 256) * 1024 * 1024

    results = []

    try:
        for test in tests:
            results.append(run_test(code, test, time_limit, mem_limit))

        all_passed = all(r["status"] == "OK" for r in results)
        print(json.dumps({
            "status": "OK" if all_passed else "FAILED",
            "tests": results
        }))

    except Exception as e:
        print(json.dumps({
            "status": "ERROR",
            "error": str(e)
        }))


if __name__ == "__main__":
    main()
