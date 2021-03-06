import os
import shutil
import zipfile

version = "v1.2"

output_dir = "Morrowind Dialog Explorer %s" % version

print("Starting...")

os.mkdir(output_dir)

shutil.copytree("../src", os.path.join(output_dir, "src"), ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))
shutil.copytree("../Morrowind Dialog Explorer.app", os.path.join(output_dir, "Morrowind Dialog Explorer.app"))
shutil.copyfile("../Morrowind Dialog Explorer.bat", os.path.join(output_dir, "Morrowind Dialog Explorer.bat"))
shutil.copyfile("../config.ini", os.path.join(output_dir, "config.ini"))
shutil.copyfile("../LICENSE", os.path.join(output_dir, "LICENSE"))
shutil.copyfile("../readme.md", os.path.join(output_dir, "readme.md"))

print("Compressing...")

with zipfile.ZipFile(output_dir + ".zip", "w", zipfile.ZIP_DEFLATED) as zfile:
    for root, dirs, file_names in os.walk(output_dir):
        for file_name in file_names:
            zfile.write(os.path.join(root, file_name))

print("Done.")
