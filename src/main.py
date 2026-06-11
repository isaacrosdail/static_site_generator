import os
import shutil
from pathlib import Path

from block_markdown import markdown_to_html_node, extract_title


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    # from_path md file:
    md_contents = ""
    with open(from_path) as f:
        md_contents = f.read()
    template_contents = ""
    with open(template_path) as f:
        template_contents = f.read()

    # Convert md_contents to an HTML string
    md_as_html = markdown_to_html_node(md_contents).to_html()
    # Use extract title to grab the title for page
    page_title = extract_title(md_contents)
    # Replace the {{ Title }} and {{ Content }} placeholders in the template with the HTML + title
    replaced_template = template_contents.replace("{{ Title }}", page_title).replace("{{ Content }}", md_as_html)

    # Write the new full HTML page to a file at dest_path
    dest_dir_path = os.path.dirname(dest_path)
    os.makedirs(dest_dir_path, exist_ok=True)
    with open(dest_path, 'w') as f:
        f.write(replaced_template)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    # Crawl every entry in content directory
    # Recursive case? go thru dirs
    for name in os.listdir(dir_path_content):
        dir_path_content_child = os.path.join(dir_path_content, name)
        dest_dir_path_child = os.path.join(dest_dir_path, name)
        # Recursive case:
        if os.path.isdir(dir_path_content_child):
            generate_pages_recursive(dir_path_content_child, template_path, dest_dir_path_child)
        # For each md file found, generate a new html file using the same template.html
        # Base case? "stop" and call generate_page instead of generate_page_r?
        if os.path.isfile(dir_path_content_child):
            final_dest_path = Path(dest_dir_path_child).with_suffix(".html")
            generate_page(dir_path_content_child, template_path, final_dest_path)


def rebuild_public():
    # Delete contents of public dir & recreate fresh
    shutil.rmtree("public", ignore_errors=True) # so first run doesn't crash
    os.mkdir("public")

def copy_r(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
    for name in os.listdir(src):
        src_child = os.path.join(src, name)
        dst_child = os.path.join(dst, name)
        # For dir -> ensure we mirror in dst, then recurse
        # Recursive case
        if os.path.isdir(src_child):
            os.mkdir(dst_child)
            copy_r(src_child, dst_child)
        # For file -> copy
        # Base case
        if os.path.isfile(src_child):
            shutil.copy(src_child, dst_child)



def main():

    # Rebuild public dir from scratch
    rebuild_public()
    # Recursively copy contents of static -> public
    copy_r("static", "public")

    # Generate a page from content/index.md using template.html and write it to public/index.html
    #####generate_page("content/index.md", "template.html", "public/index.html")
    # Generate ALL our pages from our .md files:
    generate_pages_recursive("content", "template.html", "public")


if __name__ == "__main__":
    main()

