
import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_one(self):
        node = HTMLNode("p", "hey", None, {"href": "https://www.google.com", "target": "_blank"})
        props_str = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), props_str)

    def test_two(self):
        node = HTMLNode("p", "hey", None, {"class": "my_class"})
        node2 = HTMLNode("h1", "hey", None, {"class": "my_class"})
        self.assertNotEqual(node, node2)

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(tag=None, value="Free as the wind")
        self.assertEqual(node.to_html(), "Free as the wind")

class TestParentNode(unittest.TestCase):
    def test_parent_to_html(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_deeper(self):
        inner_p = LeafNode("p", "mytext", {"class": "my_p"})
        inner_div_inner = ParentNode("div", [inner_p])
        inner_div_outer = ParentNode("div", [inner_div_inner])
        parent_node = ParentNode("main", [inner_div_outer])

        self.assertEqual(
            parent_node.to_html(),
            '<main><div><div><p class="my_p">mytext</p></div></div></main>',
        )

if __name__ == "__main__":
    unittest.main()

