import pytest


@pytest.mark.parametrize("name", ["dog", "cat"])
@pytest.mark.echo(True)
@pytest.mark.use_sample_data(True)
def test_hello(client, name):
    # graphql
    query = """
    query($name: String) { hello(name: $name) }
    """

    variables = {"name": name}

    response = client.post("/", json={"query": query, "variables": variables})

    assert response.status_code == 200
    assert response.json()["data"]["hello"] == f"Hello {name}!"
