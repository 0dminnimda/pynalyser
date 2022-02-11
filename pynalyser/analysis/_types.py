from typing import List

import attr


@attr.s(auto_attribs=True)
class PynalyserType:
    name: str = attr.ib(default="object", kw_only=True)


@attr.s(auto_attribs=True)
class UnknownType(PynalyserType):
    pass


@attr.s(auto_attribs=True)
class UnionType(PynalyserType):
    types: List[PynalyserType]

    def get_name(self) -> str:
        return f"Union[{', '.join(tp.name for tp in self.types)}]"

    def set_name(self, name: str) -> None:
        pass

    name = property(get_name, set_name)


objectType = PynalyserType()
