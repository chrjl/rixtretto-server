from __future__ import annotations
from ariadne import MutationType

from db import models
from schema.normalized_types.roaster import normalized_roaster_input

mutation_type = MutationType()


@mutation_type.field("roasterCreate")
def resolve_roaster_create(_, info, input):
    Session = info.context["Session"]

    with Session() as session:
        roaster = models.Roaster(**normalized_roaster_input(input))
        session.add(roaster)

        session.commit()
        session.refresh(roaster)

    return {"status": True, "roaster": roaster}


@mutation_type.field("roasterUpdate")
def resolve_roaster_update(_, info, id, input):
    Session = info.context["Session"]

    with Session() as session:
        roaster = session.get(models.Roaster, id)

        for key, value in normalized_roaster_input(input).items():
            setattr(roaster, key, value)

        session.commit()
        session.refresh(roaster)

    return {"status": True, "roaster": roaster}
