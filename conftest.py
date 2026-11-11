import os
import sys

# 让 pytest 在未安装包的情况下也能从 src 导入 mjson
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
