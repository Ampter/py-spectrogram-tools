import re
import os
from pathlib import Path

def bump_version(version_str):
    major, minor, patch = map(int, version_str.split('.'))
    if patch < 9:
        patch += 1
    elif minor < 1:
        minor += 1
        patch = 0
    else:
        major += 1
        minor = 0
        patch = 0
    return f"{major}.{minor}.{patch}"

def main():
    init_file = Path("pyspectools2/__init__.py")
    content = init_file.read_text(encoding="utf-8")

    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find __version__ in pyspectools2/__init__.py")

    current_version = match.group(1)
    new_version = bump_version(current_version)

    new_content = re.sub(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
        content
    )

    init_file.write_text(new_content, encoding="utf-8")
    print(f"Bumped version from {current_version} to {new_version}")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"new_version={new_version}\n")

if __name__ == "__main__":
    main()
