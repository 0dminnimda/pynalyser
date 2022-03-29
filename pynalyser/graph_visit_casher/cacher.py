from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple, TypeVar

# Version upon what can be built other version
# that could handle graph changes automatically.
# Stores everyting in tree
# class Cacher:
#     children: Dict[str, "Cacher"]
#     change: Dict[str, Any]

#     def __init__(self) -> None:
#         self.children = []
#         self.change = {}

#     def save(self, name: str, obj: Any) -> None:
#         self.change[name] = obj

#     def visit_new(self, name: str) -> "Cacher":
#         new_node = type(self)()
#         self.children[name] = new_node
#         return new_node

#     def visit_existent(self, name: str, data: Dict[str, Any]) -> "Cacher":
#         data.update(self.change)
#         return self.children[name]


class Change:
    count: int
    data: Dict[str, Any]

    def __init__(self, count, data) -> None:
        self.count = count
        self.data = data

    def __repr__(self) -> str:
        return f"Change({self.count}, {self.data})"


class Base:
    data: Dict[str, Any]
    changes: List[Change]
    counter: int
    index: Optional[int]

    def __init__(self, data, changes) -> None:
        self.data = data
        self.changes = changes
        self.counter = -1
        self.index = None if not changes else 0

    def next_index(self, index: int) -> Optional[int]:
        new_index: Optional[int] = index + 1
        if new_index == len(self.changes):
            new_index = None
        return new_index


class Reproducer(Base):
    def visit(self) -> None:
        if self.index is None:
            pass
        elif self.changes[self.index].count == self.counter:
            self.data.update(self.changes[self.index].data)
            self.index = self.next_index(self.index)

        self.counter += 1


class Recorder(Reproducer):
    _changes_made: Set[int]

    def __init__(self, data, changes) -> None:
        super().__init__(data, changes)
        self._changes_made = set()

    # def visit(self) -> None:
    #     if self.index is None:
    #         pass
    #     elif self.changes[self.index].count == self.counter:
    #         self.index = self.next_index(self.index)

    #     self.counter += 1

    # def change_nodes(self, node_count_change: int) -> None:
    #     raise NotImplementedError("'change_nodes' is not supported yet")
    #     if not node_count_change:
    #         for i, v in enumerate(self.changes[self.index:]):
    #             self.changes[i].count = v.count + node_count_change
    #     # if node_count_change is negative and
    #     # overlaps with previous we need to delete it

    def change_data(self, **data: Any) -> None:
        if self.counter in self._changes_made:
            raise RuntimeError("Changes can be made only once per visit")
        self._changes_made.add(self.counter)

        # TODO: implement saving only difference between data
        if self.data == data:
            return None

        if self.index is None:
            self.changes.append(Change(self.counter, data))
        else:
            if self.changes[self.index].count == self.counter:
                self.changes[self.index].data = data
            else:
                self.changes.insert(self.index, Change(self.counter, data))
                self.index += 1
                assert self.index != len(self.changes)

        self.data.update(data)
