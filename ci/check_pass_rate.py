"""Fail the build if the pass rate in a JUnit XML file is below a threshold.

Usage: python ci/check_pass_rate.py reports/junit.xml 95
"""
import sys
import xml.etree.ElementTree as ET


def main(path: str, threshold: float) -> int:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else root.iter("testsuite")

    total = failed = skipped = 0
    for s in suites:
        total += int(s.get("tests", 0))
        failed += int(s.get("failures", 0)) + int(s.get("errors", 0))
        skipped += int(s.get("skipped", 0))

    executed = total - skipped
    if executed == 0:
        print("No tests were executed - failing the gate.")
        return 1

    rate = (executed - failed) / executed * 100
    print(f"Executed={executed} Failed={failed} Skipped={skipped} PassRate={rate:.2f}% (required >= {threshold}%)")
    return 0 if rate >= threshold else 1


if __name__ == "__main__":
    xml_path = sys.argv[1] if len(sys.argv) > 1 else "reports/junit.xml"
    min_rate = float(sys.argv[2]) if len(sys.argv) > 2 else 95
    try:
        sys.exit(main(xml_path, min_rate))
    except (FileNotFoundError, ET.ParseError) as e:
        print(f"Could not read results: {e}")
        sys.exit(1)
