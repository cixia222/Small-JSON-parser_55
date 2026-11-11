"""性能对比：mjson 手写解析器 vs 标准库 json。

运行::

    python benchmark/bench.py
"""

import json
import time

from mjson import loads

SAMPLE = json.dumps({
    "name": "Small-JSON-parser",
    "version": "0.1.0",
    "tags": ["json", "parser", "educational"],
    "stats": {"stars": 42, "forks": 7},
    "nested": {"a": [1, 2, 3], "b": {"c": None, "d": True}},
})
SAMPLE = "[" + ",".join(SAMPLE for _ in range(200)) + "]"

N = 50


def timeit(fn, data):
    start = time.perf_counter()
    for _ in range(N):
        fn(data)
    return time.perf_counter() - start


def main():
    print(f"测试数据大小: {len(SAMPLE)} 字符, 重复 {N} 次")
    t_json = timeit(json.loads, SAMPLE)
    t_mjson = timeit(loads, SAMPLE)
    print(f"标准库 json.loads : {t_json:.4f} 秒")
    print(f"mjson.loads        : {t_mjson:.4f} 秒")
    print(f"mjson 慢约        : {t_mjson / t_json:.1f} 倍")
    print()
    print("说明：mjson 的定位是可读性/教学，而非性能，慢是预期的。")


if __name__ == "__main__":
    main()
