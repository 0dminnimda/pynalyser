import ast

from cacher import Recorder, Reproducer


class AstRecorder(ast.NodeVisitor):
    def __init__(self, changes=None):
        self.reset(changes)

    def reset(self, changes=None) -> None:
        if changes is None:
            changes = []
        self.data = {"cls": None}
        self.cacher = Recorder(self.data, changes)

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        self.cacher.visit()
        prev_data = {**self.data}
        result = visitor(node)
        self.cacher.visit()
        self.cacher.change_data(**prev_data)
        return result


class AstReproducer(ast.NodeVisitor):
    def __init__(self, changes):
        self.reset(changes)

    def reset(self, changes) -> None:
        self.data = {"cls": None}
        self.cacher = Reproducer(self.data, changes)

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        self.cacher.visit()
        result = visitor(node)
        self.cacher.visit()
        return result

if __name__ == "__main__":
    class Tst(AstRecorder):
        def visit_ClassDef(self, node):
            self.cacher.change_data(cls=node.name)
            self.generic_visit(node)

    class Tst2(AstReproducer):
        def visit_ClassDef(self, node):
            self.generic_visit(node)

    tree = ast.parse("""
class T:
    pass
    #a = b
    class B:
        pass
    # b = c
class D:
    pass
#     b = c
#     c = d
    # d = e
pass
#T()
# D()
""")
    # "a = b = c = d.d = 6"

    t = Tst()
    t.visit(tree)
    t2 = Tst2(t.cacher.changes)
    t2.visit(tree)
    print("\n", t.cacher.changes)

