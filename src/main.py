
import os

from textnode import TextNode, TextType


### SCRAPS from /tmp/ (to test)
import os
import shutil

def list_contents_r(filepath: str | os.PathLike[str]) -> None:
    filepath_str = str(filepath)
    print("=================================")
    print(f"now in: {filepath_str}")
    for file in os.listdir(filepath):
        filename: str = os.fsdecode(file)
        print(f"{filepath_str}/{filename}")
        full_path = os.path.join(filepath_str, filename)
        if not os.path.isfile(full_path):
            # get one layer deeper for next path
            list_contents_r(full_path)
    print("=================================")


def main():
    public_dir_str = "public"
    # 1. Wipe public dir
    dir = os.fsencode(public_dir_str)
    shutil.rmtree(dir)
    # 2. Recreate public dir
    os.mkdir(dir)
    # 3. Recursively copy contents from static/ to public/
    # list contents of static recursively?
    static_dir_str = "static"
    static_dir = os.fsencode(static_dir_str)
    abs_path = os.path.abspath(".")
    print(f"abs path here is: {os.path.abspath(".")}")
    static_dir = os.path.normpath(os.path.join(abs_path, static_dir_str))
    list_contents_r(static_dir)


if __name__ == "__main__":
    main()
# =============================================================================






def copier():
    # Delete contents of public dir
    dir = os.fsencode("public/")
    for file in os.listdir(dir):


def main():
    print("hello world")
    text_node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(text_node)

if __name__ == "__main__":
    main()

