import pytest
import json


@pytest.mark.usefixtures("seed_sample_green_coffees")
def test_create_green_coffee(client, green_coffees_list):
    query = """
    query {
        greenCoffees {
            id
            name
            processes
            varieties
            tasting
            source {
                origin {
                    id
                    name
                }
            }
        }
    }
    """

    response = client.post("/", json={"query": query})
    result = response.json()["data"]["greenCoffees"]
    sorted_result = {coffee["name"]: coffee for coffee in result}

    assert len(result) == len(green_coffees_list)

    assert set(sorted_result.keys()) == set(
        [coffee["name"] for coffee in green_coffees_list]
    )

    for coffee in green_coffees_list:
        name = coffee["name"]

        assert set(sorted_result[name]["processes"]) == set(coffee["processes"])
        assert set(sorted_result[name]["varieties"]) == set(coffee["varieties"])
        assert set(sorted_result[name]["tasting"]) == set(coffee["tasting"])
        assert sorted_result[name]["source"]["origin"]["name"] == coffee["origin_name"]


@pytest.mark.parametrize(
    "name, new_processes, new_origin_name",
    [("new_name", ["honey", "black honey"], "Kona")],
)
def test_update_green_coffee(
    client,
    create_green_coffee,
    green_coffees_list,
    name,
    new_processes,
    new_origin_name,
):
    sample_data = green_coffees_list[0]
    sample_green_coffee = create_green_coffee(sample_data)

    mutation_query = """
    mutation($id:ID!, $input: GreenCoffeeInput!) {
        greenCoffeeUpdate(id: $id, input: $input) {
            status
            error {
                code
                message
            }
            greenCoffee {
                id
                name
                processes
                varieties
                tasting
                source {
                    origin {
                        id
                        name
                    }
                }
            }
        }
    }
    """

    variables = {
        "id": sample_green_coffee["id"],
        "input": {"name": name, "processes": new_processes},
    }

    response = client.post("/", json={"query": mutation_query, "variables": variables})
    assert response.status_code == 200

    result = response.json()["data"]["greenCoffeeUpdate"]["greenCoffee"]

    assert result["name"] == name
    assert set(result["varieties"]) == set(sample_data["varieties"])
    assert set(result["processes"]) == set(new_processes)


def test_green_coffee_tag_add(client, green_coffees_list, create_green_coffee):
    sample_green_coffee = green_coffees_list[0]
    green_coffee_obj = create_green_coffee(sample_green_coffee)

    mutation_query = """
    mutation($id: ID!, $type: String!, $values: [String]!) {
        greenCoffeeTagAdd(id: $id, type: $type, values: $values) {
            status
            error {
                code
                message
            }
            greenCoffee {
                id
                name
                processes
                varieties
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
                "id": green_coffee_obj["id"],
                "type": "process",
                "values": ["test_value"],
            },
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["greenCoffeeTagAdd"]["greenCoffee"]

    assert len(result["processes"]) == len(sample_green_coffee["processes"]) + 1
    assert set(result["processes"]) == set(
        [*sample_green_coffee["processes"], "test_value"]
    )
    assert result["varieties"] == sample_green_coffee["varieties"]
    assert result["tasting"] == sample_green_coffee["tasting"]


def test_green_coffee_tag_clear(client, green_coffees_list, create_green_coffee):
    sample_green_coffee = green_coffees_list[0]
    green_coffee_obj = create_green_coffee(sample_green_coffee)

    mutation_query = """
    mutation($id: ID!, $type: String!) {
        greenCoffeeTagDelete(id: $id, type: $type) {
            status
            error {
                code
                message
            }
            greenCoffee {
                id
                name
                processes
                varieties
                tasting
            }
        }
    }
    """

    response = client.post(
        "/",
        json={
            "query": mutation_query,
            "variables": {"id": green_coffee_obj["id"], "type": "process"},
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["greenCoffeeTagDelete"]["greenCoffee"]

    assert result["processes"] == []
    assert len(result["varieties"]) == len(sample_green_coffee["varieties"])
    assert len(result["tasting"]) == len(sample_green_coffee["tasting"])

    response = client.post(
        "/",
        json={
            "query": mutation_query,
            "variables": {"id": green_coffee_obj["id"], "type": "variety"},
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["greenCoffeeTagDelete"]["greenCoffee"]

    assert result["processes"] == []
    assert result["varieties"] == []
    assert len(result["tasting"]) == len(sample_green_coffee["tasting"])

    response = client.post(
        "/",
        json={
            "query": mutation_query,
            "variables": {"id": green_coffee_obj["id"], "type": "error"},
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["greenCoffeeTagDelete"]["error"]

    assert result["code"] == 400


def test_green_coffee_tag_delete(client, green_coffees_list, create_green_coffee):
    sample_green_coffee = green_coffees_list[0]
    green_coffee_obj = create_green_coffee(sample_green_coffee)

    mutation_query = """
    mutation($id: ID!, $type: String!, $values: [String]) {
        greenCoffeeTagDelete(id: $id, type: $type, values: $values) {
            status
            error {
                code
                message
            }
            greenCoffee {
                id
                name
                processes
                varieties
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
                "id": green_coffee_obj["id"],
                "type": "variety",
                "values": [sample_green_coffee["varieties"][-1]],
            },
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["greenCoffeeTagDelete"]["greenCoffee"]

    assert result["processes"] == sample_green_coffee["processes"]
    assert result["tasting"] == sample_green_coffee["tasting"]
    assert result["varieties"] == sample_green_coffee["varieties"][:-1]
