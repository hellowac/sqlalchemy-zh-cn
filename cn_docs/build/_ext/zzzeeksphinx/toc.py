# mypy: ignore-errors
#!coding: utf-8
import re
from typing import cast

from docutils import nodes as docutils_nodes
from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.environment.adapters.toctree import TocTree


UNDERSCORE_RE = re.compile(r"_\w+\.(.+)$")


class TOCMixin:

    app: Sphinx

    def get_current_subtoc(self, current_page_name, start_from=None):
        """Return a TOC for sub-files and sub-elements of the current file.

        This is to provide a "contextual" navbar that shows the current page
        in context of all of its siblings, not just the immediate "previous"
        and "next".

        This allows a very long page with many sections to be broken
        into smaller pages while not losing the navigation of the overall
        section, with the added bonus that only the page-level bullets for
        the current subsection are expanded, thus making for a much shorter,
        "drill-down" style navigation.

        """
        assert self.app.env is not None
        assert self.app.builder is not None

        toc_tree = TocTree(self.app.env)
        raw_tree = toc_tree.get_toctree_for(
            current_page_name, self.app.builder, True, maxdepth=-1
        )
        local_toc_tree = toc_tree.get_toc_for(
            current_page_name, self.app.builder
        )

        if raw_tree is None:
            raw_tree = local_toc_tree

        # start with the bullets inside the doc's toc,
        # not the top level bullet, as we get that from the other tree
        if (
            not local_toc_tree.children
            or len(local_toc_tree.children[0].children) < 2
        ):
            local_tree = None
        else:
            local_tree = local_toc_tree.children[0].children[1]

        def _locate_nodes(nodes, level, outer=True):
            # this is a lazy way of getting at all the info in a
            # series of docutils nodes, with an absolute mimimal
            # reliance on the actual structure of the nodes.
            # we just look for refuris and the fact that a node
            # is dependent on another somehow, that's it, then we
            # flatten it out into a clean "tree" later.
            # An official Sphinx feature/extension
            # here would probably make much more use of direct
            # knowledge of the structure

            for elem in nodes:

                if hasattr(elem, "attributes"):
                    refuri = elem.attributes.get("refuri", None)
                else:
                    refuri = None

                name = None
                if refuri is not None:
                    for index, sub_elem in enumerate(elem.children, 1):
                        if isinstance(
                            sub_elem,
                            (docutils_nodes.Text, docutils_nodes.literal),
                        ):
                            continue
                        else:
                            break

                    local_text = elem.children[0:index]
                    name = str(local_text[0])
                    remainders = elem.children[index:]

                    yield level, refuri, name, local_text
                else:
                    remainders = elem.children

                # try to embed the item-level get_toc_for() inside
                # the file-level get_toctree_for(), otherwise if we
                # just get the full get_toctree_for(), it's enormous.
                if outer and refuri == "":
                    if local_tree is not None:
                        for ent in _locate_nodes(
                            [local_tree], level + 1, False
                        ):
                            yield ent
                else:
                    for ent in _locate_nodes(remainders, level + 1, outer):
                        yield ent

        def _organize_nodes(nodes):
            """organize the nodes that we've grabbed with non-contiguous
            'level' numbers into a clean hierarchy"""

            stack = []
            levels = []
            for level, refuri, name, text_nodes in nodes:
                if not levels or levels[-1] < level:
                    levels.append(level)
                    new_collection = []
                    if stack:
                        stack[-1].append(new_collection)
                    stack.append(new_collection)
                elif level < levels[-1]:
                    while levels and level < levels[-1]:
                        levels.pop(-1)
                        if level > levels[-1]:
                            levels.append(level)
                        else:
                            stack.pop(-1)

                stack[-1].append((refuri, name, text_nodes))
            return stack

        def _render_nodes(
            stack,
            level=0,
            start_from=None,
            nested_element=False,
            parent_element=None,
        ):

            printing = False
            if stack:
                printing = (
                    nested_element
                    or start_from is None
                    or start_from
                    in [elem[0] for elem in stack if isinstance(elem, tuple)]
                )
                if printing:
                    if not isinstance(
                        parent_element, docutils_nodes.bullet_list
                    ):
                        new_list = docutils_nodes.bullet_list()
                        parent_element.append(new_list)
                        parent_element = new_list
                while stack:
                    elem = stack.pop(0)
                    as_links = not isinstance(elem, tuple) or elem[0] != ""
                    if isinstance(elem, tuple):
                        refuri, name, text_nodes = elem
                        if not stack or isinstance(stack[0], tuple):
                            if printing:
                                list_item = docutils_nodes.list_item(
                                    classes=["selected"]
                                    if not as_links
                                    else []
                                )
                                list_item.append(
                                    self._link_node(refuri, text_nodes)
                                    if as_links
                                    else self._strong_node(refuri, text_nodes)
                                )
                                parent_element.append(list_item)
                        elif isinstance(stack[0], list):
                            if printing:
                                list_item = docutils_nodes.list_item(
                                    classes=["selected"]
                                    if not as_links
                                    else []
                                )
                                list_item.append(
                                    self._link_node(refuri, text_nodes)
                                    if as_links
                                    else self._strong_node(refuri, text_nodes)
                                )
                                parent_element.append(list_item)
                            else:
                                list_item = None
                            _render_nodes(
                                stack[0],
                                level=level + 1,
                                start_from=start_from,
                                nested_element=nested_element
                                or printing
                                or elem[0] == "",
                                parent_element=list_item or parent_element,
                            )
                    elif isinstance(elem, list):
                        _render_nodes(
                            elem,
                            level=level + 1,
                            start_from=start_from,
                            nested_element=nested_element,
                            parent_element=parent_element,
                        )

        element = docutils_nodes.bullet_list()

        nodes = _organize_nodes(_locate_nodes([raw_tree], 0))
        _render_nodes(nodes, start_from=start_from, parent_element=element)
        return cast(StandaloneHTMLBuilder, self.app.builder).render_partial(
            element
        )["fragment"]

    def get_local_toc(self, current_page_name, apply_exact_top_anchor=False):
        """Return the equivalent of Sphinx "toc" with options for rendering."""

        assert self.app.env is not None
        assert self.app.builder is not None

        # local toc tree.  will be missing the actual anchor for top section
        toc_tree = TocTree(self.app.env)
        local_toc_tree = toc_tree.get_toc_for(
            current_page_name, self.app.builder
        )

        # sphinx "toc" puts '#' as the anchor for the first section, meaning
        # if you click it, the page jumps to the top (unless you redefine #
        # which I'd rather not do).  This was all fine and good for a sidebar
        # toc, but a toc at the top of the page this just takes you away
        # from where you want to go.  The lead section of the content
        # has a real anchorname, so swap that into the toc
        if apply_exact_top_anchor:
            # get that top anchor name from the ids
            the_top_anchor = None
            sections = list(
                self.app.env.get_doctree(current_page_name).traverse(
                    docutils_nodes.section
                )
            )

            if sections:
                first_section = sections[0]

                if first_section.attributes["ids"]:
                    the_top_anchor = first_section.attributes["ids"][0]

            # have the top anchor and the toctree, put them together!
            if the_top_anchor:
                local_toc_tree = local_toc_tree.deepcopy()
                toc_tree_refs = list(
                    local_toc_tree.traverse(docutils_nodes.reference)
                )
                if toc_tree_refs:
                    toc_tree_refs[0]["anchorname"] = toc_tree_refs[0][
                        "refuri"
                    ] = f"#{the_top_anchor}"

        return cast(StandaloneHTMLBuilder, self.app.builder).render_partial(
            local_toc_tree
        )["fragment"]

    def _link_node(self, refuri, text_nodes):
        text_nodes = list(self._sub_out_underscores(text_nodes))
        link = docutils_nodes.reference("", "", text_nodes[0], refuri=refuri)
        link.extend(text_nodes[1:])
        cp = docutils_nodes.inline(classes=["link-container"])
        cp.append(link)
        return cp

    def _strong_node(self, refuri, text_nodes):
        cp = docutils_nodes.inline(classes=["link-container"])
        n1 = docutils_nodes.strong()
        n1.extend(self._sub_out_underscores(text_nodes))
        cp.append(n1)
        paramlink = docutils_nodes.reference(
            "",
            "",
            docutils_nodes.Text("¶", "¶"),
            refid="",
            # paramlink is our own CSS class, headerlink
            # is theirs.  Trying to get everything we can for existing
            # symbols...
            classes=["paramlink", "headerlink"],
        )

        cp.append(paramlink)
        return cp

    def _sub_out_underscores(self, nodes):
        for node in nodes:
            for lt in node.traverse(docutils_nodes.Text):
                m = UNDERSCORE_RE.match(str(lt))
                if m:
                    lt.parent.replace(lt, docutils_nodes.Text(m.group(1)))

            yield node
