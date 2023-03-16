from unittest.mock import Mock

import pytest
from werkzeug import exceptions

from app.source.errors import unmapped_instance, wrong_arguments


@pytest.mark.parametrize(
    "exception, function",
    [
        (exceptions.InternalServerError, wrong_arguments),
        (exceptions.NotFound, unmapped_instance),
    ],
)
def test_errors(exception, function):
    error = Mock()
    with pytest.raises(exception):
        function(error)
