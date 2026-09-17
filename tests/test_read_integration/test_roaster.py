import pytest


@pytest.mark.use_sample_data(True)
class TestRoasterColumns:
    query = """
    query($ids: [ID], $filter: Filter) {
        roasters(ids: $ids, filter: $filter) {
            id
            name
            location {
                city
                state
                country {
                    id
                    name
                    longName
                }
            }
            equipment {
                brand
                model
                capacity
            }
            details
        }
    }
    """

    def test_all_roasters(self, client, roaster_count):
        response = client.post("/", json={"query": self.query})
        result = response.json()["data"]["roasters"]

        assert response.status_code == 200
        assert len(result) == roaster_count

        for sample_roaster in result:
            assert type(sample_roaster.get("id")) == str
            assert type(sample_roaster.get("name")) == str
            assert type(sample_roaster.get("location")) == dict
            assert type(sample_roaster.get("equipment")) == dict
            assert type(sample_roaster.get("details")) == dict

            if location := sample_roaster.get("location"):
                if country := location.get("country"):
                    assert "id" in country
                    assert "name" in country
                    assert "longName" in country

    @pytest.mark.parametrize(
        "filter,name",
        [
            ({"name": {"starts_with": "C"}}, "Christopher L"),
            ({"name": {"starts_with": "G"}}, "Go Get Em Tiger"),
        ],
    )
    def test_filter_by_name(self, client, filter, name):
        variables = {"filter": filter}

        response = client.post("/", json={"query": self.query, "variables": variables})
        result = response.json()["data"]["roasters"]

        assert response.status_code == 200
        assert result[0]["name"] == name

    @pytest.mark.parametrize(
        "filter, count",
        [
            ({"city": "los ang"}, 2),
            ({"city": "san fran"}, 0),
            ({"state": "ca"}, 3),
            ({"countryId": "us"}, 5),
            ({"countryName": "united"}, 5),
            ({"countryName": "canada"}, 1),
        ],
    )
    def test_filter_by_location(self, client, filter, count):
        variables = {"filter": {"location": filter}}

        response = client.post("/", json={"query": self.query, "variables": variables})
        result = response.json()["data"]["roasters"]

        assert response.status_code == 200
        assert len(result) == count


class TestOriginRelationships:
    def test_roasted_coffees(self):
        """TODO"""
        pass
