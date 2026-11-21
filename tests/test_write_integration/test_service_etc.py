import pytest
import re
from httpx2 import Response


@pytest.fixture
def coffee_service_create(client):
    def _coffee_service_create(**input) -> Response:
        query = """
            mutation($input: CoffeeServiceInput!) {
                coffeeServiceCreate(input: $input) {
                    status
                    error {
                        code
                        message
                    }
                    service {
                        id
                        name
                    }
                }
            }
        """

        variables = {"input": input}

        return client.post("/", json={"query": query, "variables": variables})

    return _coffee_service_create


@pytest.fixture
def coffee_service_update(client):
    def _coffee_service_update(id, **input) -> Response:
        query = """
            mutation($id: ID!, $input: CoffeeServiceInput!) {
                coffeeServiceUpdate(id: $id, input: $input) {
                    status
                    error {
                        code
                        message
                    }
                    service {
                        id
                        name
                    }
                }
            }
        """

        variables = {"id": id, "input": input}

        return client.post("/", json={"query": query, "variables": variables})

    return _coffee_service_update


class TestMutations:
    @pytest.mark.parametrize("coffee_service_data", [{"name": "service_name"}])
    def test_create_service(
        self,
        coffee_service_create,
        coffee_service_data,
    ) -> int | None:
        response = coffee_service_create(**coffee_service_data)
        assert response.status_code == 200

        result = response.json()["data"]["coffeeServiceCreate"]

        assert result["status"] == True
        assert result["service"]["name"] == coffee_service_data["name"]

        return result.get("service", {}).get("id")

    @pytest.mark.parametrize(
        "input, update",
        [
            ({"name": "service_name"}, {"name": "updated_name"}),
            ({"name": "service_name"}, {}),
        ],
    )
    def test_create_and_update_service(
        self,
        coffee_service_create,
        coffee_service_update,
        input,
        update,
    ):
        id = self.test_create_service(coffee_service_create, input)

        response = coffee_service_update(id, **update)
        assert response.status_code == 200

        result = response.json()["data"]["coffeeServiceUpdate"]

        assert result["status"] == True

        if updated_name := update.get("name"):
            assert result["service"]["name"] == updated_name
        else:
            assert result["service"]["name"] == input["name"]


class TestErrors:
    @pytest.mark.parametrize(
        "coffee_service_data, http_error_code, resolver_error_code, keyword",
        [({}, 200, 400, "name")],
    )
    def test_create_service(
        self,
        coffee_service_create,
        coffee_service_data,
        http_error_code,
        resolver_error_code,
        keyword,
    ):
        response = coffee_service_create(**coffee_service_data)
        assert response.status_code == http_error_code

        result = response.json()["data"]["coffeeServiceCreate"]

        assert result["status"] == False
        assert result["error"]["code"] == resolver_error_code
        assert re.search(keyword, result["error"]["message"])
