import pytest
import json

from bin.seed.seed_roasters import sample_roaster_data


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
