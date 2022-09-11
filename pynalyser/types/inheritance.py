from typing import List, Optional, Tuple, Type

from .exceptions import duplicate_base, inheritance_cycle, invalid_mro


ENTRY = Type["Inheritable"]
INHERITABLES = Tuple[ENTRY, ...]


def find_a_good_head(linearizations: List[List[ENTRY]]) -> Optional[ENTRY]:
    for head, *_ in linearizations:
        if all(head not in tail for _, *tail in linearizations):
            return head
    return None


def linearization(obj: ENTRY, parents: INHERITABLES) -> INHERITABLES:
    parent_linearizations = [list(parent.mro) for parent in parents] + [list(parents)]
    linearization: List[ENTRY] = []

    # probably will take at most set(chain(*parent_linearizations)) iterations
    while 1:
        parent_linearizations = [lin for lin in parent_linearizations if lin]
        if len(parent_linearizations) == 0:
            return (obj, *linearization)

        head = find_a_good_head(parent_linearizations)
        if head is None:
            raise invalid_mro([lin.__name__ for lin in parents])

        linearization.append(head)
        for parent_linearization in parent_linearizations:
            if parent_linearization[0] == head:
                del parent_linearization[0]

    assert False, "Unreachable"


def validate_bases(obj: ENTRY, bases: INHERITABLES) -> None:
    visited = set()

    for base in bases:
        if base is obj:
            raise inheritance_cycle()

        if base not in visited:
            visited.add(base)
        else:
            raise duplicate_base(base.__name__)


def set_bases(obj: ENTRY, bases: INHERITABLES) -> None:
    validate_bases(obj, bases)
    obj.bases = bases
    obj.mro = linearization(obj, obj.bases)


_internal_counter = 0


def register_inheritance(obj: ENTRY) -> None:
    global _internal_counter
    _internal_counter += 1

    obj._type_id = _internal_counter


class Inheritable:
    mro: INHERITABLES = ()
    bases: INHERITABLES = ()
    _type_id: int = 0

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        register_inheritance(cls)

