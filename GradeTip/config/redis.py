from types import SimpleNamespace

post = SimpleNamespace(
    pid="pid",
    sid="sid",
    cid="cid",
    uid="uid",
    title="title",
    kind="kind",
    content="content",
    price="price",
    comments="comments",
    likes="likes",
    time="time",
    time_format="%m/%d/%Y %I:%M:%S %p %Z",
    ex=20 * 60,
    session_expiry=4 * 60 * 60
)

user = SimpleNamespace(
    uid="uid",
    pw="pw",
    dn="dn",
    sid="sid"
)


