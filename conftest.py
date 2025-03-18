import pytest
import re
from rest_framework import status
from django.urls import reverse
from django.conf import settings
from core.jwt_token.token_service import JWTAuth
from qa_lib.my_django_client import MyDjangoClient
from typing import Callable, Any, Tuple, Union
from datetime import datetime


# ===========================
# Fixtures for Authentication
# ===========================
@pytest.fixture
def auth_client(db, user) -> MyDjangoClient:
    """Creates an instance of MyDjangoClient with authentication."""
    token = JWTAuth().generate_pair_of_tokens(subject=user.id, subject_type=SubjectType.USER.value)
    client = MyDjangoClient()
    client.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + token['access']
    return client


@pytest.fixture
def auth_superuser(db, superuser) -> MyDjangoClient:
    """Authenticates Django client as a superuser."""
    token = JWTAuth().generate_pair_of_tokens(subject=superuser.id, subject_type=SubjectType.USER.value)
    client = MyDjangoClient()
    client.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + token['access']
    return client


@pytest.fixture
def token_for_user(user) -> str:
    """Generates a JWT access token for a regular user."""
    expiration_time = settings.ACCESS_TOKEN_EXPIRATION_TIME
    return jwt.encode(
        {'sub': user.pk, 'exp': round((datetime.now() + expiration_time).timestamp()), 'type': 'access'},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


@pytest.fixture
def token_for_superuser(superuser) -> str:
    """Generates a JWT access token for a superuser."""
    expiration_time = settings.ACCESS_TOKEN_EXPIRATION_TIME
    return jwt.encode(
        {'sub': superuser.pk, 'exp': round((datetime.now() + expiration_time).timestamp()), 'type': 'access'},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


@pytest.fixture
def get_pair_of_tokens(user, client: Client) -> dict:
    """Returns tokens."""
    return JWTAuth().generate_pair_of_tokens(subject=user.id, subject_type=SubjectType.USER.value)


# ==============================
# Fixtures for Password Recovery
# ==============================
@pytest.fixture
def password_recovery_code(db, user) -> UserPasswordRecoveryCode:
    """Creates a password recovery code for a user."""
    unique_code = UserPasswordRecoveryCode.create_unique_code()
    return UserPasswordRecoveryCode.objects.create(user=user, code=unique_code)


# ==============================
# Fixtures for Utility Functions
# ==============================
@pytest.fixture
def n_numbered_chars() -> Callable[[int], str]:
    """Returns a function to generate a random alphanumeric string of a given length."""

    def internal(n: int) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

    return internal


@pytest.fixture
def generated_string(n_numbered_chars: Callable[[int], str]) -> Callable[[int], str]:
    """Returns a function that generates a random alphanumeric string of a given length."""
    return n_numbered_chars


@pytest.fixture
def fill_templated_values(request) -> Union[Tuple[Any, str], Tuple[Any, str, str]]:
    """
    Processes a parameterized tuple containing a payload and optional expected messages.
    Recursively replaces placeholders of the format "FIX::<fixture_name>" with
    actual fixture values.

    Args:
        request: The pytest request object containing the parameterized values.

    Returns:
        Tuple: Depending on the input, returns either (payload, description) or
        (payload, expected_message, description).
    """
    params = request.param
    payload = universal_replace(params[0], request)
    if len(params) == 2:
        description = params[1]
        return payload, description
    elif len(params) == 3:
        expected_message = params[1]
        description = params[2]
        return payload, expected_message, description
    else:
        raise ValueError('Invalid parameter tuple length. Must be 2 or 3.')


def universal_replace(obj: Any, request) -> Any:
    """
    Recursively iterates over an object (dict, list, str) and replaces all strings
    formatted as "FIX::<fixture_name>" with the corresponding fixture value.

    Args:
        obj (Any): The object to process, which can be a dict, list, or string.
    request: The pytest request object used to resolve fixture values.

    Returns:
        Any: The processed object with all placeholders replaced by their actual values.
    """
    match obj:
        case dict():
            return {k: universal_replace(v, request) for k, v in obj.items()}
        case list():
            return [universal_replace(item, request) for item in obj]
        case str():
            return resolve_placeholder(obj, request)
        case _:
            return obj


def resolve_placeholder(value: Any, request) -> Any:
    """
    If the value is a string formatted as "FIX::<fixture_name>(param)",
    resolves and returns the corresponding object.

    Args:
        value (Any): The value to check for a placeholder pattern.
        request: The pytest request object used to retrieve fixture values.

    Returns:
        Any: The resolved fixture value if the pattern matches, otherwise the original value.
    """
    fixture_pattern = re.compile(r'^FIX::(\w+)(?:\((\d+)\))?$')

    if isinstance(value, str) and (match := fixture_pattern.match(value)):
        fixture_name, param = match.groups()

        match fixture_name, param:
            case 'generated_string', str(length):  # Handles dynamically generated string lengths
                return request.getfixturevalue('generated_string')(int(length))
            case _, None:  # Handles standard fixtures without parameters
                return request.getfixturevalue(fixture_name)

    return value
