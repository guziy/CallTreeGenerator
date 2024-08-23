__author__ = "huziy"
__date__ = "$20 aout 2011 14:33:52$"


class Node(object):
    def __init__(self, name=''):
        self.name = name
        self.children = []
        self.parents = []

    def get_gv_strings(self):
        lines = []
        for c in self.children:
            for line in c.get_gv_strings():
                if line not in lines:
                    lines.append(line)
            line = "{} -> {}; \n".format(self.name, c.name)
            if line not in lines:
                lines.append(line)
        return lines

    def add_child(self, child):
        if not child in self.children:
            self.children.append(child)

        if self not in child.parents:
            child.parents.append(self)

    def remove_child(self, child):
        child.parents.remove(self)
        self.children.remove(child)

    def insert_to_tree(self, tree, parent_id):
        current_id = tree.insert(parent_id, 'end', text=self.name)
        for c in self.children:
            c.insert_to_tree(tree, current_id)

    def remove_children(self):
        """
        Remove all children of the node
        """
        for c in self.children:
            c.parents.remove(self)

        self.children.clear()

    def crop_deeper_than(self, depth=1):
        if depth == 1:
            for c in self.children:
                c.remove_children()
        else:
            for c in self.children:
                c.crop_deeper_than(depth=depth - 1)


if __name__ == "__main__":
    print("Hello World")
