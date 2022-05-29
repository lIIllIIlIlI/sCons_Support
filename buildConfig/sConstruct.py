from pathlib import Path

sourceList = [str(Path.cwd() / "src" / "marks" / "marks.c")]

VariantDir("../build", "../src", duplicate = 1)

Program("../build/marks.exe", sourceList)