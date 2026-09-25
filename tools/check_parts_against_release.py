"""Is each published part file the same solid the released assembly holds?

Every part of these packages is declared from a file under `3D_Printed_Parts/` or
`Metal_Parts/`, and every placement in `arm.assy` is read off the released
assembly - which holds its own copy of each of those solids. A placement is only
right for the model it was measured from, so the two copies have to be the same
solid. This asks, part by part, by bounding box and by volume.

They are not all the same. Eleven of the 71 checked differ, and two of those are
swapped: the geometry published as `01_Lower_Arm_Cover.step` is what the release
assembles as the *upper* arm cover and the other way round, their volumes matching
across exactly. The rest look like revisions - the same outline with a different
volume, or the same solid 2 mm along its own axis. ../PARTCAD.md lists them under
the open data questions; nothing here decides which copy is authoritative.

Run it from the repository root:

    python3 tools/check_parts_against_release.py

It reads and reports; it changes nothing.
"""
import os
import sys

sys.path.insert(0, "tools")
import assy_from_reference as A
import yaml
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool

import build123d as bd


def measure(shape):
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box)
    lo, hi = box.CornerMin(), box.CornerMax()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return (lo.X(), hi.X(), lo.Y(), hi.Y(), lo.Z(), hi.Z()), props.Mass()


for key in ("b601-dm", "b601-rs"):
    spec = A.PACKAGES[key]
    doc = TDocStd_Document(TCollection_ExtendedString("d"))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    reader.ReadFile(os.path.join(spec["dir"], spec["step"]))
    reader.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    labels = TDF_LabelSequence()
    st.GetShapes(labels)
    products = {}
    for i in range(1, labels.Length() + 1):
        label = labels.Value(i)
        if XCAFDoc_ShapeTool.IsAssembly_s(label) or XCAFDoc_ShapeTool.IsReference_s(label):
            continue
        attr = TDataStd_Name()
        name = (attr.Get().ToExtString() if label.FindAttribute(TDataStd_Name.GetID_s(), attr) else "").split(":")[0]
        products.setdefault(A.normalize(name), label)

    parts = yaml.safe_load(open(os.path.join(spec["dir"], "partcad.yaml"))).get("parts") or {}
    print("=== %s" % key)
    checked = differs = 0
    for name, part in sorted(parts.items()):
        path = part.get("path")
        if not path or not path.endswith(".step"):
            continue
        label = products.get(A.normalize(os.path.splitext(os.path.basename(path))[0]))
        if label is None:
            continue
        checked += 1
        released, released_volume = measure(XCAFDoc_ShapeTool.GetShape_s(label))
        published, published_volume = measure(bd.import_step(os.path.join(spec["dir"], path)).wrapped)
        worst = max(abs(a - b) for a, b in zip(released, published))
        by_volume = abs(released_volume - published_volume)
        if worst < 0.01 and by_volume < 1.0:
            continue
        differs += 1
        print("  %-24s box off by %8.3f mm, volume by %9.1f mm^3  (%s)" % (name, worst, by_volume, path))
        print("      released  z %9.3f..%9.3f  volume %10.1f" % (released[4], released[5], released_volume))
        print("      published z %9.3f..%9.3f  volume %10.1f" % (published[4], published[5], published_volume))
    print("  %d of %d published part files differ from the solid the release assembles" % (differs, checked))
