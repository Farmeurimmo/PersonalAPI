version = {
    "v1": [
        "mc",
        "portfolio",
        "plugins",
        "/",
    ],
}


def get_versions():
    return version.keys()


def get_latest_of(item):
    latest = None
    for v in version.keys():
        if item in version[v]:
            latest = v
    if latest is None:
        return None
    return get_version_formatted(latest)


def version_exists(item, v) -> bool:
    v = get_version_formatted(v)
    try:
        return version[v].__contains__(item)
    except KeyError:
        return False


def get_version_formatted(v):
    if not v.__contains__("v"):
        v = "v" + v
    return v
