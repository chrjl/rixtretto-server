import re
import pytest


@pytest.mark.usefixtures("seed_sample_roasters")
def test_create_roasters(client, roasters_list):
    query = """
        query {
            roasters {
                name
                location {
                    country {
                        id
                    }
                    state
                    city
                }
            }
        }
    """

    response = client.post(
        "/",
        json={"query": query},
    )
    assert response.status_code == 200

    result = response.json()["data"]["roasters"]
    assert len(result) == len(roasters_list)

    for fetched, expected in zip(result, roasters_list):
        assert fetched["name"] == expected["name"]
        assert fetched["location"]["city"] == expected["city"]
        assert fetched["location"]["state"] == expected["state"]
        assert fetched["location"]["country"]["id"] == expected["country"]


@pytest.mark.parametrize(
    "name, city, state, country_id",
    [("Stereoscope", "Los Angeles", "CA", "US")],
)
def test_update_roaster(client, create_roaster, name, city, state, country_id):
    roaster_obj = create_roaster(
        {"name": name, "country": country_id},
    )

    query = """
    mutation($id: ID, $input: RoasterInput!) {
        roasterUpdate(id: $id, input: $input) {
            status
            roaster {
                name
                location {
                    city
                    state
                    country {
                        id
                        name
                    }
                }
            }
        }
    }
    """

    variables = {
        "id": roaster_obj["id"],
        "input": {
            "location": {
                "city": city,
                "state": state,
            },
        },
    }

    response = client.post("/", json={"query": query, "variables": variables})
    assert response.status_code == 200

    result = response.json()["data"]["roasterUpdate"]
    assert result["status"]

    assert result["roaster"]["name"] == name
    assert result["roaster"]["location"]["city"] == city
    assert result["roaster"]["location"]["state"] == state
    assert result["roaster"]["location"]["country"]["id"] == country_id


class TestErrors:
    @pytest.fixture
    def roaster_create(self, request, client):
        echo_response = request.node.get_closest_marker("echo_response")

        def _roaster_create(input):
            query = """
                mutation($input: RoasterInput!) {
                    roasterCreate(input: $input) {
                        status
                        error {
                            code
                            message
                        }
                        roaster {
                            id
                            name
                        }
                    }
                }
            """
            response = client.post(
                "/", json={"query": query, "variables": {"input": input}}
            )

            if (echo_response is not None) and (echo_response.args[0]):
                print(response.status_code)
                print(response.json())

            return response

        return _roaster_create

    @pytest.fixture
    def roaster_update(self, request, client):
        echo_response = request.node.get_closest_marker("echo_response")

        def _roaster_update(id, patch):
            query = """
                mutation($input: RoasterInput!) {
                    roasterCreate(input: $input) {
                        status
                        error {
                            code
                            message
                        }
                        roaster {
                            id
                            name
                        }
                    }
                }
            """
            response = client.post(
                "/", json={"query": query, "variables": {"id": id, "input": patch}}
            )

            if (echo_response is not None) and (echo_response.args[0]):
                print(response.status_code)
                print(response.json())

            return response

        return _roaster_update

    @pytest.fixture
    def test_response(self):
        def _test_response(response, http_status_code, resolver_error_code, keyword):
            assert response.status_code == http_status_code

            match (response.status_code):
                case 200:
                    result = response.json()["data"]["roasterCreate"]
                    assert result["error"]["code"] == resolver_error_code

                    if keyword:
                        assert re.search(keyword, result["error"]["message"], re.I)

                case 400:
                    errors = response.json()["errors"]

                    if keyword:
                        assert re.search(keyword, errors[0]["message"], re.I)

        return _test_response

    @pytest.mark.echo_response(False)
    @pytest.mark.parametrize(
        "input, http_status_code, resolver_error_code, keyword",
        [
            ({"location": {"countryId": "US"}}, 200, 400, "`name`"),
            ({"name": "test"}, 200, 400, "`location.countryId`"),
            ({"name": None}, 400, None, "validation"),
            (
                {"name": "test", "location": {"countryId": None}},
                400,
                None,
                "validation",
            ),
            (
                {"name": "test", "location": {"countryId": "ZZZ"}},
                400,
                None,
                "validation",
            ),
            (
                {"name": "test", "location": {"countryId": "ZZ"}},
                200,
                400,
                "data",
            ),
        ],
    )
    def test_roaster_create(
        self,
        roaster_create,
        test_response,
        input,
        http_status_code,
        resolver_error_code,
        keyword,
    ):
        response = roaster_create(input)
        test_response(response, http_status_code, resolver_error_code, keyword)

    @pytest.mark.echo_response(False)
    @pytest.mark.parametrize(
        "patch, http_status_code, resolver_error_code, keyword",
        [
            ({"name": None}, 400, None, "validation"),
            ({"location": {"countryId": None}}, 400, None, "validation"),
            ({"location": {"countryId": "ZZZ"}}, 400, None, "validation"),
            ({"name": "test", "location": {"countryId": "ZZ"}}, 200, 400, "data"),
        ],
    )
    def test_roaster_update(
        self,
        roaster_create,
        roaster_update,
        test_response,
        patch,
        http_status_code,
        resolver_error_code,
        keyword,
    ):
        input = {"name": "test", "location": {"countryId": "US"}}
        roaster = roaster_create(input).json()["data"]["roasterCreate"]["roaster"]

        response = roaster_update(roaster["id"], patch)
        test_response(response, http_status_code, resolver_error_code, keyword)
