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
    "sample_data, error_code",
    [
        ({"country": "US"}, 400),
        ({"name": "test"}, 400),
    ],
)
def test_create_errors(create_roaster, sample_data, error_code):
    result = create_roaster(sample_data)
    assert result.get("code") == error_code


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
