

# Architecture:
1. /content  - .md files, with a template.html file in the root of the project
2. src/      - Python code, reads md files and the template file
3. Generator converts the md files to a final HTML file for each page & writes them to the /public dir
4. Start the built-in Python HTTP server to serve content of /public dir locally

(refer back to CH1;L7 if we need to see this again)
# How the SSG works:
1. deletes /public's contents
2. Copy any static assets (html template, images, CSS, etc) to /public fresh
3. Generate an HTML file for each md file in /content dir:
    1. Open + read contents
    2. Split the markdown into "blocks" (eg paragraphs, headings, lists, etc)
    3. Convert each block into a tree of HTMLNode objs. For inline elements (like bold, links, etc) we
          will convert:
          - Raw md -> TextNode -> HTMLNode
    4. Join all HTMLNode blocks under one large parent HTMLNode for the pages.
    5. Use a recursive to_html() method to convert the HTMLNode and all its nested nodes to a giant HTML string and inject it in the HTML template.
    6. Write the full HTML string to a file for that page in the /public dir.


