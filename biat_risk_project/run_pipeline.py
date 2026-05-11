"""
Pipeline runner: executes all 5 data pipeline scripts in order.
Run this once to generate all outputs before starting the app.
"""
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

scripts = [
    "src/1_data_preparation.py",
    "src/2_feature_engineering.py",
    "src/3_train_models.py",
    "src/4_scoring.py",
    "src/5_build_evolution.py",
]

if __name__ == "__main__":
    for script in scripts:
        path = os.path.join(ROOT, script)
        print(f"\n{'='*60}")
        print(f"  Running: {script}")
        print(f"{'='*60}")
        result = subprocess.run(
            [sys.executable, path],
            cwd=ROOT,
        )
        if result.returncode != 0:
            print(f"  ❌ FAILED: {script}")
            sys.exit(1)
        print(f"  ✅ Done: {script}")
    print(f"\n{'='*60}")
    print("  🎉 Pipeline complet. Lancez: streamlit run app/Home.py")
    print(f"{'='*60}")
