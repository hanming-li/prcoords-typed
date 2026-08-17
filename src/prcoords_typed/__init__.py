"""在 WGS-84、GCJ-02 和 BD-09 之间进行转换。"""

import dataclasses
import math
import typing

type CoordinateSystem = typing.Literal["wgs84", "gcj02", "bd09"]


def _sin(i: float, /) -> float:
    return math.sin(math.radians(i))


def _sins(variable: float, /, *coefficients: tuple[float, float]) -> float:
    return (40 / 3) * sum(
        _external * _sin(3 * _internal * variable)
        for _external, _internal in coefficients
    )


@dataclasses.dataclass(order=True, frozen=True)
class Position:
    """经纬度坐标"""

    lat: float
    """纬度"""
    lng: float
    """经度"""

    def __add__(self, other: typing.Self) -> typing.Self:
        return self.__class__(lat=self.lat + other.lat, lng=self.lng + other.lng)

    def __sub__(self, other: typing.Self) -> typing.Self:
        return self.__class__(lat=self.lat - other.lat, lng=self.lng - other.lng)

    def __abs__(self) -> float:
        return math.hypot(self.lat, self.lng)

    @classmethod
    def from_polar(cls, r: float, theta: float) -> typing.Self:
        return cls(lat=r * math.sin(theta), lng=r * math.cos(theta))


def convert(pt: Position, _from: CoordinateSystem, _to: CoordinateSystem) -> Position:
    """给定源点、来源坐标系和目标坐标系，计算目标点。"""
    if _from == _to:
        return pt

    if _from == "wgs84" and _to == "gcj02":
        _dp: Position = pt - Position(lat=35, lng=105)
        """相对 (35N, 105E) 的偏移量。"""

        def _helper(c: float, cx: float, cy: float, csqrtabsx: float, /) -> float:
            return c + math.sumprod(
                [cx, cy, 0.1, 1 / csqrtabsx],
                [_dp.lng, _dp.lat, _dp.lng * _dp.lat, abs(_dp.lng) ** 0.5],
            )

        _dx: float = _helper(300, 1 + _dp.lng / 10, 2, 10) + _sins(
            _dp.lng, (1, 360), (1, 120), (1, 60), (2, 20), (7.5, 5), (15, 2)
        )
        """在横轴上的偏移量（米）。"""

        _dy: float = (
            _helper(-100, 2, 3 + _dp.lat / 5, 5)
            + _sins(_dp.lng, (1, 360), (1, 120))
            + _sins(_dp.lat, (1, 60), (2, 20), (8, 5), (16, 2))
        )
        """在纵轴上的偏移量（米）。"""

        GCJ_A: float = 6378245
        GCJ_EE: float = 0.006693421622965823
        _魔法数: float = 1 - GCJ_EE * _sin(pt.lat) ** 2
        _纬长: float = GCJ_A * math.radians((1 - GCJ_EE) / _魔法数**1.5)
        """该点附近 1 纬度的长度（单位为米）"""
        _经长: float = GCJ_A * math.radians(_sin(90 - pt.lat) / _魔法数**0.5)
        """该点附近 1 经度的长度（单位为米）"""
        return pt + Position(lat=_dy / _纬长, lng=_dx / _经长)

    if _from == "gcj02" and _to == "bd09":
        return Position(lat=6e-3, lng=6.5e-3) + Position.from_polar(
            r=abs(pt) + 2e-5 * _sin(pt.lat * 3e3),
            theta=math.atan2(pt.lat, pt.lng) + 3e-6 * _sin(90 - pt.lng * 3e3),
        )

    if _from == "wgs84" and _to == "bd09":
        _mid: Position = convert(pt=pt, _from="wgs84", _to="gcj02")
        return convert(pt=_mid, _from="gcj02", _to="bd09")

    """
    设恶化函数（WGS84->GCJ02、GCJ02->BD09）为 `f(x)`。

    函数具有局部线性性质，所以对相近的 x 和 y，有 `f(y) - y ≈ f(x) - x`，即 `x = y - (f(y) - f(x))`。

    设 `y = f(x)`，则 `x ≈ f(x) - (f(f(x)) - f(x))`。
    """

    _estimated_x: Position = pt - (convert(pt=pt, _from=_to, _to=_from) - pt)
    """估计的原始点"""
    _diff: Position = Position(lat=90, lng=180)
    """原始点转换的结果和实际点转换的结果的偏差"""

    while abs(_diff) > 1e-14:
        _diff: Position = convert(pt=_estimated_x, _from=_to, _to=_from) - pt
        _estimated_x -= _diff

    return _estimated_x
