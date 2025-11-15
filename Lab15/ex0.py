import importlib

def check_package(name):
    try:
        mod = importlib.import_module(name)
        ver = getattr(mod, "__version__", "unknown")
        print(f"{name}: installed (version {ver})")
    except Exception:
        print(f"{name}: NOT installed")

if __name__ == "__main__":
    for pkg in ("scipy", "statsmodels", "matplotlib"):
        check_package(pkg)
# ...existing code...