#!/usr/bin/env python3
"""Write an arm's ASSY from the placements in the released STEP assembly.

Both arms are released as one STEP file with the product structure intact: every
component in it carries the name of the file that part is published as, and the
transformation that puts it where it belongs. That is precisely a link of an
ASSY - a part and a `location:` - so the tree transcribes rather than has to be
measured, and the result is the arm as its designers assembled it instead of a
pile of parts at the origin.

It also answers two things the readmes do not. The per-joint fastener counts are
in here (the readme gives one arm-wide minimum, "KM3*7mm x76+", which is not a
number anyone can order a joint's worth of screws from), and so is the grouping
into base and links, which was inferred from part names until now.

What this does not produce is the *reason* each part is where it is. A location
says where a part ends up; it does not say what holds it there, and `pc test`'s
connectivity check says so about every one of them. Replacing them with
`connect:` against declared ports is the next step, and it is a step this file
makes possible rather than one it takes: the placements are what the ports have
to reproduce, so they are what a port is checked against.

Run it from the repository root:

    python3 tools/assy_from_reference.py b601-dm
    python3 tools/assy_from_reference.py b601-rs

It needs OCP (the `partcad` environment has it) and rewrites the arm's `.assy`.
Re-run it when the released STEP changes; do not hand-edit the generated part of
the output.
"""

import argparse
import collections
import os
import re
import sys

import yaml
from OCP.gp import gp_Vec
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool

# Which release each package is generated from, and what to call the sub-assembly
# a component of the STEP's top level becomes. The STEP's own group names are the
# CAD's ("Link6:1", "07-RS-GRIPPER_ASM:1"); an ASSY name is read by somebody
# looking for a part, so the arms use one spelling for the same thing.
PACKAGES = {
    "b601-dm": {
        "dir": "hardware/reBot_B601_DM",
        "step": "reBot_B601_DM_v1.1_20260425.step",
        "release": "v1.1, exported 2026-04-25",
        "groups": {
            "Base": "base",
            "Link1": "link1",
            "Link2": "link2",
            "Link3": "link3",
            "Link4": "link4",
            "Link5": "link5",
            "Link6": "link6",
            "Gripper": "gripper",
        },
        "own_file": {"gripper": "gripper.assy"},
    },
    "b601-rs": {
        "dir": "hardware/reBot_B601_RS",
        "step": "reBot_B601_RS_v1.0_20260625.step",
        "release": "v1.0, exported 2026-06-25",
        "groups": {
            "01-BASE_ASM": "base",
            "02-RS-LINK-1_ASM": "link1",
            "03-RS-LINK-2_ASM": "link2",
            "04-RS-LINK-3_ASM": "link3",
            "05-RS-LINK-4_ASM": "link4",
            "06-RS-LINK-5_ASM": "link5",
            "07-RS-GRIPPER_ASM": "gripper",
        },
        "own_file": {"gripper": "gripper.assy"},
    },
}

# The parts whose geometry is not a file of this package, so nothing matches them
# by file name. Everything here is bought: what the CAD calls it, and what this
# repository declares it as.
#
# The names are the vendor shorthand of the released model. HM/KM/KA are the
# readme's own prefixes for socket head, countersunk and self-tapping; "PIN-DxLy"
# is a dowel pin of diameter x and length y; "GEAR-1M16C" is the module 1, 16
# tooth gear the gripper is driven by.
PURCHASED = {
    "b601-dm": {
        "6707ZZ": "bearing-6707zz",
        "6803ZZ": "bearing-6803zz",
        "AXK5578": "bearing-axk5578",
        "DM-J4310": "actuator-dm4310",
        "DM-J4340P": "actuator-dm4340p",
        "RAIL-170": "rail-mgn9-170",
        "SLIDER": "carriage-mgn9",
        "SILICONE-L30W9H2": "pad-silicone",
        "HM3-6": "screw-hm3-6",
        "HM3-12": "screw-hm3-12",
        "HM3-26": "screw-hm3-25",
        "HM4-75": "screw-hm4-75",
        "KM3-7": "screw-km3-7",
        "KM3-8-XIAO": "screw-km3-8",
        "KM3-9": "screw-km3-9",
        "KM3-12": "screw-km3-12",
        "KM3-16": "screw-km3-16",
        "KA3-12": "screw-ka3-12",
        "PIN-D3L8": "pin-d3x8",
        "PIN-D4L7": "pin-d4x7",
        "PIN-D4L10": "pin-d4x10",
        "PIN-D4L14": "pin-d4x14",
        "GEAR-1M16C": "gear-m1-16t",
        "S-M4-5-JIMI": "screw-m4x5-set",
    },
    "b601-rs": {
        "6-BEARING-F6803ZZ-OD26ID17H5": "bearing-6803zz",
        "9-SOCKET-XT30-2-2": "connector-xt30-socket",
        "6-THRUST-BEARING-OD78ID55H5": "bearing-axk5578",
        "9-M-RS00": "actuator-rs00",
        "9-M-RS06": "actuator-rs06",
        "9-XT30_2_2-V1": "connector-xt30",
        "7-HM3-8": "screw-hm3-8",
        "7-HM3-30": "screw-hm3-30",
        "7-HM4-8": "screw-hm4-8",
        "7-HM4-16": "screw-hm4-16",
        "7-HM4-70": "screw-hm4-70",
        "7-KM3-7": "screw-km3-7",
        "7-KM3-16": "screw-km3-16",
        "7-KA3-12": "screw-ka3-12",
        "6-RAIL-170": "rail-mgn9-170",
        "6-SLIDER": "carriage-mgn9",
        "6-SILICONE-L30W9H2": "pad-silicone",
        "5-GEAR-1M16C": "gear-m1-16t",
    },
}

# Where the file a part is declared from is not the file whose name the release
# gives that part. The release's name is the authority here, because it is what
# comes with the placement: it places the product it calls "01_Lower_Arm_Cover" on
# the lower arm, and the geometry published under that name is the *upper* cover's
# (see ../tools/check_parts_against_release.py). So the two are matched by what
# they are rather than by what they are called, and the basename match below would
# get both backwards.
PRODUCT_OVERRIDES = {
    "b601-dm": {
        "01_Lower_Arm_Cover": "lower-arm-cover",
        "01_Upper_Arm_Cover": "upper-arm-cover",
    },
    "b601-rs": {},
}

# A component name is "<product>:<instance>"; the product is what identifies the
# part.
INSTANCE_SUFFIX = re.compile(r":\d+$")

# How an alias of a part the two arms share records the file name the *other*
# release publishes that same solid under.
COPY_OF_THE_SAME_SOLID = re.compile(r"(?:DM|RS) copy: (\S+\.step)")


def normalize(text):
    """One spelling of a file's name, for comparing a CAD name with a file name.

    The released models spell one part three ways - '01_Joint6_7_Cable
    Restraint_A' as a component, with a space, and with an underscore as a file -
    so neither case nor the separator can be part of the comparison.
    """
    return re.sub(r"[\s_-]+", "", text).upper()


def read_tree(path):
    """The STEP's product structure: nested components with names and placements."""
    doc = TDocStd_Document(TCollection_ExtendedString("doc"))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    if not reader.ReadFile(path):
        sys.exit("cannot read %s" % path)
    reader.Transfer(doc)

    def name_of(label):
        attr = TDataStd_Name()
        if label.FindAttribute(TDataStd_Name.GetID_s(), attr):
            return attr.Get().ToExtString()
        return ""

    def placement(label):
        trsf = XCAFDoc_ShapeTool.GetLocation_s(label).Transformation()
        translation = trsf.TranslationPart()
        # OCP's binding writes the axis into the vector it is handed and returns
        # the angle, so the vector is an output parameter rather than a default.
        axis = gp_Vec(0, 0, 1)
        (angle,) = trsf.GetRotation().GetVectorAndAngle(axis)
        if trsf.IsNegative():
            # A mirror is not an ASSY location, and neither arm has one. Refuse
            # rather than write a placement that silently drops the reflection.
            sys.exit("%s is placed by a mirror, which a 'location:' cannot say" % name_of(label))
        return {
            "xyz": [round(translation.X(), 4), round(translation.Y(), 4), round(translation.Z(), 4)],
            "axis": [round(axis.X(), 6), round(axis.Y(), 6), round(axis.Z(), 6)],
            "angle": round(angle * 180.0 / 3.141592653589793, 4),
        }

    def walk(label):
        components = TDF_LabelSequence()
        out = []
        if not XCAFDoc_ShapeTool.GetComponents_s(label, components):
            return out
        for i in range(1, components.Length() + 1):
            component = components.Value(i)
            node = {"name": name_of(component)}
            node.update(placement(component))
            referred = TDF_Label()
            if XCAFDoc_ShapeTool.GetReferredShape_s(component, referred):
                node["product"] = name_of(referred)
                node["children"] = walk(referred)
            out.append(node)
        return out

    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    free = TDF_LabelSequence()
    shape_tool.GetFreeShapes(free)
    if free.Length() != 1:
        sys.exit("expected one root shape in %s, found %d" % (path, free.Length()))
    return walk(free.Value(1))


def declared_parts(package_dir):
    """What this package declares, indexed by the file each part's shape is in.

    An `alias` has no file of its own - it is another name for a part of another
    package, and the two releases publish one solid under two file names - so the
    file to index it by is the *source's*. Without that, every part the two arms
    share is a component of the released assembly that its own package appears not
    to declare.
    """
    config = yaml.safe_load(open(os.path.join(package_dir, "partcad.yaml")))
    parts = config.get("parts") or {}

    def path_of(part, depth=0):
        """The file a part's shape is in, following a second name to the first."""
        if part.get("path"):
            return part["path"]
        source = part.get("source")
        if not source or depth > 4:
            return None
        package, _, source_name = source.rpartition(":")
        if not package:
            return path_of(parts.get(source_name) or {}, depth + 1)
        # Only the two arms alias each other's parts; the third_party package
        # builds its shapes, so nothing there has a file to match on and the
        # PURCHASED table above is what names those.
        spec = PACKAGES.get(package.rsplit("/", 1)[-1])
        if spec is None:
            return None
        other = yaml.safe_load(open(os.path.join(spec["dir"], "partcad.yaml")))
        return path_of((other.get("parts") or {}).get(source_name) or {}, depth + 1)

    by_file = {}
    for name, part in parts.items():
        path = path_of(part)
        if path:
            by_file.setdefault(normalize(os.path.splitext(os.path.basename(path))[0]), name)
        # A shared part is one solid published in both releases under a file name
        # of each, and the alias records the other one: "... - RS copy: 2-RACK-1M.step".
        # The release this generator reads is *this* package's, so that is the name
        # its components carry - without it every shared part reads as undeclared.
        for other in COPY_OF_THE_SAME_SOLID.findall(part.get("desc") or ""):
            by_file.setdefault(normalize(os.path.splitext(other)[0]), name)
    return by_file


def descriptions_of(assy_path):
    """The descriptions the previous revision of this file gave each part.

    They are written by hand and say what a part is *for*, which no STEP file
    knows, so a regeneration carries them over rather than dropping them. One
    description per part name: every instance of a part is the same part.
    """
    if not os.path.exists(assy_path):
        return {}
    text = open(assy_path).read()
    # The hand-written revisions template their repeats; a description is not
    # inside a conditional, so dropping the tags is enough to read the YAML.
    text = re.sub(r"\{%.*?%\}", "", text, flags=re.S)
    try:
        config = yaml.safe_load(text)
    except yaml.YAMLError:
        return {}
    out = {}

    def walk(links):
        for link in links or []:
            if not isinstance(link, dict):
                continue
            name = link.get("part") or link.get("assembly")
            if name and link.get("description"):
                out.setdefault(name.split(":")[-1], link["description"].strip())
            walk(link.get("links"))

    walk((config or {}).get("links"))
    return out


def flatten(children, by_file, purchased, overrides, declared, unknown):
    """One link group's parts, with the category sub-groups dissolved.

    '<Link>_Metal_Parts' and its two siblings are how the CAD organizes a
    browser tree, not a stage of assembling anything, and each sits at the
    identity location - so a part's placement within the group is its placement
    within the link.
    """
    out = []
    for node in children:
        grandchildren = node.get("children") or []
        if grandchildren:
            if node["xyz"] != [0.0, 0.0, 0.0] or abs(node["angle"]) > 1e-9:
                sys.exit("the category group %s is not at the identity location" % node["name"])
            out.extend(flatten(grandchildren, by_file, purchased, overrides, declared, unknown))
            continue
        product = INSTANCE_SUFFIX.sub("", node.get("product") or node["name"])
        part = overrides.get(product) or purchased.get(product) or by_file.get(normalize(product))
        if part is None or part not in declared:
            # A name in the PURCHASED table above that this package does not
            # declare is not a placement: it is a part still to be declared, and
            # writing it here would produce an ASSY that does not load.
            unknown[product if part is None else "%s (-> %s)" % (product, part)] += 1
            continue
        out.append({"part": part, "product": product, "placement": node})
    return out


def location_text(placement):
    """An ASSY 'location:', as this repository writes one.

    The identity rotation has no axis, and OCCT answers the X axis for it; Z is
    what every other placement here turns about, so an unrotated part reads as
    turned about Z by nothing rather than about an axis chosen by arithmetic.
    """
    axis = placement["axis"]
    angle = placement["angle"]
    if abs(angle) < 1e-9:
        axis, angle = [0, 0, 1], 0

    def number(value):
        text = "%.4f" % value
        text = text.rstrip("0").rstrip(".")
        return text if text not in ("", "-0") else "0"

    return "[[%s], [%s], %s]" % (
        ", ".join(number(v) for v in placement["xyz"]),
        ", ".join(number(v) for v in axis),
        number(angle),
    )


HEADER = """\
# reBot Arm {title}.
#
# GENERATED by tools/assy_from_reference.py from {step},
# {release}, which is released with its product structure intact.
# Every placement below is the one the released assembly gives that component,
# and every count is how many of that part the released assembly holds. Do not
# edit it by hand: re-run the generator.
#
# The hand-written part of this file is the descriptions, which the generator
# carries over from the previous revision, and the grouping names: the CAD calls
# the gripper "{example}", and an ASSY is read by somebody looking
# for a part.
#
# Check it with:
#
#   pc bom -P //{package} arm        # the bill of materials this file produces
#   pc test -P //{package} arm       # what it says about how the arm goes together
#
# There is no projection of it: an assembly's drawing needs its shape built, and
# a build with a sub-assembly to stage first does not finish - see
# ../../PARTCAD.md.
#
# STATUS
#   * Geometrically correct: this is the arm as its designers assembled it, which
#     was checked part by part against the released assembly's own bounding box
#     for each one. So 'pc test's interference check is asking a real question
#     here, where over an arm at the identity location it was not.
#   * Every 'location:' still says where a part ends up rather than what holds it
#     there, which is what the connectivity check reports about each of them.
#     Ports and 'connect:' are what answer that, and these placements are what
#     such a port is checked against - see ../../PARTCAD.md.
#   * {coverage}

links:
"""

SUB_HEADER = """\
# The {name} of the reBot Arm {title}, on its own.
#
# GENERATED by tools/assy_from_reference.py from {step}: the {count} components
# the released assembly puts in this group, at the placements it gives them
# relative to the group. ./arm.assy places the group. Do not edit by hand.
#
# The two arms hold the same solids here - the racks, the slider bracket, the
# extensions, the gear connector, the rail, its carriages and the gear are one
# part each, declared once and aliased - and they do not place them to the same
# numbers. Measured from the slider bracket, the two releases agree on every one
# of these parts in X and differ in Z: the carriages are at +/-14.8 mm here
# against +/-14.3 in the other release, the racks at +/-4.125 against +/-4.175,
# the extensions at +/-0.069 against +/-0.119. So there is one set of parts and
# two grippers rather than one shared sub-assembly, and that is an argument for
# ports: a placement derived from the parts cannot disagree with itself, while two
# copied placements can. See ../../PARTCAD.md.

links:
"""


def links_text(parts, descriptions, indent):
    """One group's links, as YAML lines at the given indentation."""
    out = []
    counts = collections.Counter(part["part"] for part in parts)
    seen = collections.Counter()
    for part in sorted(parts, key=lambda p: (p["part"], p["placement"]["xyz"])):
        out.append("%s- part: %s" % (indent, part["part"]))
        if counts[part["part"]] > 1:
            seen[part["part"]] += 1
            out.append("%s  name: %s-%d" % (indent, part["part"], seen[part["part"]]))
        if descriptions.get(part["part"]) and seen[part["part"]] in (0, 1):
            out.append("%s  description: >-" % indent)
            for line in wrap(descriptions[part["part"]], 70):
                out.append("%s    %s" % (indent, line))
        out.append("%s  location: %s" % (indent, location_text(part["placement"])))
    return out


def generate(key):
    spec = PACKAGES[key]
    package_dir = spec["dir"]
    step_path = os.path.join(package_dir, spec["step"])
    assy_path = os.path.join(package_dir, "arm.assy")

    by_file = declared_parts(package_dir)
    declared = set(yaml.safe_load(open(os.path.join(package_dir, "partcad.yaml"))).get("parts") or {})
    purchased = PURCHASED[key]
    overrides = PRODUCT_OVERRIDES[key]
    descriptions = descriptions_of(assy_path)
    unknown = collections.Counter()

    tree = read_tree(step_path)
    groups = []
    loose = []
    for node in tree:
        product = INSTANCE_SUFFIX.sub("", node.get("product") or node["name"])
        name = spec["groups"].get(product)
        if name is not None:
            groups.append((name, node, flatten(node.get("children") or [], by_file, purchased, overrides, declared, unknown)))
            continue
        if node.get("children"):
            unknown["<group> " + product] += 1
            continue
        # A part of the top level rather than of a link: the released assembly has
        # a handful, and where the CAD left them is not a group of anything.
        loose.extend(flatten([node], by_file, purchased, overrides, declared, unknown))
    # The CAD's own order is the order the arm is built in; keep it.
    order = list(spec["groups"].values())
    groups.sort(key=lambda g: order.index(g[0]))
    if loose:
        groups.append(("unassigned", {"xyz": [0, 0, 0], "axis": [0, 0, 1], "angle": 0}, loose))

    placed = sum(len(parts) for _, _, parts in groups)
    missing = sum(unknown.values())
    coverage = "%d of the %d components of the released assembly are placed here." % (placed, placed + missing)
    if missing == 1:
        coverage += " The one that is not is named at the end of this file."
    elif missing:
        coverage += " The %d that are not are named at the end of this file." % missing

    out = [
        HEADER.format(
            title=key.replace("b601-", "B601 ").upper(),
            step=spec["step"],
            release=spec["release"],
            package="pub/robotics/rebot/devarm/" + key,
            example=[k for k, v in spec["groups"].items() if v == "gripper"][0],
            coverage=coverage,
        )
    ]

    written = []
    for name, node, parts in groups:
        own_file = spec.get("own_file", {}).get(name)
        out.append("  # " + "-" * 75)
        if own_file:
            # A group the package declares as an assembly of its own: this file
            # places it, and that file holds its parts. Two files rather than one
            # because the package renders a document for it and because the
            # gripper is the assembly somebody works on without the arm around it.
            out.append("  - assembly: %s" % name)
            if descriptions.get(name):
                out.append("    description: >-")
                for line in wrap(descriptions[name], 74):
                    out.append("      " + line)
            out.append("    location: %s" % location_text(node))
            out.append("")
            written.append(
                (
                    os.path.join(package_dir, own_file),
                    "\n".join(
                        [
                            SUB_HEADER.format(
                                name=name,
                                title=key.replace("b601-", "B601 ").upper(),
                                step=spec["step"],
                                count=len(parts),
                            )
                        ]
                        + links_text(parts, descriptions, indent="  ")
                    ).rstrip()
                    + "\n",
                )
            )
            continue
        out.append("  - name: %s" % name)
        if descriptions.get(name):
            out.append("    description: >-")
            for line in wrap(descriptions[name], 74):
                out.append("      " + line)
        out.append("    location: %s" % location_text(node))
        out.append("    links:")
        out.extend(links_text(parts, descriptions, indent="      "))
        out.append("")

    if unknown:
        out.append("# Components of the released assembly that this package does not declare, and")
        out.append("# so cannot place. Each needs a part with a shape - see ../../third_party.")
        out.append("#")
        for product, count in sorted(unknown.items()):
            out.append("#   %-36s x%d" % (product, count))

    text = "\n".join(out).rstrip() + "\n"
    open(assy_path, "w").write(text)
    for path, body in written:
        open(path, "w").write(body)
        print("%s: written" % path)
    print("%s: %d groups, %d parts placed, %d components unplaced" % (assy_path, len(groups), placed, missing))
    for product, count in sorted(unknown.items()):
        print("   unplaced: %-36s x%d" % (product, count))


def wrap(text, width):
    """The narrow wrapping this repository's YAML uses, without a dependency."""
    words, lines, line = text.split(), [], ""
    for word in words:
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        lines.append(line)
    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("package", choices=sorted(PACKAGES), nargs="+")
    args = parser.parse_args()
    for package in args.package:
        generate(package)
