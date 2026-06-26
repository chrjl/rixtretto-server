import pytest
import json

from bin.seed.seed_roasters import sample_roaster_data
from bin.seed.seed_green_coffees import sample_green_coffee_data


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
