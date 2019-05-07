from aioidex.exceptions import IdexClientContentTypeError


def test_content_type_error():
    e = IdexClientContentTypeError(1, 2)
    assert e.status == 1
    assert e.content == 2
    assert str(e) == '[1] 2'
