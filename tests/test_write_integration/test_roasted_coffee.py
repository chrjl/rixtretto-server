import pytest
import json
from datetime import datetime


@pytest.mark.usefixtures("seed_sample_roasters")
@pytest.mark.usefixtures("seed_sample_roasted_coffees")
def test_create_roasted_coffee(client, roasted_coffees_list):
    query = """
        query {
            roastedCoffees {
                name
                roaster {
                    name
                }
                dateAdded
                dateRemoved
                profiles
                tasting
            }
        }
    """

    response = client.post("/", json={"query": query})

    result = response.json()["data"]["roastedCoffees"]
    assert len(result) == len(roasted_coffees_list)

    sorted_result = {coffee["name"]: coffee for coffee in result}

    assert set([coffee["name"] for coffee in result]) == set(
        [coffee["name"] for coffee in roasted_coffees_list]
    )

    for coffee in roasted_coffees_list:
        name = coffee["name"]

        assert sorted_result[name]["roaster"]["name"] == coffee["roaster_name"]

        if sorted_result[name]["dateAdded"]:
            assert datetime.fromisoformat(
                sorted_result[name]["dateAdded"]
            ) == datetime.fromisoformat(coffee["date_added"])
        if sorted_result[name]["dateRemoved"]:
            assert datetime.fromisoformat(
                sorted_result[name]["dateRemoved"]
            ) == datetime.fromisoformat(coffee["date_removed"])

        assert set(sorted_result[name]["profiles"]) == set(coffee["profiles"])
        assert set(sorted_result[name]["tasting"]) == set(coffee["tasting"])


@pytest.mark.parametrize(
    "name, roaster_name, date_added, date_removed, profiles",
    [("new_name", "new_roaster_name", "2026-07-01", None, ["new_profile", "seasonal"])],
)
@pytest.mark.usefixtures("seed_sample_roasters")
def test_update_roasted_coffee(
    client,
    roasted_coffees_list,
    create_roasted_coffee,
    create_roaster,
    name,
    roaster_name,
    date_added,
    date_removed,
    profiles,
):
    sample_data = {}
    sample_data_iterator = iter(roasted_coffees_list)

    while not (sample_data.get("profiles", []) and sample_data.get("tasting")):
        sample_data = next(sample_data_iterator)

    sample_roaster = create_roaster({"name": roaster_name, "country": "US"})
    sample_roasted_coffee = create_roasted_coffee(sample_data)

    mutation_query = """
    mutation($id:ID!, $input: RoastedCoffeeInput!) {
        roastedCoffeeUpdate(id: $id, input: $input) {
            status
            error {
                code
                message
            }
            roastedCoffee {
                id
                name
                profiles
                tasting
                roaster {
                    name
                }
            }
        }
    }
    """

    variables = {
        "id": sample_roasted_coffee["id"],
        "input": {
            "name": name,
            "roasterId": sample_roaster["id"],
            "dateAdded": date_added,
            "dateRemoved": date_removed,
            "profiles": profiles,
        },
    }

    response = client.post("/", json={"query": mutation_query, "variables": variables})
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffeeUpdate"]["roastedCoffee"]

    assert result["name"] == name
    assert result["roaster"]["name"] == roaster_name
    assert set(result["profiles"]) == set(profiles)
    assert set(result["tasting"]) == set(sample_data["tasting"])


def test_roasted_coffee_tag_add(client, seed_sample_roasted_coffees):
    sample_data = {}
    sample_data_iterator = iter(seed_sample_roasted_coffees)

    while not (sample_data.get("profiles", []) and sample_data.get("tasting")):
        sample_data = next(sample_data_iterator)

    mutation_query = """
    mutation($id: ID!, $type: String!, $values: [String]!) {
        roastedCoffeeTagAdd(id: $id, type: $type, values: $values) {
            status
            error {
                code
                message
            }
            roastedCoffee {
                id
                name
                profiles
                tasting
            }
        }
    }
    """

    response = client.post(
        "/",
        json={
            "query": mutation_query,
            "variables": {
                "id": sample_data["id"],
                "type": "profile",
                "values": ["test_value"],
            },
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffeeTagAdd"]["roastedCoffee"]

    assert len(result["profiles"]) == len(sample_data["profiles"]) + 1
    assert set(result["profiles"]) == set([*sample_data["profiles"], "test_value"])
    assert set(result["tasting"]) == set(sample_data["tasting"])


def test_roasted_coffee_tag_clear(client, seed_sample_roasted_coffees):
    sample_data = {}
    sample_data_iterator = iter(seed_sample_roasted_coffees)

    while not (sample_data.get("profiles", []) and sample_data.get("tasting")):
        sample_data = next(sample_data_iterator)

    mutation_query = """
    mutation($id: ID!, $type: String!) {
        roastedCoffeeTagDelete(id: $id, type: $type) {
            status
            error {
                code
                message
            }
            roastedCoffee {
                id
                name
                profiles
                tasting
            }
        }
    }
    """

    response = client.post(
        "/",
        json={
            "query": mutation_query,
            "variables": {"id": sample_data["id"], "type": "profile"},
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffeeTagDelete"]["roastedCoffee"]

    assert result["profiles"] == []
    assert set(result["tasting"]) == set(sample_data["tasting"])

    response = client.post(
        "/",
        json={
            "query": mutation_query,
            "variables": {"id": sample_data["id"], "type": "tasting"},
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffeeTagDelete"]["roastedCoffee"]

    assert result["profiles"] == []
    assert result["tasting"] == []

    response = client.post(
        "/",
        json={
            "query": mutation_query,
            "variables": {"id": sample_data["id"], "type": "error"},
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffeeTagDelete"]["error"]

    assert result["code"] == 400

def test_roasted_coffee_tag_delete(client, seed_sample_roasted_coffees):
    sample_data = {}
    sample_data_iterator = iter(seed_sample_roasted_coffees)

    while not (sample_data.get("profiles", []) and sample_data.get("tasting")):
        sample_data = next(sample_data_iterator)

    mutation_query = """
    mutation($id: ID!, $type: String!, $values: [String]) {
        roastedCoffeeTagDelete(id: $id, type: $type, values: $values) {
            status
            error {
                code
                message
            }
            roastedCoffee {
                id
                name
                profiles
                tasting
            }
        }
    }
    """

    response = client.post(
        "/",
        json={
            "query": mutation_query,
            "variables": {
                "id": sample_data["id"],
                "type": "profile",
                "values": [sample_data["profiles"][-1]],
            },
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffeeTagDelete"]["roastedCoffee"]

    assert result["profiles"] == sample_data["profiles"][:-1]
    assert result["tasting"] == sample_data["tasting"]
