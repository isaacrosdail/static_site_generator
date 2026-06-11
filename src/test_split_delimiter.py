
import unittest

from split_delimiter import (
    block_to_block_type, BlockType, markdown_to_blocks, markdown_to_html_node,
    split_nodes_delimiter, extract_markdown_images, extract_markdown_links,
    split_nodes_image, split_nodes_link, text_to_textnodes
)
from textnode import TextNode, TextType

class TestThing(unittest.TestCase):
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








class TestBlockToBlockType(unittest.TestCase):
    def test_block(self):
        block = """>this
> ought to match for a quote
>block."""
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

class TestSplitNodesDelimiter(unittest.TestCase):
    def test_one(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes, expected)

    def test_two(self):
        node = TextNode("This is text with a `code block word", TextType.TEXT)
        with self.assertRaises(Exception):
            new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)

    def test_three(self):
        node = TextNode("**bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes, expected)

    def test_multiple_nodes_input(self):
        node1 = TextNode("This is text with a `code block` word", TextType.TEXT)
        node2 = TextNode("This is text with another `code block` word", TextType.TEXT)
        node3 = TextNode("This is text with just normal words", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node1, node2, node3], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
            TextNode("This is text with another ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
            TextNode("This is text with just normal words", TextType.TEXT),
        ]
        self.assertEqual(len(new_nodes), 7)  # 3 for each code block ones, 1 for just the text type one
        self.assertEqual(new_nodes, expected)

    def test_passthrough_for_non_text_type(self):
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("already bold", TextType.BOLD)
        ]
        self.assertEqual(new_nodes, expected)

class TestExtractMDImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

class TestExtractMDLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        should_be = [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev")
        ]
        self.assertListEqual(should_be, matches)

    def test_should_reject_image(self):
        matches = extract_markdown_links(
            "This has an ![image](my_image_link)"
        )
        should_be = []
        self.assertListEqual(should_be, matches)

class TestSplitImages(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_two(self):
        node = TextNode("This doesn't even have a darn image!", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This doesn't even have a darn image!", TextType.TEXT)
            ],
            new_nodes,
        )


class TextSplitLinks(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](dennys.com) and another [second link](ihop.gov)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "dennys.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "ihop.gov"),
            ],
            new_nodes,
        )


class TextTextToTextNodes(unittest.TestCase):
    def test_one(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        new_nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            new_nodes,
        )


