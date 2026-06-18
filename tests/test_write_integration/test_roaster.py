import pytest


@pytest.fixture
def new_roaster_data():
    return {
        "name": "Stereoscope",
        "country_id": "US",
        "state": "CA",
        "city": "Los Angeles",
    }


@pytest.fixture
def create_new_roaster(client, new_roaster_data):
    roaster_name = new_roaster_data.get("name")
    country_id = new_roaster_data.get("country_id")
    state = new_roaster_data.get("state")
    city = new_roaster_data.get("city")

    mutation_query = """
    mutation($input: RoasterInput!) {
        roasterCreate(input: $input) {
            status
            roaster {
                id
            }
        }
    }
    """

    variables = {
        "input": {
            "name": roaster_name,
            "location": {"countryId": country_id, "state": state, "city": city},
        }
    }

    response = client.post(
        "/",
        json={"query": mutation_query, "variables": variables},
    )

    assert response.status_code == 200

    result = response.json()["data"]["roasterCreate"]["roaster"]
    return result


@pytest.mark.usefixtures("create_new_roaster")
def test_create_roaster(client, new_roaster_data):
    query = """
        query($filter: Filter) {
            roasters(filter: $filter) {
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
        json={
            "query": query,
            "variables": {
                "filter": {"name": {"starts_with": new_roaster_data["name"]}}
            },
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["roasters"][0]
    assert result["name"] == new_roaster_data["name"]
    assert result["location"]["country"]["id"] == new_roaster_data["country_id"]
    assert result["location"]["state"] == new_roaster_data["state"]
    assert result["location"]["city"] == new_roaster_data["city"]


@pytest.mark.parametrize(
    "name, city, state, country_id, country_name",
    [("Coffee Libre", "Seoul", None, "KR", "Korea")],
)
def test_update_roaster(
    client, create_new_roaster, name, city, state, country_id, country_name
):
    roaster_id = create_new_roaster["id"]

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
        "id": roaster_id,
        "input": {
            "name": name,
            "location": {
                "city": city,
                "state": state,
                "countryId": country_id,
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
    assert result["roaster"]["location"]["country"]["name"].startswith(country_name)
