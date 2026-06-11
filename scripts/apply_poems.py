"""Fix 红楼梦 poem titles and regenerate frontend bundles."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POETRY_DIR = os.path.join(ROOT, "data", "poetry")


def fix_hongloumeng_titles():
    changed = 0
    for fn in os.listdir(POETRY_DIR):
        if not fn.endswith(".json"):
            continue
        fp = os.path.join(POETRY_DIR, fn)
        data = json.loads(open(fp, encoding="utf-8").read())
        file_changed = False
        for e in data.get("entries", []):
            author = e.get("author", "")
            source = e.get("source", "")
            title = e.get("title", "")
            # 曹雪芹作品，或来源标注红楼梦
            if author == "曹雪芹" or "红楼梦" in source or "红楼梦" in title:
                if title != "红楼梦":
                    e["title"] = "红楼梦"
                    file_changed = True
                    changed += 1
        if file_changed:
            json.dump(data, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return changed


def main():
    n = fix_hongloumeng_titles()
    print(f"Fixed {n} entries -> title 红楼梦")

    for script in ("gen_browse_data.py", "gen_palette.py"):
        path = os.path.join(ROOT, "scripts", script)
        print(f"Running {script}...")
        subprocess.run([sys.executable, path], cwd=os.path.join(ROOT, "scripts"), check=True)

    print("Done.")


if __name__ == "__main__":
    main()
