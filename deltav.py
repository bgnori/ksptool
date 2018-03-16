import math
import json
from itertools import starmap


def tonne(x):
    return x*1000.0

def deltaV(Isp, m0, mt, gravitational_acc=9.80665):
    """
    >>> deltaV(440.0, tonne(374.8), tonne(60))
    7905.151497282325
    """
    if mt == 0:
        if m0 == 0:
            """ mathematically undefined, but pratically it's 0, since it is "null" craft. """
            return 0
        else:
            raise ValueError("mt == 0")
    return Isp * gravitational_acc * math.log(m0/mt)

def compositeIsp(*IspThrustPair):
    z = zip(*starmap(lambda Isp, th: (th, th/Isp), IspThrustPair))
    th, ff = map(sum, z)
    return th/ff


class Stage:
    def __init__(self, _parts, **kw):
        self._parts = _parts
        self._data = dict(kw)

    def __getattr__(self, name):
        if name.startswith("_calc_"):
            return None

        v = self._data.get(name, None)
        if v is not None:
            return v
        f = getattr(self, "_calc_" + name, None)
        if f is not None:
            return f()

        raise AttributeError(name)

    def _calc_Wet(self):
        if hasattr(self, "overhead"):
            try:
                return self.fuel / (1.0 - self.overhead)
            except Exception as e:
                raise AttributeError("Failed to calc: Wet") from e
        if hasattr(self, "Dry"):
            return self.Dry + self.fuel

    def _calc_Dry(self):
        try:
            return self.Wet - self.fuel
        except Exception as e:
            raise AttributeError("Failed to calc: Dry") from e

    def _calc_fuel(self):
        return self.Wet - self.Dry

    def _calc_Isp(self):
        if hasattr(self, "parts"):
            xs = []
            for name in self.parts:
                part = self._parts[name]
                Isp = part["atmosphereCurve"]["0"] #FIXME
                thrust = part["maxThrust"]
                xs.append((Isp, thrust))
            return compositeIsp(*xs)
        else:
            return 0

    def hasSomeThrust(self):
        return self.fuel > 0 #FIXME


def compoisiteDeltaV(rocket, parts):
    total_weight = 0.0
    total_deltaV = 0.0

    xs = []
    for s in rocket["stages"]:
        stage = Stage(parts, **s)
        v = deltaV(stage.Isp, total_weight + stage.Wet, total_weight + stage.Dry)
            
        v_per_fuel = v / stage.fuel if stage.hasSomeThrust() else None
        
        x = dict(s)
        x.update({
                "Isp": stage.Isp,
                "fuel":stage.fuel, 
                "mt": total_weight + stage.Wet,
                "m0": total_weight + stage.Dry, 
                "Delta V":v, 
                "Delta V per fuel":v_per_fuel,
                })

        total_weight += stage.Wet
        total_deltaV += v
        x["Subtotal Weight"] = total_weight
        x["Subtotal Delta V"] = total_deltaV
        xs.append(x)
    
    result = dict(rocket)
    result.update({"stages":xs, "Total Weight":total_weight,  "Total DeltaV":total_deltaV})
    return result



if __name__ == "__main__":
    import sys
    rocket = json.loads(sys.stdin.read())
    with open("parts.json") as f:
        parts = json.loads(f.read())
    """
    cd = compoisiteDeltaV(
            Stage(name="Payload", Wet=10.0, Dry=10.0, Isp=0),
            Stage(name="Alpha", overhead=0.3, fuel=7.0, Isp=300),
            Stage(name="Beta", overhead=0.1, fuel=9.0, Isp=300),
            )
    """
    print(json.dumps(compoisiteDeltaV(rocket, parts)))
