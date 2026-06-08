from __future__ import annotations

## All optional:
# no tag -> render as raw text
# no val -> assumed to have children
# no children -> assumed to have a value
# no props -> simply won't have attrs
class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: list[HTMLNode] | None = None,
        props: dict[str, str] | None = None,
    ) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self) -> str:
        result = ""
        if self.props:
            for key, val in self.props.items():
                result += f' {key}="{val}"'
        return result

    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"


# Represents a single HTML tag with no children.
class LeafNode(HTMLNode):
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        props: dict[str, str] | None = None,
    ) -> None:
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self) -> str:
        if not self.value:
            raise ValueError("All leaf nodes must have a value")
        # Return as raw text
        if self.tag is None:
            return self.value
        return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'

    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.props})"


class ParentNode(HTMLNode):
    def __init__(
        self,
        tag: str,
        children: list[HTMLNode],
        props: dict[str, str] | None = None,
    ) -> None:
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("Parent nodes require .tag")
        if not self.children:
            raise ValueError("Parent nodes require .children")
        # For each child, append result of to_html to inner
        # ONCE after: slap on surrounding parent tag
        inner = ""
        for child in self.children:
            inner += child.to_html()
        return f'<{self.tag}>{inner}</{self.tag}>'

