
import re
from enum import Enum

# blocks + block_types + the tree
from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import HTMLNode, ParentNode, LeafNode
from inline_markdown import split_nodes_delimiter, split_nodes_image, split_nodes_link



def extract_title(markdown: str) -> str:
    # Extract the h1 header and return it
    for line in markdown.split("\n"):
        if line.startswith("#") and not line.startswith("##"):
            return line[1:].strip()
    raise Exception("no h1 for document found!")


class BlockType(Enum):
    PARAGRAPH = "PARAGRAPH"
    HEADING = "HEADING"
    CODE = "CODE"
    QUOTE = "QUOTE"
    UNORDERED_LIST = "UNORDERED_LIST"
    ORDERED_LIST = "ORDERED_LIST"


def block_to_block_type(markdown_block: str) -> BlockType:
    if re.match(r"^#{1,6}.+$", markdown_block):
        return BlockType.HEADING
    if re.match(r"^```\n[\s\S]*```$", markdown_block):
        return BlockType.CODE
    if re.match(r"^(?:> ?.*\n)*> ?.*$", markdown_block):
        return BlockType.QUOTE
    if re.match(r"^(?:- .+\n)+- .+$", markdown_block):
        return BlockType.UNORDERED_LIST
    if re.match(r"^(?:\d+\. .+\n)*\d+\. .+$", markdown_block):
        for i, line in enumerate(markdown_block.split("\n")):
            number = int(line.split(".", 1)[0])
            if number != i + 1:
                return BlockType.PARAGRAPH

        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def markdown_to_blocks(markdown: str) -> list[str]:
    #blocks = markdown.split("\n\n")
    #stripped = map(lambda line: line.strip(), blocks)
    #filtered = list(filter(lambda block: block != "", stripped))
    # TODO: Tidy
    # Or, more succinctly:
    return [block.strip() for block in markdown.split("\n\n") if block.strip() != ""]


# Takes string of text + rets a list HTMLNodes that
#  represent the inline markdown using previously-created
#  functions (think TextNode -> HTMLNode)
def text_to_children(text: str) -> list[HTMLNode]:
    text_nodes = text_to_textnodes(text)

    result = []
    for node in text_nodes:
        html_node = text_node_to_html_node(node)
        result.append(html_node)
    return result



def text_to_textnodes(text: str) -> list[TextNode]:
    # This is **text** with an _italic_ word and a `code block` and an ![img](link.jpg) and a [link](site.com)
    nodes = []

    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes


def markdown_to_html_node(markdown: str) -> HTMLNode:
    # 1. Split markdown into blocks
    blocks = markdown_to_blocks(markdown)
    # 2. Loop over each block:
    block_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        # 1. Strip markdown syntax from block
        # 2. Pass inner text to text_to_children to get a list of LeafNodes
        # 3. Wrap that list in a ParentNode with the right tag
        if block_type is BlockType.CODE:
            # becomes a <pre><code>{CONTENT}</pre></code> section
            stripped = block.replace("```", "").removeprefix("\n")
            inner_node = LeafNode("code", stripped)
            outer_node = ParentNode("pre", [inner_node])
            block_nodes.append(outer_node)
        elif block_type is BlockType.HEADING:
            heading_lvl = block.count("#")
            stripped = block.lstrip("# ")
            children = text_to_children(stripped)
            parent_node = ParentNode(f"h{heading_lvl}", children)
            block_nodes.append(parent_node)
        elif block_type is BlockType.QUOTE:
            stripped = block.replace(">", "").strip()
            children = text_to_children(stripped)
            parent_node = ParentNode("blockquote", children)
            block_nodes.append(parent_node)
        elif block_type is BlockType.ORDERED_LIST:
            # Surround each block with ol, each item with li
            # "1. First\n2. Second\n3. Third"
            # So split on \n -> each entry is an li?
            splitted = block.split("\n")
            lis = []
            number = 1
            for item in splitted:
                stripped = item.removeprefix(f"{number}. ")
                number += 1
                lis.append(ParentNode("li", text_to_children(stripped)))
            parent_node = ParentNode("ol", lis)
            block_nodes.append(parent_node)

        elif block_type is BlockType.UNORDERED_LIST:
            splitted = block.split("\n")
            lis = []
            for item in splitted:
                stripped = item.removeprefix("- ")
                lis.append(ParentNode("li", text_to_children(stripped)))
            parent_node = ParentNode("ul", lis)
            block_nodes.append(parent_node)

        else:
            replaced = block.replace("\n", " ")
            children = text_to_children(replaced)
            parent_node = ParentNode("p", children)
            block_nodes.append(parent_node)

    single_parent = ParentNode("div", block_nodes)
    return single_parent


