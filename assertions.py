import json
import pytest
from typing import Any, List, Dict
from common.authentication import JWTAuthentication


class Assertions:
    @staticmethod
    def _parse_json(response: Any) -> Dict:
        """
        Helper method to parse JSON response safely.
        """
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            pytest.fail(f"Response is not in JSON format. Response content is {response.content}")

    @staticmethod
    def assert_json_value_by_name(response: Any, name: str, expected_value: Any) -> None:
        """
        Checks that the JSON response contains the expected value for a specific key.
        """
        response_as_dict = Assertions._parse_json(response)
        assert name in response_as_dict, f"Response JSON does not have key '{name}'"

        actual_value = response_as_dict[name]
        if isinstance(expected_value, str) and expected_value.strip() == "":
            expected_value = ""
        if isinstance(actual_value, list):
            actual_value = actual_value[0] if actual_value else None

        assert actual_value == expected_value, (
            f"Value for key '{name}' is {repr(actual_value)} but should be {repr(expected_value)}"
        )

    @staticmethod
    def assert_json_has_key(response: Any, name: str) -> None:
        """
        Checks that the JSON response contains a specific key.
        """
        response_as_dict = Assertions._parse_json(response)
        assert name in response_as_dict, f"Response JSON does not have key '{name}'"

    @staticmethod
    def assert_json_has_keys(response: Any, names: List[str]) -> None:
        """
        Checks that the JSON response contains specific keys.
        """
        response_as_dict = Assertions._parse_json(response)
        missing_keys = [name for name in names if name not in response_as_dict]
        assert not missing_keys, f"Response JSON is missing keys: {missing_keys}"

    @staticmethod
    def assert_status_code(response: Any, expected_status_code: int) -> None:
        """
        Checks the HTTP status code.
        """
        assert response.status_code == expected_status_code, (
            f"Unexpected status code! Expected {expected_status_code} but received {response.status_code}"
        )

    @staticmethod
    def assert_jwt_valid(response: Any) -> None:
        """
        Checks that the JSON response contains a valid JWT token with the correct type.
        """
        json_response = Assertions._parse_json(response)
        assert 'access_token' in json_response, "Response JSON does not contain 'access_token'"
        jwt_token = json_response['access_token']

        try:
            decoded_token = JWTAuthentication.decode_token(jwt_token)
        except ValueError as e:
            pytest.fail(f"JWT decoding failed: {e}")

        actual_type = decoded_token.get('type')
        assert actual_type and actual_type.lower() == "access", (
            f"Expected JWT type 'access', but got '{actual_type}'"
        )

    @staticmethod
    def assert_dicts_equal_except(
            updated_dict: Dict, original_dict: Dict, ignore_keys: List[str] = None
    ) -> None:
        """
        Recursively compares two dictionaries, ensuring that all keys not listed in `ignore_keys`
        have identical values. Supports nested dictionaries.
        """
        auto_updated_fields = ['modified_at']
        ignore_keys = set((ignore_keys or []) + auto_updated_fields)

        filtered_original = {k: v for k, v in original_dict.items() if k not in ignore_keys}
        filtered_updated = {k: v for k, v in updated_dict.items() if k not in ignore_keys}

        assert filtered_original.keys() == filtered_updated.keys(), (
            f"Key mismatch: expected {set(filtered_original.keys())}, got {set(filtered_updated.keys())}"
        )

        for key in filtered_original:
            orig_value, upd_value = filtered_original[key], filtered_updated[key]

            if isinstance(orig_value, dict) and isinstance(upd_value, dict):
                Assertions.assert_dicts_equal_except(upd_value, orig_value, list(ignore_keys))
            else:
                assert upd_value == orig_value, (
                    f"Value mismatch for key '{key}': expected {orig_value}, but received {upd_value}"
                )

    @staticmethod
    def assert_partial_update_response(response: Any, original_data: Dict, payload: Dict) -> None:
        """
        Validates a response after a partial update.
        """
        updated_data = Assertions._parse_json(response)
        special_keys = ["assigned_users", "observers_users", "admin_users"]

        for key, expected_value in payload.items():
            if key in special_keys:
                if key in updated_data:
                    Assertions.assert_user_list_field_equal(updated_data, key, expected_value)
                else:
                    pytest.fail(f"Did not receive key '{key}' in response")
            else:
                Assertions.assert_json_value_by_name(response, key, expected_value)

        ignore_keys = list(payload.keys())
        Assertions.assert_dicts_equal_except(updated_data, original_data, ignore_keys)

    @staticmethod
    def assert_response_schema_by_serializer(response: Any, serializer_class: Any) -> None:
        """
        Validates that the response data matches the schema defined by the serializer.
        """
        data = Assertions._parse_json(response)
        items = data.get("results", data)  # Handle pagination
        many = isinstance(items, list)
        serializer = serializer_class(data=items, many=many)
        assert serializer.is_valid(), f"Response schema does not match: {serializer.errors}"

    @staticmethod
    def assert_user_list_field_equal(data: Dict, field_key: str, expected_user_ids: List[int]) -> None:
        """
        Checks that the specified key in `data` contains a list of objects,
        where each object has a 'user' field matching the expected user IDs.
        """
        assert field_key in data, f"Response JSON does not have key '{field_key}'"
        user_list = data[field_key]
        assert isinstance(user_list, list), f"Key '{field_key}' should be a list"
        actual_ids = [item.get("user") for item in user_list]
        assert sorted(actual_ids) == sorted(expected_user_ids), (
            f"Expected user ids for '{field_key}': {expected_user_ids}, but got {actual_ids}"
        )
