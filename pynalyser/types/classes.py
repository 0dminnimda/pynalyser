import attr


@attr.s(auto_attribs=True)
class PynalyserType:
    name: str


objectType = PynalyserType("object")
