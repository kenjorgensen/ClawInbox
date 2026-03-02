from email_mcp.db.models import Message
from email_mcp.vector.hybrid import hybrid_rank


def test_hybrid_rank_combines():
    fts = [
        Message(id=1, account_id=1, mailbox_id=1, uid=1, subject="a", from_addr="", to_addrs="", date="", text="", stored_path=""),
        Message(id=2, account_id=1, mailbox_id=1, uid=2, subject="b", from_addr="", to_addrs="", date="", text="", stored_path=""),
    ]
    vector = [
        (Message(id=2, account_id=1, mailbox_id=1, uid=2, subject="b", from_addr="", to_addrs="", date="", text="", stored_path=""), 0.1),
        (Message(id=3, account_id=1, mailbox_id=1, uid=3, subject="c", from_addr="", to_addrs="", date="", text="", stored_path=""), 0.2),
    ]
    results = hybrid_rank(fts, vector, limit=3)
    ids = [msg.id for msg in results]
    assert 1 in ids
    assert 2 in ids
    assert 3 in ids
