import pytest
import zk2

class TestSearch:

    @pytest.mark.parametrize(
        ("q", "expected"),
        [
            ('apa', 0),
            ('service', 6),
            ('"wood-working', 1),
            ('diy workshop', 8),
            ('@1810', 2),
            ('diy "wood-working', 1),
            ('"brilliant @2201', 1),
        ]
    )
    def test_query1(self, q, expected):
        zk = zk2.ZK()
        assert len(zk.query(q)) == expected

