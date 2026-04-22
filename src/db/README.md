# DB layer

## Queries API

Model queries organized into classes that inherit from a `Base` query.

```python
from db import queries

queries.Origin().filter_by_name({"starts_with": "B", "contains": "oli"}).select(["id"])
```

- Filters: returns a query object
  - Filters can be strung together
  - Some fields can accept SQLAlchemy selectables as subqueries.

- Select columns: returns a SQLAlchemy selectable
  - `select()` for entire object
  - `select(["list", "of", "column", "names"])` for specific columns

- Relationship queries
  - `get("attribute")` for entire object
  - `get("attribute", ["list", "of", "column", "names"])` for specific columsn of related object (not fully supported)
