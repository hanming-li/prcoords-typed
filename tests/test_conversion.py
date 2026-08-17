"""WGS-84、GCJ-02 和 BD-09 坐标转换的测试。"""

import itertools

import prcoords_typed

_CASES: dict[str, dict[prcoords_typed.CoordinateSystem, prcoords_typed.Position]] = {
    "北京首都国际机场": {
        "wgs84": prcoords_typed.Position(lng=116 + 35.9 / 60, lat=40 + 4.4 / 60),
        "gcj02": prcoords_typed.Position(
            lng=116.604139268664,
            lat=40.074379611546,
        ),  # 高德转换结果
        # "gcj02": prcoords_typed.Position(
        #     lng=116.604139,
        #     lat=40.074379,
        # ),  # 腾讯转换结果
    }  # Center of RWY 18L/36R
}
"""每个用例由源坐标系、目标坐标系和期望结果组成。"""


def test_convert() -> None:
    _systems: list[prcoords_typed.CoordinateSystem] = [
        "wgs84",
        "gcj02",
        # "bd09",
    ]
    for key1, key2 in itertools.permutations(iterable=_systems, r=2):
        for name, case in _CASES.items():
            result: prcoords_typed.Position = prcoords_typed.convert(
                pt=case[key1], _from=key1, _to=key2
            )
            assert abs(result - case[key2]) < 1e-6, (
                f"{name} {key1}->{key2} 失败：\n{case[key1]}\n -> {result}\n != {case[key2]}"
            )
