"""Which classes are live. A class is offered on the page (and run in its table) only once registered:

    @register("craftable")
    class InfinityEdge(BuildItem): ...

Kinds: craftable, radiant, artifact, emblem (items); trait, augment (buffs). Each list keeps registration order;
set19items / set19buffs decide the order the page sees."""
REGISTRIES = {kind: [] for kind in ("craftable", "radiant", "artifact", "emblem", "trait", "augment")}


def register(kind):
    names = REGISTRIES[kind]

    def add(cls):
        assert cls.__name__ not in names, f"{cls.__name__} registered twice as {kind}"
        names.append(cls.__name__)
        return cls
    return add
