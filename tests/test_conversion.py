"""WGS-84、GCJ-02 和 BD-09 坐标转换的测试。"""

import itertools

from prcoords_typed import CoordinateSystem, Position, convert

_SYSTEMS: list[CoordinateSystem] = ["wgs84", "gcj02", "bd09"]
_CASES: dict[str, dict[CoordinateSystem, Position]] = {
    "北京/首都": {
        "wgs84": Position(lng=116 + 35.9 / 60, lat=40 + 4.4 / 60),
        "gcj02": Position(lng=116.604140, lat=40.074380),
        "bd09": Position(lng=116.610670, lat=40.080272),
    },
    "北京/大兴": {
        "wgs84": Position(lng=116 + 24 / 60, lat=39 + 30 / 60),
        "gcj02": Position(lng=116.406192, lat=39.501340),
        "bd09": Position(lng=116.412597, lat=39.507676),
    },
    "鄂尔多斯/伊金霍洛": {
        "wgs84": Position(lng=109 + 51.9 / 60, lat=39 + 29.4 / 60),
        "gcj02": Position(lng=109.870522, lat=39.490848),
        "bd09": Position(lng=109.877133, lat=39.496571),
    },
}


def test_convert() -> None:
    for key1, key2 in itertools.permutations(iterable=_SYSTEMS, r=2):
        for name, case in _CASES.items():
            result: Position = convert(pt=case[key1], _from=key1, _to=key2)
            assert abs(result - case[key2]) < 1.5e-6, (
                f"{name} {key1}->{key2} 失败：\n{case[key1]}\n -> {result}\n != {case[key2]}"
            )
