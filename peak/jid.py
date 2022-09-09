def jid(name, domain):
    return name + "@" + domain


def name(jid: str):
    return jid.split("@")[0]


def domain(jid: str):
    return jid.split("@")[1].split("/")[0]


def resource(jid: str):
    return jid.split("@")[1].split("/")[1]


def group_sender(jid: str):
    return jid(resource(jid), domain(jid))
