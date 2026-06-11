

import unittest
from block_markdown import (
    BlockType,
    markdown_to_blocks, block_to_block_type, markdown_to_html_node, extract_title
)



class TestExtractTitle(unittest.TestCase):
    def test_one(self):
        md = "Hey there Arnold\n# This is the #1 header of all time!"
        extracted = extract_title(md)
        self.assertEqual(extracted, "This is the #1 header of all time!")

    def test_raises_if_no_h1(self):
        md = "This doesn't even have an h1 at all!"
        with self.assertRaises(Exception):
            extract_title(md)


class TestMarkdownToHTMLNode(unittest.TestCase):

    def test_quoted(self):
        md = """> "I am in fact a Hobbit in all but size."\n>\n> -- J.R.R. Tolkien"""
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            """<div><blockquote>"I am in fact a Hobbit in all but size."\n\n -- J.R.R. Tolkien</blockquote></div>"""
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_headings(self):
        md = """
#### This is an h4 tag, with a p tag under it?

This is the body of text in said p tag.
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h4>This is an h4 tag, with a p tag under it?</h4><p>This is the body of text in said p tag.</p></div>",
        )

    def test_ol(self):
        md = """1. Gandalf
2. Bilbo
3. Sam
4. Glorfindel"""
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            "<div><ol><li>Gandalf</li><li>Bilbo</li><li>Sam</li><li>Glorfindel</li></ol></div>",
        )



class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )





class TestBlockToBlockType(unittest.TestCase):
    def test_quote_one(self):
        block = """>this
> ought to match for a quote
>block."""
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.QUOTE)

    def test_quote_two(self):
        block = ">I am in fact a Hobbit in all but size.\n>\n> -- J.R.R. Tolkien"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.QUOTE)


    def test_heading(self):
        block = "# This is a heading"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.HEADING)

    def test_code(self):
        block = """```
        my_var = "I am a coding god"
        my_age = 12
        print("I am the bestest")
        ```"""
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.CODE)

    def test_ul(self):
        block = """- First
- Second
- Third"""
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.UNORDERED_LIST)

    def test_ol(self):
        block = """1. First
2. Second
3. Third
4. Four
5. fifth
6. sixth
7. seventh
8. eighth
9. nine
10. ten"""
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.ORDERED_LIST)

    def test_ol_should_fail(self):
        block = """1. First
3. Third
7. Seventh"""
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.PARAGRAPH)


