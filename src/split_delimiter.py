import re
from enum import Enum

from textnode import TextType, TextNode, text_node_to_html_node
from htmlnode import HTMLNode, ParentNode, LeafNode


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
            text_node = TextNode(stripped, TextType.TEXT)
            html_node = text_node_to_html_node(text_node)
            inner_node = ParentNode("code", [html_node])
            outer_node = ParentNode("pre", [inner_node])
            block_nodes.append(outer_node)
        elif block_type is BlockType.HEADING:
            heading_lvl = block.count("#")
            stripped = block.lstrip("# ")
            children = text_to_children(stripped)
            parent_node = ParentNode(f"h{heading_lvl}", children)
            block_nodes.append(parent_node)
        elif block_type is BlockType.QUOTE:
            stripped = block.replace(">", "")
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
                stripped = item.removeprefix(f"{number}.")
                number += 1
                lis.append(ParentNode("li", text_to_children(stripped)))
            print(f"{lis = }")
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
    if re.match(r"^(?:> ?.+\n)*> ?.+$", markdown_block):
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


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_list = []
    # If an old node is not a TextType.TEXT type, just add it to the new list as-is
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_list.append(node)
            continue
        # If a matching closing delimiter isn't found, raise exception for invalid md syntax
        ## even # of delimiters -> odd number of resulting strings in split, & vice versa
        split = node.text.split(delimiter)
        if len(split) % 2 == 0:
            raise Exception("Error on split: incomplete delimiter pairing(s)")

        for idx, val in enumerate(split):
            if val == "":
                continue
            if idx % 2 == 0: # <- inside TEXT
                new_list.append(TextNode(val, TextType.TEXT))
            else:            # <- inside whatever delimiter-type we're using rn
                new_list.append(TextNode(val, text_type))

    return new_list


# Tuples of alt text and URLs
# "Text with a ![rick roll](LINK) and ![obi wan](LINK2)"
# Basically we want:
#   the stuff      inside ![] -> that's our alt text
#   & right after, inside ( ) -> that's our link
def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    # Need to find the first !, then take what's inside the []
    # result = re.findall(r"!\[(.*?)\]\((.*?)\)", text)  our original.
    #  ->  mistakenly accepts: ![a]b](link) -> 'a]b' as alt text :(
    result = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)  # his: 
    return result

# Tuples of anchor text and URLs
def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    # (?<!!) = negative lookbehind to explicitly ensure we DON'T have a ! before [text](link)
    # This is the same regex as his above, but with the
    #    negative lookbehind to delineate images from links explicitly
    result = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return result


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    # TextNode(
    #    "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
    # TextType.TEXT,
    # )
    # So we split this into 4 pieces:
    # 1. text before link
    # 2. link 1
    # 3. text between links
    # 4. link 2
    # Similar to delimiter split, but here the delimiter are the links?
    new_list = []

    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_list.append(node)
            continue # skip

        # 3. Extract the images
        images = extract_markdown_images(node.text)
        # 4. Handle "no images" case: append original node + move on
        if len(images) == 0:
            new_list.append(node)
            continue

        current_text = node.text
        for img in images:
            splitted = current_text.split(f"![{img[0]}]({img[1]})", 1)
            # that means we have:
            # splitted[0] = "This is text with "
            # splitted[1] = "(img1) and (img2)"
            # So we append this new TextNode
            new_list.append(TextNode(splitted[0], TextType.TEXT))
            # Then make a new img node for this img
            new_list.append(TextNode(img[0], TextType.IMAGE, img[1]))
            current_text = splitted[1]   # continue to next

        # Guard against appending empty string
        if current_text != "":
            new_list.append(TextNode(current_text, TextType.TEXT))
    return new_list


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_list = []

    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_list.append(node)
            continue

        links = extract_markdown_links(node.text)
        if len(links) == 0:
            new_list.append(node)
            continue

        current_text = node.text
        for link in links:
            splitted = current_text.split(f"[{link[0]}]({link[1]})", 1)
            new_list.append(TextNode(splitted[0], TextType.TEXT))
            new_list.append(TextNode(link[0], TextType.LINK, link[1]))

            current_text = splitted[1]

        # Guard against appending empty string
        if current_text != "":
            new_list.append(TextNode(current_text, TextType.TEXT))

    return new_list


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
