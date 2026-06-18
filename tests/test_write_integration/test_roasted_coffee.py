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
    mutation($id: ID!, $input: CoffeeTagInput!) {
        roastedCoffeeTagAdd(id: $id, input: $input) {
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
                "input": {
                    "type": "profile",
                    "values": ["test_value"],
                },
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
    mutation($id: ID!, $input: CoffeeTagInput!) {
        roastedCoffeeTagDelete(id: $id, input: $input) {
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
            "variables": {"id": sample_data["id"], "input": {"type": "profile"}},
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
            "variables": {"id": sample_data["id"], "input": {"type": "tasting"}},
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
            "variables": {"id": sample_data["id"], "input": {"type": "error"}},
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
    mutation($id: ID!, $input: CoffeeTagInput!) {
        roastedCoffeeTagDelete(id: $id, input: $input) {
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
                "input": {
                    "type": "profile",
                    "values": [sample_data["profiles"][-1]],
                },
            },
        },
    )
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffeeTagDelete"]["roastedCoffee"]

    assert result["profiles"] == sample_data["profiles"][:-1]
    assert result["tasting"] == sample_data["tasting"]


def test_roasted_coffee_component_add_green_coffee(
    client,
    origin_id,
    create_roaster,
    create_green_coffee,
    create_roasted_coffee,
    create_component_association,
):
    roaster_name = "test roaster"
    sample_roasted_coffee_data = {
        "name": "sample roasted coffee",
        "roaster_name": roaster_name,
        "profiles": ["blend", "seasonal"],
        "tasting": ["cucumber", "watermelon", "hibiscus"],
    }
    sample_green_coffee_data = [
        {
            "name": "sample green 1",
            "origin_name": "Huila",
            "country_name": "Colombia",
            "processes": ["washed"],
            "varieties": ["typica", "caturra"],
        },
        {
            "name": "sample green 2",
            "origin_name": "Guatemala",
            "country_name": "Guatemala",
            "processes": ["honey", "black honey"],
            "varieties": ["catuai"],
        },
    ]

    sample_roaster = create_roaster({"name": roaster_name, "country": "US"})
    sample_roasted_coffee = create_roasted_coffee(sample_roasted_coffee_data)
    sample_green_coffees = [
        create_green_coffee(data) for data in sample_green_coffee_data
    ]

    results = [
        create_component_association(
            roasted_id=sample_roasted_coffee["id"], green_id=green_coffee["id"]
        )
        for green_coffee in sample_green_coffees
    ]

    for result in results:
        assert result["origin"] == None
        assert result["roastedCoffee"]["name"] == sample_roasted_coffee_data["name"]
        assert result["roastedCoffee"]["roaster"]["name"] == roaster_name

    assert set([result["greenCoffee"]["name"] for result in results]) == set(
        [
            sample_green_coffee["name"]
            for sample_green_coffee in sample_green_coffee_data
        ]
    )

    roasted_coffee_query = """
    query($ids: [ID]!) {
        roastedCoffees(ids: $ids) {
            name
            roaster {
                name
            }
            profiles
            tasting
            processes
            varieties

            components {
                greenCoffee {
                    name
                }
                origin {
                    name
                }
            }

            origins {
                name
            }
        }
    }
    """

    variables = {"ids": [sample_roasted_coffee["id"]]}

    response = client.post(
        "/",
        json={"query": roasted_coffee_query, "variables": variables},
    )
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffees"][0]

    assert result["name"] == sample_roasted_coffee_data["name"]
    assert result["roaster"]["name"] == roaster_name
    assert set(result["profiles"]) == set(sample_roasted_coffee_data["profiles"])
    assert set(result["tasting"]) == set(sample_roasted_coffee_data["tasting"])

    assert len(result["components"]) == len(sample_green_coffee_data)

    sample_processes = [
        process
        for sample_green_coffee in sample_green_coffee_data
        for process in sample_green_coffee["processes"]
    ]

    assert set(result["processes"]) == set(sample_processes)

    sample_varieties = [
        variety
        for sample_green_coffee in sample_green_coffee_data
        for variety in sample_green_coffee["varieties"]
    ]

    assert set(result["varieties"]) == set(sample_varieties)

    sample_green_coffee_names = [
        sample_green_coffee["name"] for sample_green_coffee in sample_green_coffee_data
    ]

    assert set(
        [component["greenCoffee"]["name"] for component in result["components"]]
    ) == set(sample_green_coffee_names)

    sample_green_coffee_origin_names = [
        sample_green_coffee["origin_name"]
        for sample_green_coffee in sample_green_coffee_data
    ]

    assert set(origin["name"] for origin in result["origins"]) == set(
        sample_green_coffee_origin_names
    )

    origin_query = """
    query($ids: [ID]!) {
        origins(ids: $ids) {
            roasters {
                id
                name
            }
            roastedCoffees {
                id
                name
            }
            greenCoffees {
                id
                name
            }
        }
    }
    """
    variables = {"ids": [origin_id(sample_green_coffee_data[0]["country_name"])]}

    response = client.post(
        "/",
        json={"query": origin_query, "variables": variables},
    )
    assert response.status_code == 200

    result = response.json()["data"]["origins"][0]

    assert result["roasters"][0]["name"] == roaster_name
    assert result["roastedCoffees"][0]["name"] == sample_roasted_coffee_data["name"]
    assert result["greenCoffees"][0]["name"] == sample_green_coffee_data[0]["name"]


def test_roasted_coffee_add_component_origin(
    client,
    create_roaster,
    create_roasted_coffee,
    create_component_association,
    origin_id,
):
    roaster_name = "test roaster"
    sample_roasted_coffee_data = {
        "name": "sample roasted coffee",
        "roaster_name": roaster_name,
        "profiles": ["blend", "seasonal"],
        "tasting": ["cucumber", "watermelon", "hibiscus"],
    }
    sample_origin_data = [
        {"name": "Huila", "process": "washed", "variety": "Caturra"},
        {"name": "Oaxaca", "process": "washed", "variety": "Typica"},
    ]

    sample_roaster = create_roaster({"name": roaster_name, "country": "US"})
    sample_roasted_coffee = create_roasted_coffee(sample_roasted_coffee_data)

    results = [
        create_component_association(
            roasted_id=sample_roasted_coffee["id"],
            origin_id=origin_id(sample_origin["name"]),
            process=sample_origin["process"],
            variety=sample_origin["variety"],
        )
        for sample_origin in sample_origin_data
    ]

    for result in results:
        assert result["greenCoffee"] == None
        assert result["roastedCoffee"]["name"] == sample_roasted_coffee_data["name"]
        assert result["roastedCoffee"]["roaster"]["name"] == roaster_name

    assert set([result["origin"]["name"] for result in results]) == set(
        [sample_origin["name"] for sample_origin in sample_origin_data]
    )

    query = """
    query($ids: [ID]!) {
        roastedCoffees(ids: $ids) {
            name
            roaster {
                name
            }
            profiles
            tasting
            processes
            varieties

            components {
                greenCoffee {
                    name
                }
                origin {
                    name
                }
            }

            origins {
                name
            }
        }
    }
    """

    variables = {"ids": [sample_roasted_coffee["id"]]}

    response = client.post("/", json={"query": query, "variables": variables})
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffees"][0]

    assert result["name"] == sample_roasted_coffee_data["name"]
    assert result["roaster"]["name"] == roaster_name
    assert set(result["profiles"]) == set(sample_roasted_coffee_data["profiles"])
    assert set(result["tasting"]) == set(sample_roasted_coffee_data["tasting"])

    assert len(result["components"]) == len(sample_origin_data)

    assert set(result["processes"]) == set(
        [component["process"] for component in sample_origin_data]
    )
    assert set(result["varieties"]) == set(
        [component["variety"] for component in sample_origin_data]
    )

    assert set(
        [component["origin"]["name"] for component in result["components"]]
    ) == set([origin["name"] for origin in sample_origin_data])

    assert set(origin["name"] for origin in result["origins"]) == set(
        [origin["name"] for origin in sample_origin_data]
    )


def test_roasted_coffee_delete_components(
    client,
    create_roaster,
    create_green_coffee,
    create_roasted_coffee,
    create_component_association,
    origin_id,
):
    roaster_name = "test roaster"
    sample_roasted_coffee_data = {
        "name": "sample roasted coffee",
        "roaster_name": roaster_name,
        "profiles": ["blend", "seasonal"],
        "tasting": ["cucumber", "watermelon", "hibiscus"],
    }
    sample_origin_data = [
        {"name": "Huila", "process": "washed", "variety": "Caturra"},
        {"name": "Oaxaca", "process": "washed", "variety": "Typica"},
    ]
    sample_green_coffee_data = [
        {
            "name": "sample green 1",
            "origin_name": "Colombia",
            "processes": ["washed"],
            "varieties": ["typica", "caturra"],
        },
        {
            "name": "sample green 2",
            "origin_name": "Guatemala",
            "processes": ["honey", "black honey"],
            "varieties": ["catuai"],
        },
    ]

    sample_roaster = create_roaster({"name": roaster_name, "country": "US"})
    sample_roasted_coffee = create_roasted_coffee(sample_roasted_coffee_data)
    sample_green_coffees = [
        create_green_coffee(data) for data in sample_green_coffee_data
    ]

    results = [
        *[
            create_component_association(
                roasted_id=sample_roasted_coffee["id"],
                origin_id=origin_id(sample_origin["name"]),
                process=sample_origin["process"],
                variety=sample_origin["variety"],
            )
            for sample_origin in sample_origin_data
        ],
        *[
            create_component_association(
                roasted_id=sample_roasted_coffee["id"], green_id=green_coffee["id"]
            )
            for green_coffee in sample_green_coffees
        ],
    ]
    for result in results:
        assert result["roastedCoffee"]["name"] == sample_roasted_coffee_data["name"]
        assert result["roastedCoffee"]["roaster"]["name"] == roaster_name

    mutation_query = """
    mutation($id: ID!, $input: CoffeeComponentInput!) {
        roastedCoffeeComponentDelete(id: $id, input: $input) {
            status
            roastedCoffee {
                id
                name
                components {
                    greenCoffee {
                        name
                    }
                    origin {
                        name
                    }
                    process
                    variety
                }
            }
        }
    }
    """

    component_count = len(sample_origin_data) + len(sample_green_coffee_data)

    inputs = [
        {"greenId": sample_green_coffees[-1]["id"]},
        {
            "originId": origin_id(sample_origin_data[-1]["name"]),
            "process": sample_origin_data[-1]["process"],
            "variety": sample_origin_data[-1]["variety"],
        },
    ]

    for input in inputs:
        response = client.post(
            "/",
            json={
                "query": mutation_query,
                "variables": {"id": sample_roasted_coffee["id"], "input": input},
            },
        )
        assert response.status_code == 200
        component_count -= 1

        result = response.json()["data"]["roastedCoffeeComponentDelete"][
            "roastedCoffee"
        ]
        assert len(result["components"]) == component_count

    query = """
    query {
        roastedCoffees {
            name
            components {
                greenCoffee {
                    id
                    name
                }
                origin {
                    id
                    name
                }
                process
                variety
                fraction
            }
        }
    }
    """

    response = client.post("/", json={"query": query})
    result = response.json()["data"]["roastedCoffees"][0]

    assert len(result["components"]) == component_count


def test_roasted_coffee_green_coffee_component_update(
    client,
    create_roaster,
    create_green_coffee,
    create_roasted_coffee,
    create_component_association,
):
    roaster_name = "test roaster"
    sample_roasted_coffee_data = {
        "name": "sample roasted coffee",
        "roaster_name": roaster_name,
        "profiles": ["blend", "seasonal"],
        "tasting": ["cucumber", "watermelon", "hibiscus"],
    }
    sample_green_coffee_data = [
        {
            "name": "sample green 1",
            "origin_name": "Huila",
            "country_name": "Colombia",
            "processes": ["washed"],
            "varieties": ["typica", "caturra"],
        }
    ]

    sample_roaster = create_roaster({"name": roaster_name, "country": "US"})
    sample_roasted_coffee = create_roasted_coffee(sample_roasted_coffee_data)
    sample_green_coffees = [
        create_green_coffee(data) for data in sample_green_coffee_data
    ]

    sample_green_coffee_components = [
        create_component_association(
            roasted_id=sample_roasted_coffee["id"], green_id=green_coffee["id"]
        )
        for green_coffee in sample_green_coffees
    ]
    for result in sample_green_coffee_components:
        assert (result["greenCoffee"] is None) or (result["origin"] is None)
        assert result["fraction"] is None

    update_query = """
    mutation($id: ID!, $input: CoffeeComponentInput) {
        roastedCoffeeComponentUpdate(id: $id, input: $input) {
            roastedCoffee {
                name
                components {
                    greenCoffee {
                        name
                    }
                    origin {
                        name
                    }
                    process
                    variety
                    fraction
                }
            }
        }
    }
    """

    # Test update None to number for green coffee component fraction
    variables = {
        "id": sample_roasted_coffee["id"],
        "input": {
            "greenId": sample_green_coffees[0]["id"],
            "fraction": 100,
        },
    }
    response = client.post("/", json={"query": update_query, "variables": variables})

    assert response.status_code == 200
    result = response.json()["data"]["roastedCoffeeComponentUpdate"]["roastedCoffee"]

    assert result["components"][0]["fraction"] == 100

    # Test update number to number for green coffee component fraction
    variables = {
        "id": sample_roasted_coffee["id"],
        "input": {
            "greenId": sample_green_coffees[0]["id"],
            "fraction": 20,
        },
    }
    response = client.post("/", json={"query": update_query, "variables": variables})

    assert response.status_code == 200
    result = response.json()["data"]["roastedCoffeeComponentUpdate"]["roastedCoffee"]

    assert result["components"][0]["fraction"] == 20

    # Test update number to None for green coffee component fraction
    variables = {
        "id": sample_roasted_coffee["id"],
        "input": {
            "greenId": sample_green_coffees[0]["id"],
            "fraction": None,
        },
    }
    response = client.post("/", json={"query": update_query, "variables": variables})

    assert response.status_code == 200
    result = response.json()["data"]["roastedCoffeeComponentUpdate"]["roastedCoffee"]

    assert result["components"][0]["fraction"] is None


def test_roasted_coffee_origin_component_update(
    client,
    origin_id,
    create_roaster,
    create_roasted_coffee,
    create_component_association,
):
    roaster_name = "test roaster"
    sample_roasted_coffee_data = {
        "name": "sample roasted coffee",
        "roaster_name": roaster_name,
        "profiles": ["blend", "seasonal"],
        "tasting": ["cucumber", "watermelon", "hibiscus"],
    }
    sample_origin_data = [{"name": "Huila", "process": "washed", "variety": "Caturra"}]

    sample_roaster = create_roaster({"name": roaster_name, "country": "US"})
    sample_roasted_coffee = create_roasted_coffee(sample_roasted_coffee_data)

    sample_origin_components = [
        create_component_association(
            roasted_id=sample_roasted_coffee["id"],
            origin_id=origin_id(sample_origin["name"]),
            process=sample_origin["process"],
            variety=sample_origin["variety"],
        )
        for sample_origin in sample_origin_data
    ]

    for result in sample_origin_components:
        assert (result["greenCoffee"] is None) or (result["origin"] is None)
        assert result["fraction"] is None

    update_query = """
    mutation($id: ID!, $input: CoffeeComponentInput) {
        roastedCoffeeComponentUpdate(id: $id, input: $input) {
            roastedCoffee {
                name
                components {
                    greenCoffee {
                        name
                    }
                    origin {
                        name
                    }
                    process
                    variety
                    fraction
                }
            }
        }
    }
    """

    # Test update None to number for green coffee component fraction
    variables = {
        "id": sample_roasted_coffee["id"],
        "input": {
            "originId": origin_id(sample_origin_data[0]["name"]),
            "process": sample_origin_data[0]["process"],
            "variety": sample_origin_data[0]["variety"],
            "fraction": 100,
        },
    }
    response = client.post("/", json={"query": update_query, "variables": variables})

    assert response.status_code == 200
    result = response.json()["data"]["roastedCoffeeComponentUpdate"]["roastedCoffee"]

    assert result["components"][0]["fraction"] == 100

    # Test update number to number for green coffee component fraction
    variables = {
        "id": sample_roasted_coffee["id"],
        "input": {
            "originId": origin_id(sample_origin_data[0]["name"]),
            "process": sample_origin_data[0]["process"],
            "variety": sample_origin_data[0]["variety"],
            "fraction": 20,
        },
    }
    response = client.post("/", json={"query": update_query, "variables": variables})

    assert response.status_code == 200
    result = response.json()["data"]["roastedCoffeeComponentUpdate"]["roastedCoffee"]

    assert result["components"][0]["fraction"] == 20

    # Test update number to None for green coffee component fraction
    variables = {
        "id": sample_roasted_coffee["id"],
        "input": {
            "originId": origin_id(sample_origin_data[0]["name"]),
            "process": sample_origin_data[0]["process"],
            "variety": sample_origin_data[0]["variety"],
            "fraction": None,
        },
    }
    response = client.post("/", json={"query": update_query, "variables": variables})

    assert response.status_code == 200
    result = response.json()["data"]["roastedCoffeeComponentUpdate"]["roastedCoffee"]

    assert result["components"][0]["fraction"] is None


@pytest.mark.usefixtures("seed_sample_roasters")
@pytest.mark.usefixtures("seed_sample_green_coffees")
@pytest.mark.usefixtures("seed_sample_roasted_coffees")
def test_roasted_coffee_component_update_error_handling(client):
    query = """
    mutation($id: ID!, $input: CoffeeComponentInput) {
        roastedCoffeeComponentUpdate(id: $id, input: $input) {
            status
            error {
                code
                message
            }
        }
    }
    """

    # Test error handling: roasted coffee not found
    variables = {
        "id": 9999,
        "input": {"originId": 1},
    }

    response = client.post("/", json={"query": query, "variables": variables})
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffeeComponentUpdate"]
    assert result["status"] == False
    assert result["error"]["code"] == 404

    # Both origin and green coffee components specified
    variables = {
        "id": 1,
        "input": {"originId": 1, "greenId": 1},
    }

    response = client.post("/", json={"query": query, "variables": variables})
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffeeComponentUpdate"]
    assert result["status"] == False
    assert result["error"]["code"] == 400

    # Neither origin nor green coffee components specified
    variables = {
        "id": 1,
        "input": {},
    }

    response = client.post("/", json={"query": query, "variables": variables})
    assert response.status_code == 200

    result = response.json()["data"]["roastedCoffeeComponentUpdate"]
    assert result["status"] == False
    assert result["error"]["code"] == 400


@pytest.mark.skip("incomplete refactoring")
class TestRoastedCoffeeComponentUpdate:
    @pytest.fixture(scope="class")
    def roaster_name(self):
        return "test roaster"

    @pytest.fixture(scope="class")
    def sample_roaster(self, roaster_name, create_roaster):
        return create_roaster({"name": roaster_name, "country": "US"})

    @pytest.fixture(scope="class")
    def sample_green_coffees(self, create_green_coffee):
        sample_green_coffee_data = [
            {
                "name": "sample green 1",
                "origin_name": "Huila",
                "country_name": "Colombia",
                "processes": ["washed"],
                "varieties": ["typica", "caturra"],
            }
        ]

        return [create_green_coffee(data) for data in sample_green_coffee_data]

    @pytest.fixture(scope="class")
    def sample_roasted_coffee(self, roaster_name, create_roasted_coffee):
        sample_roasted_coffee_data = {
            "name": "sample roasted coffee",
            "roaster_name": roaster_name,
            "profiles": ["blend", "seasonal"],
            "tasting": ["cucumber", "watermelon", "hibiscus"],
        }

        return create_roasted_coffee(sample_roasted_coffee_data)

    @pytest.fixture(scope="class")
    def sample_components(
        self,
        sample_roasted_coffee,
        sample_green_coffees,
        origin_id,
        create_component_association,
    ):
        sample_origin_data = [
            {"name": "Huila", "process": "washed", "variety": "Caturra"}
        ]

        sample_green_coffee_components = [
            create_component_association(
                roasted_id=sample_roasted_coffee["id"],
                green_id=green_coffee["id"],
            )
            for green_coffee in sample_green_coffees
        ]
        sample_origin_components = [
            create_component_association(
                roasted_id=sample_roasted_coffee["id"],
                origin_id=origin_id(sample_origin["name"]),
                process=sample_origin["process"],
                variety=sample_origin["variety"],
            )
            for sample_origin in sample_origin_data
        ]

        return {
            "green_coffees": sample_green_coffee_components,
            "origins": sample_origin_components,
        }

    def test_component_associations(self, sample_components):
        for component_association in sample_components["green_coffees"]:
            assert component_association["origin"] is None
            assert component_association["fraction"] is None
