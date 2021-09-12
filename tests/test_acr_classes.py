import ast

import pytest
from pynalyser.abstract_code_representation.classes import (
    Action, Actor, Name, Pointer, Variable)


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


def test_Actor():
    actions = [Action(ast.AST())]

    actor = Actor()
    assert actor.actions == []

    actor = Actor(actions=actions)
    assert actor.actions is actions

    with pytest.raises(TypeError):
        # those are only_kw for convenience of class construction
        # maybe we should not test for that
        Actor(actions)


def test_Variable():
    n = "name"
    actions = [Action(ast.AST())]
    scope = "global"

    variable = Variable(n)
    assert variable.name is n
    assert variable.actions == []
    assert variable.scope == ""

    variable = Variable(n, scope)
    assert variable.name is n
    assert variable.actions == []
    assert variable.scope is scope

    variable = Variable(n, scope, actions=actions)
    assert variable.name is n
    assert variable.actions is actions
    assert variable.scope is scope

    with pytest.raises(TypeError):
        Variable()

    # should it be splitted or all in one 'with'?
    with pytest.raises(TypeError):
        Variable(n, scope, actions)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
