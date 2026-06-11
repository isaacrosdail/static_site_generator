import re

from textnode import TextType, TextNode


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

