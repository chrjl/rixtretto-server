import pytest
import json
from datetime import datetime

from bin.seed.seed_roasters import sample_roaster_data
from bin.seed.seed_green_coffees import sample_green_coffee_data
from bin.seed.seed_roasted_coffees import (
    sample_roasted_coffee_data,
    sample_coffee_association_data,
)


@pytest.fixture
def roasters_list():
    return sample_roaster_data()


@pytest.fixture
def create_roaster(client):
    def _create_roaster(roaster):
        roaster_name = roaster.get("name")
        country = roaster.get("country")
        state = roaster.get("state")
        city = roaster.get("city")
        details = roaster.get("details")

        mutation_query = """
        mutation($input: RoasterInput!) {
            roasterCreate(input: $input) {
                status
                error {
                    code
                    message
                }
                roaster {
                    id
                }
            }
        }
        """

        variables = {
            "input": {
                "name": roaster_name,
                "location": {"countryId": country, "state": state, "city": city},
                "details": json.dumps(details),
            }
        }

        response = client.post(
            "/",
            json={"query": mutation_query, "variables": variables},
        )

        assert response.status_code == 200

        result = response.json()["data"]["roasterCreate"]

        if result["status"] is True:
            return result["roaster"]
        else:
            return result["error"]

    return _create_roaster


@pytest.fixture
def seed_sample_roasters(roasters_list, create_roaster):
    roaster_ids = []

    for roaster in roasters_list:
        new_roaster = create_roaster(roaster)
        roaster_ids.append(new_roaster["id"])

    return roaster_ids


@pytest.fixture
def origin_id(client):
    def _origin_id(origin_name: str) -> int | None:
        query = """
            query($filter: Filter) {
                origins(filter: $filter) {
                    name
                    id
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": origin_name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["origins"]

        if len(result) == 1:
            return result[0]["id"]

        return None

    return _origin_id


@pytest.fixture
def green_coffees_list():
    return sample_green_coffee_data()


@pytest.fixture
def create_green_coffee(client, origin_id):
    def _create_green_coffee(green_coffee):
        input = {}

        for v in ["name", "processes", "varieties", "tasting"]:
            if v in green_coffee:
                input[v] = green_coffee[v]

        if any(
            [
                v in green_coffee
                for v in ["source", "source_type", "community", "origin_name"]
            ]
        ):
            input["source"] = {}

            if "source" in green_coffee:
                input["source"]["name"] = green_coffee["source"]
            if "source_type" in green_coffee:
                input["source"]["type"] = green_coffee["source_type"]
            if "community" in green_coffee:
                input["source"]["community"] = green_coffee["community"]
            if "origin_name" in green_coffee:
                input["source"]["originId"] = origin_id(green_coffee["origin_name"])

        if "details" in green_coffee:
            input["details"] = json.dumps(green_coffee["details"])

        query = """
        mutation($input: GreenCoffeeInput!) {
            greenCoffeeCreate(input: $input) {
                status
                error {
                    code
                    message
                }
                greenCoffee {
                    id
                }
            }
        }
        """

        response = client.post(
            "/", json={"query": query, "variables": {"input": input}}
        )

        assert response.status_code == 200

        result = response.json()["data"]["greenCoffeeCreate"]

        if result["status"] == True:
            return result["greenCoffee"]
        else:
            return result["error"]

    return _create_green_coffee


@pytest.fixture
def seed_sample_green_coffees(green_coffees_list, create_green_coffee):
    green_coffee_ids = []

    for coffee in green_coffees_list:
        new_green_coffee = create_green_coffee(coffee)
        green_coffee_ids.append(new_green_coffee["id"])

    return green_coffee_ids


@pytest.fixture
def roasted_coffees_list():
    return sample_roasted_coffee_data()


@pytest.fixture
def roaster_id(client):
    def _roaster_id(roaster_name):
        query = """
        query($filter: Filter) {
            roasters(filter: $filter) {
                id
            }
        }
        """

        variables = {"filter": {"name": {"starts_with": roaster_name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        assert response.status_code == 200

        return response.json()["data"]["roasters"][0]["id"]

    return _roaster_id


@pytest.fixture
def create_roasted_coffee(client, roaster_id):
    def _create_roasted_coffee(roasted_coffee_data):
        query = """
        mutation($input: RoastedCoffeeInput!) {
            roastedCoffeeCreate(input: $input) {
                status
                error {
                    code
                    message
                }
                roastedCoffee {
                    id
                    name
                    roaster {
                        id
                        name
                    }
                    dateAdded
                    dateRemoved
                    profiles
                    tasting
                }
            }
        }
        """

        input = {
            "name": roasted_coffee_data["name"],
            "roasterId": roaster_id(roasted_coffee_data["roaster_name"]),
            "dateAdded": roasted_coffee_data.get("date_added"),
            "dateRemoved": roasted_coffee_data.get("date_removed"),
            "profiles": roasted_coffee_data.get("profiles", []),
            "tasting": roasted_coffee_data.get("tasting", []),
        }

        response = client.post(
            "/",
            json={"query": query, "variables": {"input": input}},
        )

        assert response.status_code == 200
        result = response.json()["data"]["roastedCoffeeCreate"]

        assert result["roastedCoffee"]["name"] == roasted_coffee_data["name"]
        assert (
            result["roastedCoffee"]["roaster"]["name"]
            == roasted_coffee_data["roaster_name"]
        )

        if roasted_coffee_data.get("date_added"):
            assert datetime.fromisoformat(
                result["roastedCoffee"]["dateAdded"]
            ) == datetime.fromisoformat(roasted_coffee_data["date_added"])
        if roasted_coffee_data.get("date_removed"):
            assert datetime.fromisoformat(
                result["roastedCoffee"]["dateRemoved"]
            ) == datetime.fromisoformat(roasted_coffee_data["date_removed"])

        assert set(result["roastedCoffee"]["profiles"]) == set(
            roasted_coffee_data.get("profiles", [])
        )
        assert set(result["roastedCoffee"]["tasting"]) == set(
            roasted_coffee_data.get("tasting", [])
        )

        if result["status"] == True:
            return result["roastedCoffee"]
        else:
            return result["error"]

    return _create_roasted_coffee


@pytest.fixture
def seed_sample_roasted_coffees(
    seed_sample_roasters, roasted_coffees_list, create_roasted_coffee
) -> list[int]:
    roasted_coffee_ids = []

    for coffee in roasted_coffees_list:
        result = create_roasted_coffee(coffee)
        roasted_coffee_ids.append(result)

    return roasted_coffee_ids


@pytest.fixture
def create_component_association(client):
    def _create_component_association(
        roasted_id: int,
        green_id: int | None = None,
        origin_id: int | None = None,
        process: str | None = None,
        variety: str | None = None,
    ):
        query = """
        mutation($id: ID!, $input: CoffeeComponentInput) {
            roastedCoffeeComponentAdd(id: $id, input: $input) {
                roastedCoffee {
                    id
                    name
                    roaster {
                        id
                        name
                    }
                }
                greenCoffee {
                    id
                    name
                }
                origin {
                    id
                    name
                }
                fraction
            }
        }
        """

        variables = {"id": roasted_id, "input": {}}

        if green_id is not None:
            variables["input"] = {"greenId": green_id}
        elif origin_id is not None:
            variables["input"] = {
                "originId": origin_id,
                "process": process,
                "variety": variety,
            }

        response = client.post("/", json={"query": query, "variables": variables})
        assert response.status_code == 200

        result = response.json()["data"]["roastedCoffeeComponentAdd"]
        return result

    return _create_component_association
