import ast

import pytest
from pynalyser.abstract_code_representation.classes import (
    Action, Name, Pointer, Variable)


def test_Name():
    n = "name"

    name = Name(n)
    assert name.name is n

    with pytest.raises(TypeError):
        Name()


def test_Pointer():
    ind = 0

    pointer = Pointer(ind)
    assert pointer.action_ind is ind

    with pytest.raises(TypeError):
        Pointer()


def test_Action():
    a = ast.AST()
    pointer = Pointer(0)

    action = Action(a)
    assert action.action is a
    assert action.depends_on is None

    action = Action(a, pointer)
    assert action.action is a
    assert action.depends_on is pointer

    with pytest.raises(TypeError):
        Action()


def test_Variable():
    n = "name"
    actions = [Action(ast.AST())]
    scope = "global"

    variable = Variable(n)
    assert variable.name is n
    assert variable.actions == []

    with pytest.raises(TypeError):
        Variable()

    # should it be splitted or all in one 'with'?
    with pytest.raises(TypeError):
        Variable(n, actions)


# print(Variable("asd", []))
# print(Block())
# print(Scope("sdf"))
# print(Module("sdf"))
# print(Class("sdf"))
# print(Function("sdf"))
# print(Lambda(), Lambda([1, 2, 3]))
# print(Comprehension("sdf"))
# print(EltComprehension(ast.expr(), "sdf"))
# print(ListComp(ast.expr()))
# print(SetComp(ast.expr()))
# print(GeneratorExp(ast.expr()))
# print(DictComp(ast.expr(), ast.expr()))


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
