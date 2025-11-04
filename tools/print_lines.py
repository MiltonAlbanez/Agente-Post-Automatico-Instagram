import sys
from pathlib import Path

path = Path(sys.argv[1])
start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
end = int(sys.argv[3]) if len(sys.argv) > 3 else start + 100

for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
    if start <= i <= end:
        print(f"{i:04d}: {line}")