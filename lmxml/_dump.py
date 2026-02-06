from lmxml._impl import to_lmxml

try:
    import pydantic

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

Primitives = str | int | float | bool
Structures = dict[str, 'JSONLike'] | list['JSONLike']
JSONLike = Primitives | Structures

if PYDANTIC_AVAILABLE:
    LMXMLAble = JSONLike | pydantic.BaseModel
else:
    LMXMLAble = JSONLike

def dumps(data: LMXMLAble) -> str:
    if PYDANTIC_AVAILABLE:
        if isinstance(data, pydantic.BaseModel):
            data = data.model_dump(mode="json")
    return to_lmxml(data)

