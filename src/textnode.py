
from enum import Enum

from htmlnode import LeafNode

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str | None = None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other) -> bool:
        # Good way to iter over properties of a class?
        return (
            self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )

    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if text_node.text_type not in TextType:
        raise Exception("Invalid text_type")
    node_map = {
        TextType.TEXT: LeafNode(value=text_node.text),
        TextType.BOLD: LeafNode("b", text_node.text),
        TextType.ITALIC: LeafNode("i", text_node.text),
        TextType.CODE: LeafNode("code", text_node.text),
        TextType.LINK: LeafNode("a", text_node.text, {"href": text_node.url or ""}),
        TextType.IMAGE: LeafNode("img", "", {"src": "", "alt": "alt text"}),
    }
    return node_map[text_node.text_type]


