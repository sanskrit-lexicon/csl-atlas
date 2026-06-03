"""One-time setup for the F6 DE->EN gloss test: install argos-translate + the
offline German->English model. Run once; thereafter translation is fully offline.

  python scripts/forensic/_setup_argos.py
"""
import subprocess
import sys


def main():
    subprocess.run([sys.executable, "-m", "pip", "install", "argostranslate"], check=True)
    import argostranslate.package as pkg
    import argostranslate.translate as tr
    pkg.update_package_index()
    avail = pkg.get_available_packages()
    de_en = next(p for p in avail if p.from_code == "de" and p.to_code == "en")
    pkg.install_from_path(de_en.download())
    print("DE->EN model installed.")
    print("sanity:", tr.translate("Sohn eines Königs; eine Art Pflanze", "de", "en"))


if __name__ == "__main__":
    main()
