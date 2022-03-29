import ast

from .cacher import Recorder, Reproducer


class AstRecorder(ast.NodeVisitor):
    def __init__(self, data, changes=None):
        self.reset(changes)

    def reset(self, data, changes=None) -> None:
        if changes is None:
            changes = []
        self.data = data
        self.cacher = Recorder(self.data, changes)

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        self.cacher_visit()
        prev_data = {**self.data}
        result = visitor(node)
        self.cacher_visit()
        self.cacher.change_data(**prev_data)
        return result

    def cacher_visit(self):
        self.cacher.visit()

    # def _generic_cached_visit(self, node):
    #     self.cacher_visit()
    #     print(self.cacher.counter, "generic visiting",
    #           ast.dump(node), self.data)
    #     prev_data = {**self.data}
    #     super().generic_visit(node)
    #     self.cacher_visit()
    #     print(self.cacher.counter, "change from generic visit", ast.dump(node),
    #           self.cacher.data, prev_data, self.cacher.data == prev_data)
    #     self.cacher.change_data(**prev_data)

    # def generic_visit(self, node) -> None:
    #     super().generic_visit(node)


class AstReproducer(ast.NodeVisitor):
    def __init__(self, data, changes):
        self.reset(data, changes)

    def reset(self, data, changes) -> None:
        self.data = data
        self.cacher = Reproducer(self.data, changes)

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        self.cacher_visit()
        result = visitor(node)
        self.cacher_visit()
        return result

    def cacher_visit(self):
        self.cacher.visit()


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

    t = Tst({"cls": None})
    t.visit(tree)
    t2 = Tst2({"cls": None}, t.cacher.changes)
    t2.visit(tree)
    print("\n", t.cacher.changes)


# class Test(ast.NodeVisitor):
#     def __init__(self):
#         super().__init__()
#         self.c = 0
#         self.changes = []
#         self.cacher = Recorder(self.changes)
#     def visit(self, node):
#         print(ast.dump(node), self.c)
#         self.c += 1
#         return super().visit(node)


# class NodeCounter(ast.NodeVisitor):
#     counter: int

#     def count(self, node) -> int:
#         self.counter = 0
#         self.generic_visit(node)
#         return self.counter

#     def generic_visit(self, node):
#         self.counter += 1
#         super().generic_visit(node)


# class NodeTransformer(ast.NodeVisitor):
#     def __init__(self):
#         self.changes = []
#         self.cacher = Recorder(self.changes)
#         self.nc = NodeCounter()

#     def generic_visit(self, node):
#         self.cacher.visit()
#         node_count_change = 0
#         for field, old_value in ast.iter_fields(node):
#             if isinstance(old_value, list):
#                 new_values = []
#                 for value in old_value:
#                     if isinstance(value, ast.AST):
#                         new_value = self.visit(value)
#                         if new_value is None:
#                             node_count_change -= self.nc.count(value)
#                             continue
#                         elif not isinstance(new_value, ast.AST):
#                             node_count_change -= self.nc.count(value)
#                             for nv in new_value:
#                                 node_count_change += self.nc.count(nv)
#                             new_values.extend(new_value)
#                             continue
#                         value = new_value
#                     new_values.append(value)
#                 old_value[:] = new_values
#             elif isinstance(old_value, ast.AST):
#                 new_node = self.visit(old_value)
#                 if new_node is None:
#                     node_count_change -= self.nc.count(old_value)
#                     delattr(node, field)
#                 else:
#                     node_count_change -= self.nc.count(old_value)
#                     node_count_change += self.nc.count(new_node)
#                     setattr(node, field, new_node)
#         return node
