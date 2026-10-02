# PartCAD digital thread for reBot DevArm

This repository carries a [PartCAD](https://partcad.org) package so that the bill
of materials, the manufacturing data and the assembly instructions of the arm are
machine-readable instead of living only in markdown tables.

```
partcad.yaml                              the root package, //pub/robotics/rebot/devarm:
                                          the alloys both arms are cut from, and who supplies them
providers/price_list.csv                  the reference prices the readmes publish, as a price list
providers/price_list.py                   the store that reads it
providers/workshop.py                     what a printer and a machine shop here can make
hardware/reBot_B601_DM/partcad.yaml       every part of the DM (Damiao) variant
hardware/reBot_B601_DM/readme.md          generated from it
hardware/reBot_B601_DM/arm.assy           the arm, part by part, generated from the released STEP
hardware/reBot_B601_DM/arm.md             its parts list, generated
hardware/reBot_B601_DM/gripper.assy       the gripper, likewise
hardware/reBot_B601_DM/power-supply.assy  the power supply enclosure
hardware/reBot_B601_DM/doc/               the projections in the parts lists, and the two documents
                                          the generated readme links to
hardware/reBot_B601_RS/*                  the same for the RS (RobStride) variant
third_party/partcad.yaml                  shapes for the purchased parts, and the interface a Damiao
                                          actuator is bolted to
third_party/vendor/*.step                 the seven purchased parts nobody publishes a model of,
                                          taken out of the released assembly
tools/assy_from_reference.py              writes both arms' .assy files from the released STEP
tools/extract_vendor_parts.py             writes third_party/vendor/ from the same
tools/render-drawings.sh                  renders every drawing, one object at a time
tools/check_parts_against_release.py      is each part file the solid the release assembles?
.github/workflows/partcad.yml             lints, and keeps the generated documents honest
```

Requires PartCAD **0.8.136** or newer.

**Every markdown document in the two hardware folders is generated except two.**
A folder that holds parts and assemblies is a PartCAD package, and its readme is
what PartCAD writes out of the package rather than something maintained beside it:
the prose lives in `docs:` in `partcad.yaml`, the parts list is read out of the
declarations and the assemblies, and `pc render -t readme` writes the file. The two
that are not are the two the generated one links to - what to buy and what it costs
(`doc/buying.md`), and how the power supply goes together
(`doc/power-supply-assembly.md`) - and each says in its first paragraph what would
have to exist for it to be generated too. The four translated readmes are a third
case: they still carry hand-written BOM tables, and replacing those is a job for
somebody who reads those languages.

**The two `.assy` files of each arm are generated too**, from the released STEP
assembly by `tools/assy_from_reference.py`. Do not hand-edit them; the descriptions
are the hand-written part and the generator carries them over.

## Using it

```shell
pip install partcad                     # or: https://partcad.org installers
pc install                              # fetch the packages this one depends on

pc --no-ansi list parts -r              # every part of both variants
pc --no-ansi lint                       # partcad.yaml and every .assy

# rewrite both arms and both grippers from the released STEP assemblies. Needs
# nothing but OCP, which the partcad install brings; the .assy files are
# generated, so this is how they change.
python3 tools/assy_from_reference.py b601-dm b601-rs
python3 tools/extract_vendor_parts.py   # and third_party/vendor/, from the same

# every drawing the parts lists show, one object at a time (see the script for why)
tools/render-drawings.sh

# is each published part file the solid the released assembly holds? (eleven are not)
python3 tools/check_parts_against_release.py

# the bill of materials, aggregated from the assembly
pc --no-ansi bom -P //pub/robotics/rebot/devarm/b601-dm arm

# every generated document of a package: its readme, and one per assembly that
# asks for one
pc --no-ansi render -t readme -P //pub/robotics/rebot/devarm/b601-dm

# who supplies a part, and what a cart would cost
pc --no-ansi supply find //pub/robotics/rebot/devarm/b601-dm:bearing-6803zz
pc --no-ansi supply quote //pub/robotics/rebot/devarm/b601-dm:arm

# the machining routes of every plate whose 'manufacturing:' names a machine
mkdir -p /tmp/routes
pc --no-ansi cam -O /tmp/routes -P //pub/robotics/rebot/devarm/b601-dm

# what a part says about how it is made, and whether it holds up
pc --no-ansi info //pub/robotics/rebot/devarm/b601-dm:flange
pc --no-ansi test -P //pub/robotics/rebot/devarm/b601-dm flange

# the interface check: a part mated to a motor through the one declared interface
pc --no-ansi render -a -t png --view iso -O /tmp/out \
    -P //pub/robotics/rebot/devarm/b601-dm check/motor-mount

# a shape, in the viewer or as a file
pc --no-ansi inspect //pub/robotics/rebot/devarm/third_party:actuator/dm4310
pc --no-ansi export -t stl -O /tmp/out \
    //pub/robotics/rebot/devarm/b601-dm:base-plate
```

Pass `--no-ansi` whenever the output is parsed by a script or an agent, and note
that it routes the logs to stderr. If a change to a `partcad.yaml` does not seem to
be picked up, stop the background daemon that keeps the warm context:
`pc daemon stop`. A shape that does not seem to have changed is the other cache:
`rm -rf ~/.partcad/cache/shapes`. And on a first build of a whole arm - 326 parts -
set `PC_DAEMON_IDLE_TIMEOUT=0`, or the client gives up after 300 seconds while the
daemon is still working. All three are blockers below rather than advice anybody
should need.

## Conventions

* **A name is a name.** Nothing in front of it says how the part is obtained:
  what makes a part is its `manufacturing:` section, what it costs is its
  `vendor:` and `sku:`, and a prefix repeating either is a second place to keep
  in step. (This round removed `printed/`, `cnc/`, `purchased/` and
  `accessory/`.) The one exception is `<part>-blank`, which is not a category
  but a different object: the piece of plate the part is cut from.
* **Quantities are not stored on a part.** A part is declared once and its
  quantity is how many times an assembly places it - which is now the real answer,
  because the assemblies place every component of the released arm. Each part's
  `desc` still carries a quantity in words, and it earns its place by saying where
  the number comes from and where the readme disagrees: "x34 in the DM arm;
  readme.md orders 31+, which is three short".
* ASSY has no quantity field and does not need one: it is written and read by
  machines. Repeated parts are emitted with a Jinja2 loop.
* **Everything a shop is told lives on the part.** `properties:` says what it is
  (material, colour), `tolerance:` how precisely it has to be made,
  `manufacturing:` how it is made - the method, the blank it starts from, and
  the machine, with `toolAxis` saying which way the tool comes at it. Only the
  print settings are still prose in the part's `desc`, because
  `manufacturing: desc:` is refused for every method but `subtractive`.
* **`manufacturing:` only where somebody is expected to make the part.** A part
  that is bought carries `vendor:`/`sku:` and no method; where the method is
  known but the user is expected to buy, that belongs in the description.
* Materials are catalogued objects. The plastics come from
  `//pub/std/manufacturing/material/plastic`; the alloys are catalogued in this
  repository's root `partcad.yaml`.
* **What is shared between the two arms is declared once.** Seven machined and
  printed parts are the same solids in both releases, and so are most of the
  purchased ones. What is *not* shared is a sub-assembly: the two arms place those
  shared parts to different numbers. See "What the two arms share".
* **A purchased part's shape is the vendor's own, out of the released assembly**,
  written to `third_party/vendor/` by `tools/extract_vendor_parts.py`. That is not
  a preference, it is what makes a placement read off that release mean anything -
  see "What it would take to drop `location:`". The size of such a file is not a
  reason to substitute an envelope for it; it is a reason for the package holding it
  to become a package of its own, which is what `//pub/electronics/sbcs/intel` is.
  The exceptions are the four parts no release models - the two power supplies, the
  XT60E connector and the wire - which are envelopes in `third_party/src/`, and the
  three power-supply-enclosure fasteners, which are `type: enrich` of the
  parametric cq-warehouse parts in the public index.
* **An assembly is generated, not written.** Both arms and both grippers come out
  of `tools/assy_from_reference.py`; the descriptions are the hand-written part and
  the generator carries them from the previous revision.
* Anything that could not be entered faithfully is a comment in place, tagged
  `TODO(data)` (a question for the hardware maintainers), `TODO(blocked)` (waits
  on a PartCAD feature) or `TODO(partcad)` (a PartCAD bug).

## Status

Done:

* Every printed, machined and purchased part of **both** variants is declared,
  with its material, its manufacturing method, its tolerance and - for the
  machined ones - the blank it is cut from and the machine it is cut on. 235 parts
  across the three packages.
* **Both arms are assembled where their designers put them.** Both releases are
  STEP files with the product structure intact, so every component carries the
  name of the file it is published as and the transformation that places it;
  `tools/assy_from_reference.py` transcribes that into ASSY. All **326** of the
  DM arm's components are placed and **262 of the RS arm's 263** - the one left
  out is a solid the RS release holds and does not publish as a part. Nothing is
  at the identity location any more.
* **The bill of materials is complete and the counts are the CAD's.** The readme
  gives one arm-wide minimum per fastener ("KA3*12mm, 72+"), which is not a number
  a joint's worth of screws can be ordered from; `pc bom` now gives 326 line items
  for the DM arm with a count per part, and the per-link counts are in the
  assembly. Seven purchased parts that had no shape at all - the gear, the KA3x12
  screw, four dowel pins and an M4x5 set screw - are 80 of those 326, and they now
  have the vendor's own geometry rather than an envelope.
* **Every markdown document but two is generated**, the folder readmes included,
  and so is every drawing in them: 204 projections, one per part and one per
  assembly - **both arms included**, which is new. Every earlier round reported the
  two 326-part arms as the drawings that would not render; they render in a couple
  of minutes each once everything they contain has been drawn, which is what
  `tools/render-drawings.sh` orders them for.
* **Each machined part names its stock.** `method: subtractive` means "what is
  left of something that existed first", and PartCAD asks what that was: 49 blanks,
  22 in the DM package and 27 in the RS one, each derived from the part's own STEP
  file by `src/stock_plate.py` - a plate of exactly the part's thickness, 5 mm
  larger all round - so that `pc test` can check that the part fits it and that the
  blank is bigger somewhere.
* **The machined plates carry the machine they are cut on**, and no longer a
  second declaration of themselves to carry it: `manufacturing: cnc:` with a
  `toolAxis` that says which face the tool comes at. Twenty plates across the two
  arms produce G-code; the rest say `subtractive` and nothing more, because a
  2.5D outline route is not what makes them.
* **Somebody supplies every part.** Two providers in the root package: a store
  reading the readmes' own reference prices (`providers/price_list.csv`), and a
  workshop that says what it can make and refuses to invent a price for it. Until
  they existed, `pc test` failed every part with "No suppliers found".
* **One interface is real, and this round it stopped being measured on one side and
  asserted on the other.** The face a Damiao DM43xx actuator is bolted to - six M3
  on a 27 mm circle around a 14 mm boss - was read off two machined parts that carry
  it; where it sits *on the motor* used to be an assertion, and is now derived from
  the released assembly, agreed on to the third decimal by two independent parts on
  two different actuators. The same arithmetic showed that the part which was
  declared to implement the other side of it does not: see "What it would take to
  drop `location:`".
* **Every purchased part the releases model has the vendor's own geometry.** 34
  declarations in `third_party/` are files taken out of the released assemblies
  rather than envelopes drawn from a datasheet, which is what makes a placement read
  off those releases mean anything at all - a transformation says where a model's
  *origin* goes, so it is only correct for the model it was measured from.

  The four actuators were held out of that for one round, on size: 17 to 25 MB each,
  74 MB together. It cost them their geometry, and `pc test` charged for it - a
  cylinder of the full diameter swallows the steps a real motor has, so two DM4310s
  overlapped each other by 30534 mm³. They are vendor solids now, which is what
  `//pub/electronics/sbcs/intel` does: that package is a repository of its own
  holding one 27.8 MB `nuc12.step`, `type: step`, with its vendor, SKU and product
  URL. The bytes live in the package that needs them, and `//pub/electronics/sbcs`
  reaches them through a `dependencies:` entry rather than carrying them.

  So `third_party/` is the package to split off the day this repository's size
  matters - it already depends on neither arm while both arms depend on it, and
  `vendor/` is 84 MB of a 434 MB working tree whose other 106 MB is the two releases
  themselves. `third_party/README.md` says what that would take: one
  `dependencies:` block.
* Geometry is verified against the release, not by eye, at three levels. Every part
  of the DM gripper was placed by PartCAD and compared against the released
  assembly's own box for it: worst corner 0.008 mm. The whole DM arm was exported
  and compared against all 326 components of the release: five of its six extreme
  faces agree exactly, and the sixth is 2 mm out for a reason that is not this
  repository's - see below. And every published part file was compared against the
  solid the release assembles under the same name
  (`tools/check_parts_against_release.py`).
* **That last check found the release disagreeing with itself**, which is the kind
  of thing this whole exercise is for. It has its own section below.
* `pc lint` passes on every file.

Not done - and why:

* **Every placement is still a `location:` rather than a `connect:`.** They are
  the right numbers now, which is the thing that was missing, but a number says
  where a part ends up and not what holds it there - which is what `pc test`'s
  connectivity check reports about each of them, correctly. See "What it would
  take to drop `location:`", which this round turned from an estimate into a
  measurement.
* **No `how` anywhere.** Assembly instructions attach only to
  `connect`/`connectPorts` nodes, and every node here is still placed with
  `location:`.
* **What is still out of the assembly** is what the released CAD does not model:
  the CAN-USB board, the XT30 separation board, the IEC socket, the AC wiring, the
  M3 nuts and the cable harnesses. Also `2-M7-STATOR`, which the RS release
  assembles and does not publish.
* **The sheet metal chain is still one link short**: the DM links 1, 2, 3 and 5
  are machined *and* formed, which `method: sheet_metal` can express, but the
  flat blank's geometry does not exist and unfolding the finished part is a CAM
  operation this repository cannot perform.
* **`pc test` is not green** - 1586 failures, which is what an arm with real
  placements in it costs a suite of geometric checks that previously had nothing to
  measure. Most of it is worth reading rather than fixing: see "What `pc test`
  finds", where the one number that moved this round is interference, 994 down to
  731, because the four actuators stopped being cylinders.

## What the two arms share

Every STEP file of one arm was compared against every STEP file of the other -
aligned to a common bounding-box corner and matched vertex for vertex, since two
parts with the same volume, bounding box and surface area can still be mirror
images. Seven pairs are the same solid:

| The part | B601 DM | B601 RS |
|---|---|---|
| Gear connector | `02_Gear_Connector.step` | `2-M7-ROTOR.step` |
| Gripper connector A | `02_Gripper_Connector_A.step` | `2-M6-ROTOR.step` |
| Motor rear spacer | `02_Motor_Back_Spacer.step` | `2-Motor_Back_Spacer.step` |
| Rack | `02_Rack.step` | `2-RACK-1M.step` |
| Slider bracket | `02_Slider_Bracket.step` | `2-RAIL-BASE-1.step` |
| Slider extension | `02_Slider_Extension.step` | `2-SLIDER-FIX.step` |
| Rail bracket (printed) | `01_Rail_Bracket.step` | `1-RAIL-BASE-2.step` |

Each is declared once, in the DM package, and aliased into the RS one: one part,
one blank, one route, one line in a quote. Two things fell out of the comparison:

* **It answers an open question.** The RS readme lists `2-M7-STATOR.step` for
  "gripper connector B" and no such file exists; `2-M7-ROTOR.step` does, and it
  is the DM arm's gear connector vertex for vertex.
* **So are most of the purchased parts, and now provably.** Where both releases
  model a bought part, the two models are almost always the same solid in the same
  frame - the same box and the same volume to a decimal - so the thrust bearing,
  the rail, its carriages, the silicone pad, the gear and the KA3x12 and KM3x7
  screws are one declaration each, aliased into both arms. Two exceptions, and both
  are findings: the two releases model the **6803ZZ** differently (the DM release a
  plain 26 mm bearing, the RS release a flanged 28 mm one, a quarter larger by
  volume) under one readme row and one SKU; and the RS release's KM3x7 differs from
  the DM's by 3% of its volume, which is two models of one product rather than two
  products.

**The gripper slide is not one sub-assembly, and this round is when that stopped
being a guess.** Those seven parts plus the rail, its two carriages and the gear
are the whole of the slide, and the two arms grip with the same parts - but the
two releases do not place them to the same numbers. Measured from the slider
bracket, which both arms have exactly one of:

| | B601 DM | B601 RS |
|---|---|---|
| Carriages | ±14.300 | ±14.800 |
| Racks | ±4.175 | ±4.125 |
| Slider extensions | ±0.119 | ±0.069 |

Every one of these parts is at the same X in both releases, to four decimals, and
at a different Z. In Y the two are related by a reflection for some parts and by a
289 mm shift for others, so this is not one arrangement expressed in two frames.
The groupings are not the same set of parts either: the RS release puts that arm's
wrist motor inside its gripper and the DM release keeps it in link 6.

So each arm has a `gripper` of its own over one set of parts, and the shared
`gripper/slide` an earlier round declared is gone. A sub-assembly with one set of
baked placements would have been wrong for one of the two arms, and nothing would
have said so. That is the clearest argument for ports this repository has produced:
a placement *derived* from the parts cannot disagree with itself, while two copied
placements can, and half a millimetre is exactly the size of disagreement nobody
notices in a render.

What is **not** shared, though it looks it: the two arms' fingers, their limit
stops and their power supply sliding covers each have the same part count and
different geometry, and the DM's own left/right link pairs are neither identical
nor mirror images of one another. A comparison by volume and bounding box says
all four of those are the same part, which is why the check is by vertex.

## What the released CAD says that the readme does not

**The releases are not anonymous solids: they are labelled assemblies.** An
earlier round read them by grouping solids by bounding box, because that is what a
STEP file looks like through `pc bom` on an imported assembly. Read through
OpenCASCADE's XCAF layer instead, each one is a product structure with every name
and every transformation in it - 326 components in the DM release, 263 in the RS
one, grouped into a base, five or six links and a gripper, and each component
named after the file that part is published as (`03_Link1`, `02_FLANGE`,
`KM3-12`). So the placements did not have to be recovered or guessed: they are
data, and `tools/assy_from_reference.py` transcribes them.

That also makes the readme's own numbers checkable. **Every fastener count in both
readmes is a minimum with a `+` on it, and the CAD gives the real number** - which
is below the readme's minimum in some rows and above it in others:

| | readme | released CAD |
|---|---|---|
| DM KM3x7 | 76+ | 64 |
| DM KM3x9 | 31+ | **34** |
| DM KM3x12 | 30+ | 22 |
| DM KM3x16 | 34+ | 26 |
| DM KM3x8 | 31+ | 5 |
| DM KA3x12 | 72+ | 60 |
| DM HM3x6 | 16+ | 8 |
| DM HM3x12 | 14+ | 7 |
| DM HM3x25 | 14+ | 6, and 26 mm long rather than 25 |
| RS HM3x8 | 60+ | 45 |
| RS HM3x30 | 16+ | 8 |
| RS KM3x7 | 80+ | 58 |
| RS KM3x16 | 8+ | **none at all** |
| RS HM3x26 | 6+ | **none at all** |
| RS 6803ZZ | 3 | 2 |

`KM3x9` matters most of those: the readme's minimum is three screws short of what
the released arm holds, so somebody ordering to the readme cannot finish. Two rows
of the RS readme order a fastener its own CAD does not use at all.

Three other things the structure settles:

* **`2-RSM1-STATOR-2.step` and `2-SPACE-M4-STATOR.step`** were in the RS
  repository and in no BOM table. The CAD says what they are and how many: one
  95 x 95 x 8 mm plate in the base, and one 63 mm spacer 5.5 mm thick in link 3.
  Both are declared now.
* **The DM repository's second STEP file is the RS arm.**
  `reBot_B601_DM_v1.1_20260625.step` opens as `reBot_B601_RS_v1.0_20260625` with
  the RS release's group names, and it is not byte-identical to the RS folder's own
  copy either (262 components against 263). The package reads the April file,
  which is the DM arm, so nothing here is wrong - but that file is mislabelled.
* **The dowel pins are four sizes, and the readme lists two of them wrongly.** The
  DM readme orders "M4*8mm" and "M4*12mm"; the CAD holds 4x7 (x6), 4x10 (x6),
  4x14 (x3) and 3x8 (x2).

The measurements an earlier round took by bounding box still stand, and are what
the envelopes in `third_party` were drawn from:

| Readme | Released CAD | Note |
|---|---|---|
| DM4310 x4, "L56 W56 H46" | 4 solids, 69.5 x 57.0 x 57.0 | Every dimension disagrees with the listing |
| DM4340P x3, no dimensions | 3 solids, 57.0 x 57.0 x 56.6 | Now the declared envelope |
| RS00 x4, no dimensions | 4 solids, 57.1 x 57.0 x 52.0 | Now the declared envelope |
| RS06 x3, no dimensions | 3 solids, 84.5-87.3 wide x 50.5 | Drawn three slightly different ways |
| 6803ZZ x3 | 3 solids, 26.0 x 26.0 x 5.0 | Confirms the BOM |
| 6707ZZ x1 | 1 solid, 45.3 x 44.8 x 5.0 | Confirms the BOM |
| AXK5578 x1 (3 mm thick) | 1 solid, 77.7 x 77.7 x 5.0 | A 5 mm stack: the two AS5578 washers the BOM does not order |
| MGN9 rail, 170 mm | 170.0 x 9.0 x **6.5** | The MGN9 profile is 9 x 10; the model is not it |
| Silicone pad x1 (RS) | 4 solids, 30.0 x 9.0 x 2.0 | The RS arm models four |
| KM3x7 x76+, KM3x12 x30+, KM3x9 x31+, KM3x16 x34+ | 64, 82, 34, 26 heads of Ø6 | Exact counts, and two of them are nowhere near the readme's |

The fastener counts are the valuable part: they are what
`arm.assy` needs to place screws joint by joint, and they are already in the
repository.

One measurement from this round belongs beside them, because it is the first one
that produced geometry rather than a number: the face a DM43xx actuator is bolted
to, read off two machined parts that carry it (six holes on a circle of radius
13.5, around a bore of radius 7) and cross-checked against the 30 mm output boss
the envelope already declared. It is an interface now - see "What it would take
to drop `location:`".

## Where the release disagrees with itself

Each arm is published as one download, and that download holds **two different
kinds of thing**:

1. **One file per part**, under `3D_Printed_Parts/` and `Metal_Parts/`. This is
   what every part of these packages is declared from, and what somebody prints or
   sends to a shop.
2. **One file for the whole arm** - `reBot_B601_DM_v1.1_20260425.step` - which is
   an assembly holding *its own copy* of each of those solids, plus the placement
   of every one of them.

Nothing had ever compared the two, because until this round nothing needed to. Now
both matter at once: `arm.assy` takes its **placements** from (2) and its
**geometry** from (1), so a part whose two copies differ is a part placed where the
assembly says with geometry that belongs somewhere else.
`tools/check_parts_against_release.py` compares them part by part, by bounding box
and by volume. 71 part files are also assembled. **Eleven of them differ.**

### Two files are swapped

The release assembles a product it calls `01_Lower_Arm_Cover` on the lower arm
(z 109.200..136.929) and one it calls `01_Upper_Arm_Cover` on the upper
(z 170.860..195.800). The published files are the other way round:

| | vertices | volume | identical to |
|---|---|---|---|
| released `01_Lower_Arm_Cover` | 1848 | 17896.0 mm³ | published `01_Upper_Arm_Cover.step` |
| published `01_Upper_Arm_Cover.step` | 1848 | 17896.0 mm³ | released `01_Lower_Arm_Cover` |
| released `01_Upper_Arm_Cover` | 1644 | 10754.0 mm³ | — |
| published `01_Lower_Arm_Cover.step` | 1644 | 10776.0 mm³ | — (22 mm³ apart) |

One of those pairs is **vertex for vertex identical** - all 1848, compared relative
to each shape's own bounding-box corner so that neither frame matters. That is not
a coincidence of volume; it is the same solid. The other pair is the same part one
revision apart.

So the two file names are swapped. Left alone it would put the upper cover where
the lower belongs and the lower where the upper belongs - and since the two are a
similar size, nothing about the result looks wrong. Each part here is therefore
declared from the file whose *geometry* belongs where the part goes, and
`tools/assy_from_reference.py` matches these two by the release's name rather than
by the file's.

### One is why the assembled arm is 2 mm bigger than the release

| | thickness | z | volume |
|---|---|---|---|
| released `01_BASE_Plate` | 14.75 mm | -17.300..-3.300 | 385497.2 mm³ |
| published `01_BASE_Plate.step` | 14.00 mm | -15.300..-1.300 | 388611.0 mm³ |

0.75 mm thinner, 2 mm along its own axis, 3114 mm³ apart. That is the whole of the
difference between the arm PartCAD builds (z 1.300..285.500) and the release
(z 3.300..285.500): the other five extreme faces agree exactly. It is not corrected
here, because correcting it would mean choosing which copy is right.

What it means for a builder: printing the published file gives a base plate that is
not the plate the released assembly was put together with.

### Eight differ inside the same outline

Same bounding box, different volume - which reads as a revision: a fillet added, a
hole moved, a boss changed.

| part file | difference |
|---|---|
| `02_Wrist_Bracket.step` | 680.7 mm³ |
| `01_Arm_Handle.step` | 406.6 mm³ |
| `01_Joint6_7_Cable Restraint_A.step` | 169.5 mm³ |
| `01_Lower_Arm_Limit.step` | 117.7 mm³ |
| `01_Joint6_7_Cable Restraint_B.step` | 18.4 mm³ |
| `01_Motor_Cover.step` | 4.0 mm³ |
| RS `2-RSM-ROTOR-R.step` | 2049.7 mm³ |
| `01_Upper_Arm_Limit.step` | 1364.2 mm³, and 6.05 mm out of position |

### What to do about it

Nothing here decides which copy is authoritative - that is a question for whoever
publishes the release, and it is in the data questions at the end of this file. What
has changed is that the question is now **answerable in a minute** rather than
invisible: the check is a script, so the next release can be audited before anybody
builds from it.

The two most likely explanations, and they are not exclusive: the part files and
the assembly were exported at different times, so one set is stale; or the covers
were renamed at some point and the assembly kept the old names. The covers are the
one case where the evidence settles it - the geometry says which is which, and the
release's own placements agree with the geometry.

## What has landed since the last round

Between 0.8.124 and 0.8.136, four things this repository had reported as blockers
were fixed, and two of them are why this round reached as far as it did:

| Was | Now (0.8.136) |
|---|---|
| **An alias carried none of its source's `implements:`**, so every purchased part was unmatable through the name its arm uses for it - and no joint against a motor could be written in an arm assembly at all | 0.8.130 gives an alias its source's ports. `check/motor-mount` names this package's own `actuator-dm4340p` now, and the mate lands the spacer's face on the motor's output face to three decimals |
| A cached shape outlived the `.assy` that produced it, so a render or an export showed the old one with nothing said about it | 0.8.132 keys a composite on its inputs. Two of this round's geometric checks were wrong once because of the old behaviour |
| `pc render`/`pc export` needed `-p` to create the directory a slash-named object implies | 0.8.125 always creates it, and the flag is gone. This repository's commands and `tools/render-drawings.sh` no longer pass it |
| A generated readme linked every object's picture to a `<name>.<type>` file, whether or not such a file exists | Linked only where there is a file to follow. Both these folders are mostly aliases into `third_party/`, and an alias has no file of its own - so 30-odd links that resolved to nothing relative to the folder they were written in are gone from each readme |
| An aliased part's row in a generated parts list read `Alias to gear/m1-16t-b6 from //pub/robotics/rebot/devarm/third_party` | It reads *"Module 1, 16 tooth, 6 mm bore gear - what drives the two gripper racks"*. Nearly every row of both arms is an alias into `third_party/` or into the other arm, so this is most of the rows, and it is the difference between a parts list a person can order from and a map of where the declarations live |
| A part could not name the offer it is bought from | It always could - `url:` is in the schema beside `vendor`/`sku`, and `//pub/electronics/sbcs/intel` uses it for the product page. Nothing rendered it, which is contribution 7 below: a SKU in a generated list is now a link to the page the part is ordered from |

0.8.127 also changed something this repository has to answer for rather than
benefit from: a made part's **stock is procured** now, so `pc test` asks who
supplies each of the 49 blanks. That is a fairer question than it used to ask, and
the answer is a gap in the published data - see blocker 11.

Between 0.8.91 and 0.8.124 the manufacturing side of PartCAD was rebuilt, and
most of what this repository had to say about it became expressible:

| Was | Now |
|---|---|
| A `cam:` section on the part, and no way to say what a subtractive part is cut *from* | The job moved into `manufacturing:`, beside the method it belongs to: `source:` names the blank, and `cnc:`/`laser:`/`drill:` names the machine. `pc test` checks that the part fits the blank and that the blank is bigger somewhere |
| A plate had to be declared twice - once as a part, once laid flat as a machining job - because `cam:` on an alias was dropped | `toolAxis:` says which way the tool comes at the part, so the part carries its own machine. The 20 duplicate declarations are gone, and so is the `offset:` trick that laid each one flat |
| `offset:` moved the label and not the geometry | Fixed upstream, and better than the fix this repository sent: the transform is applied to the geometry with `BRepBuilderAPI_Transform` rather than to a build123d frame |
| Nothing could quote anything | `providers:` in a package, `suppliers:` per package, and `pc supply find`/`quote` over them. This repository's two providers are 120 lines and a CSV |

### What this round contributed back to PartCAD

Eight changes, each found by using it on this repository:

1. **An alias did not inherit its source's tolerance.** An `alias` is built by a
   factory that accepts no `tolerance:` field, so the field the source declared
   never reached it: `pc test` failed the alias of a machined part with "the part
   type 'alias' does not accept one" about a part whose resolved configuration
   states 0.02. It reads the resolved configuration now. This is what made the
   seven shared parts above declarable once instead of twice.
2. **An alias resolved its source's references in the wrong package.** The
   inherited `manufacturing: source:` names the blank *the source's* package
   declares, and it was looked up in the package the alias lives in - so an
   aliased machined part reported the blank of somebody else's part as missing.
   Resolved against the declaring package now, which is the rule
   `/pc:add-interfaces` already states for an enriched part's `implements:`.
3. **`pc supply find` crashed on every run**: the CLI passed the quality of
   service to `Context.find_suppliers()`, which takes one argument. It belongs to
   the cart, which is how `pc supply quote` does it.
4. **Two keys the code reads were missing from the schema**, so a package using
   either got a `pc lint` warning about a key that works: `providers.*.path` (the
   script a provider is implemented by, when it is not named after the provider)
   and `docs.name` (the title of a generated document).
5. **An implementation `path:` that is not a Python script is refused, with a
   sentence saying what `path:` is and what does set the output name.** It used to
   be compiled: `render: readme: path: readme.md`, written to make PartCAD produce
   a lowercase readme, made PartCAD execute this repository's readme as the readme
   renderer and report "leading zeros in decimal integer literals are not permitted
   (readme.md, line 20)" for every object in the package. Line 20 held a part
   number. See blocker 8 for what is still wanted: a way to set the name.
6. **The bill of materials carries what a published parts list carries** - the
   picture, the material, the method, the process, the tolerance, the vendor, the
   SKU and the file - which is the change this repository asked for last round,
   rebased onto the new `manufacturing:` and reading `manufacturing: desc:` where
   it used to read a section of its own.
7. **A SKU in a generated parts list links to the page the part is ordered
   from.** `url:` was already in the schema beside `vendor`/`sku` and already
   used by `//pub/electronics/sbcs/intel`; nothing rendered it. The four
   renderers now carry a link cell, so the generated list reaches the offer the
   way the published markdown table it replaces did.
8. **A solid with ten or more internal voids was reported as a surface
   model.** The `shell` check reads a part's topology straight off the BREP
   bytes - no CAD kernel, no sandbox - by finding each record's sub-shape list,
   "the one line in a record that ends with `*`". That list is not always one
   line: `TopTools_ShapeSet` writes ten references per line and wraps. A solid
   is bounded by one shell per cavity as well as by its outer one, so eleven
   cavities make eleven references, the list wraps, and reading only the closing
   line saw one shell owned and called the other ten free. Two of this
   repository's four actuators are exactly that - the RS00 is one solid bounded
   by eleven shells - and both failed with *"The shape is a skin rather than a
   body: 10 shell(s) that no solid bounds itself with"*, which is the opposite
   of what they are. The whole list is read now, as the run of lines that ends
   on the `*` and holds nothing but references; a fixture with eleven voids
   keeps it honest.

   Worth saying plainly, because it is the second time this round a check
   earned its keep by being wrong: a false failure here is expensive in a
   particular way. The verdict is cached, the message names a cause that cannot
   be acted on, and the obvious response - re-export the vendor's STEP, sew the
   faces, give up on the part - is work on geometry that was correct.

### What `pc test` finds

`pc test -r` over the whole tree, from an empty test cache, reports **1586
failures**: 731 interference, 728 connectivity, 66 manufacturability, 61 cam. That
is not a regression - it is a suite of geometric checks finally having something
to measure, since over an assembly at the identity location they had nothing to
say. What they say is worth reading one group at a time.

The one number that **moved** this round is interference, from 994 to 731, and it
moved because the four actuators stopped being cylinders. That is the whole of
what paying the 74 MB bought, measured:

| | before | after |
|---|---|---|
| interference findings | 994 | **731** |
| of them involving an actuator | 291 | **141** |
| largest structure-against-structure finding outside the power supply | 30534 mm³, `actuator-dm4310` against another `actuator-dm4310` | **662 mm³**, a flange against link 3's bracket |
| `shell` findings | - | 8, then **0** (see contribution 8) |

1. **Connectivity, 728: every link of both arms placed by coordinates.** The check
   is right, it is the repository's own open item, and it is what "What it would
   take to drop `location:`" is about. One failure per link, so the number is the
   size of the arms rather than the size of the problem.

2. **Interference, 731, and nine tenths of it is expected.** A screw in a tapped
   hole shares volume with the part it is screwed into, and so does a dowel pin in
   its bore and a bearing in an interference fit; the released assembly models all
   three the way a designer does. 609 of the 731 are a fastener against the thing it
   fastens and 45 are two fasteners meeting in a joint. Separating those from real
   clashes needs the joints declared: a `connect:` through a threaded interface is
   what would let PartCAD know that an overlap there is the point.

   That leaves **77 that are structure against structure**, and they are now a list
   worth reading rather than a list of measurement artifacts. The five largest are
   all in the **power supply enclosure** - 5900 to 11800 mm³ between the two cover
   shells, the supply and the slider - which is the one assembly here whose
   placements are hand-written guesses rather than a release's, so those five are
   this repository's to answer for. Everything outside it is small: 662 mm³ for a
   flange against link 3's bracket, 517 for link 2 against its own limit stop, 383
   for a silicone pad against an arm limit. The actuators appear at 188 to 241 mm³,
   against cable restraints and back extensions, which is the size an interference
   fit is.

   Last round the top of this list was `actuator-dm4310` against another
   `actuator-dm4310` by 30534 mm³ and `actuator-rs06` against `base-link` by 14815 -
   two full-diameter cylinders standing in for motors that have steps and recesses.
   Those findings are gone, which is the point: the biggest numbers in a geometric
   report should be about the design, and until this round they were about the
   stand-ins.

3. **CAM, 61: a subtractive part that PartCAD cannot route fails the check.**
   Naming no machine means a CNC router, so every `subtractive` part is asked for a
   2.5D route - and the parts that fail are genuinely subtractive and genuinely not
   2.5D: turned discs, parts cut from bar, the machined-and-formed links. They fail
   with `No 'diameter' is configured`, which points at a declaration that would not
   help if it were there.

   What would fix it: the check applying only where a machine is *named*. "Naming
   none means CNC" is a sensible default for a route somebody asked for, and a
   different thing from asking for one.

4. **Manufacturability, 66, and only seven of them are a gap in the data.** Seven
   parts can be neither bought nor made: three power-supply-enclosure fasteners
   whose readme rows carry "/" where the link should be, two more whose listings are
   missing, the M4x5 set screw the readme does not list at all, the 3 mm dowel pin
   with no listing, and the two XT30 connector bodies, which are only sold as part
   of a harness. Every other fastener of both arms carries the vendor and SKU its
   own readme row links.

   The remaining 47 lines are **not** seven parts' worth of cascade: they are 39
   distinct parts, named by the six assemblies that contain them, and nearly all of
   them failed the **CAM** check rather than anything to do with being obtainable.
   An assembly's manufacturability check re-runs every check on each object of its
   supply bill of materials and reports whatever failed as `Non-manufacturable part
   '<name>' is referenced` - so a turned disc with no 2.5D route is reported to the
   reader of a bill of materials as a part nobody can make. See blocker 11.

   This check earned its keep twice over this round: it is what found five
   accessory mounts with no tolerance and four countersunk screws whose SKU I had
   wrongly left out, both fixed here.

5. **A cached verdict loses its reason, and survives a change that should
   invalidate it.** 15 of this run's lines are `Failed test result loaded from
   cache` instead of what failed - which happens *within* one run, for an object
   tested twice, so a package's output is partly that sentence. And the key does not
   cover the declaration: changing a part from `alias` to `enrich` - which changes
   the verdict - produced the cached one.

   **This cost a false finding in this file, and the correction is the useful
   part.** Last round I reported that `manufacturable: false` fails to exempt a
   blank from the supply question, and that all 49 blanks therefore failed with
   "Cannot be purchased or manufactured". They do not. The flag works: every blank
   passes, tested on its own and in a run with the test cache cleared. What I had
   read was a cached failure from before the flag was added, and the message a
   cached failure carries says nothing about when it was decided. A stale verdict
   that reports a pass as a failure is how a tool gets a feature request it does
   not need.

Three families of failure that were here last round are **gone**, all three fixed
upstream from this repository's data: an aliased machined part no longer fails for
having no tolerance, nor for its blank being looked up in the wrong package, and a
solid with ten or more internal cavities is no longer called a surface model.

## What it would take to drop `location:`

The `/pc:gen-assembly` skill is written for an assembly whose parts are already in
the right places and converts those coordinates into joints. Last round this
repository was one step before that - every `location:` was the identity location,
so there was nothing to convert and nothing to check a conversion against. **That
step is done**: both arms now carry the placements their releases give them, so the
skill's actual subject matter applies for the first time.

Four of its rules paid off, and one of them is now the thing this repository is
built on:

* **"Do not predict a mate; try it."** This is what produced the round's best
  result. The released assembly places four DM4310s and four front spacers on them,
  and the spacer's own port was measured off the spacer's own STEP file - so the
  port on the *motor* is not something to assert, it is what those two placements
  leave: `P_motor = M⁻¹ · S · P_part · flip⁻¹`. Worked out for every
  (part, motor) pair in the release, two independent spacers on two different
  actuators give the same frame to the third decimal, twice over:

  | | derived port, in the vendor model's own frame | agreed by |
  |---|---|---|
  | DM4310 | `[[0, 0, 50.5], [1, 0, 0], 180]` | 2 spacers on 2 actuators |
  | DM4340P | `[[0, -11, 0], [1, 0, 0], 90]` | 2 spacers on 2 actuators |

  Both are declared now, and neither is a number anybody typed from a datasheet.

* **The same arithmetic falsified a declaration.** `02_FLANGE` carries the same
  six-hole pattern as the front spacer, and last round it was declared as
  implementing the same interface on that basis. Run through the release, the
  motor-side frame it would have to meet comes out **10.6 mm clear of the actuator
  model's own end face** - repeatably, the same number for two flanges on two
  different DM4340Ps - where the spacer's comes out exactly on it. So the flange
  does not sit on the actuator: it is the *rear* flange, as its own description
  always said, and something 10.6 mm thick is between the two. Its `implements:` is
  gone and the measurement is recorded beside it. A pattern that matches is not a
  joint.

* **"Group what repeats into sub-assemblies."** The gripper is a sub-assembly in
  each arm, and the parts list proves the regrouping moved nothing.

* **"When a part has no port where the joint is, leave it on coordinates and say
  why."** Still the situation for every joint but the four the interface above
  covers.

**A placement is only worth as much as the model it was measured from, and PartCAD
does not know which model that was.** This is the round's other finding, and it was
expensive. Transcribing the release's transformations produced an assembly that was
exact for every part whose geometry *is* that release's own file - checked part by
part against the release, worst corner error 0.008 mm - and wrong for every part
this repository had substituted: an envelope drawn from a datasheet, an ISO fastener
generated by `//pub/std/metric/cqwarehouse`. A transformation says where a model's
origin goes, and two models of one product do not share an origin. The clearest
case was the MGN9 rail: 170 mm long, laid along X where the release has it along Z,
170 mm out of place. 177 of the DM arm's 326 components were substitutes.

The fix was to stop substituting. `tools/extract_vendor_parts.py` writes each
purchased part out of the released assembly on its own, in its own coordinates, and
`third_party/` declares 30 parts from those files instead of from a script - the
bearings, the rail, its carriages, the pad, the connectors, the gear, the dowel
pins and fourteen screws. Two things did not follow that route:

* **The four actuators.** Their vendor models are 17 to 25 MB each, 74 MB for the
  four, which is not a thing to add to a repository for a shape that is a cylinder
  to everything downstream. They stay envelopes - and what the released models give
  them instead is the vendor's own *frame*: each is now a cylinder of the measured
  diameter with an `offset:` that puts it exactly where the release's model sits.
  That is the half of it a placement needs.
* **Three fasteners of the power supply enclosure**, which the releases do not
  model at all. They stay `enrich` of the ISO catalogue, which is the right way to
  declare a screw nobody has placed.

What this wants from PartCAD is a way for a part to say which model a placement was
measured against - or, better, for an assembly to. Nothing in a `location:` records
it, so substituting a shape silently moves every part placed relative to it, and the
only symptom is a render that looks slightly wrong.

**The thing that was blocking it is fixed.** An alias carried none of its source's
`implements:`, so its ports were empty and a `connect:` naming them silently placed
nothing - and since every purchased part is aliased into the variant that uses it,
no joint against a motor could be written in an arm assembly at all.
PartCAD 0.8.130 fixed that, and `pc info` on this package's own
`actuator-dm4340p` now reports the derived port:

```
Ports: {'interfaces': {'...:actuator/dm43xx-output': {'output': {'face': 'output-face'}}},
        'ports': {'output-face': {'location': [[0.0, -11.0, 0.0], [1.0, 0.0, 0.0], 90.0], ...
```

`check/motor-mount` is the proof end to end. It used to have to name the actuator in
the package that *declares* it, which is the one thing an arm assembly cannot do;
it names this package's alias now, and the mate puts the spacer's face at y =
-11.000 - the motor's output face, exactly, no gap and no overlap. So the chain is
whole: a pattern measured off a machined part, a motor-side frame derived from the
released assembly, a port on an alias, a `connect:` that lands where the release
puts it.

**What is left is the work rather than the blocker:**

1. **The other joints need the same derivation.** It is a script now rather than a
   research project: for each machined part that meets a purchased one, measure the
   pattern on the machined side and let the release supply the other. The joint
   families, in order of how many placements each would retire: a screw in a tapped
   hole (271 across both arms), a bearing in its housing (6), a carriage on its rail
   (4), a rack against the pinion (4).
2. **A `connect:` has to name the node it connects to**, and the pairings cross the
   link groups the releases are organized into - the Link1 front spacer bolts to an
   actuator the release puts in Link2. Whether an ASSY node in one group can be
   named from another is the next thing to find out; if it cannot, the groups have
   to be reorganized around the joints rather than around the CAD's folders.
3. **Each mate has to be checked against the placement it replaces**, which is
   section 6 of the skill and is now straightforward: the release's transformation
   is the answer the `connect:` has to reproduce, and
   `tools/check_parts_against_release.py` is the shape such a check takes.

## Blockers



1. **Nothing records which model a placement was measured against.** A
   `location:` is a transformation of a part's own origin, so it is only correct
   with the shape it was read from - and swapping that shape for another model of
   the same product silently moves the part. This round's arms are transcribed from
   the released assemblies, so every one of their 588 placements has this property,
   and the symptom of getting it wrong was a 170 mm rail lying along the wrong axis
   with nothing said about it. Working around it meant replacing 30 declarations so
   that the shape PartCAD builds is the shape the placement was read from. What
   would help: a way for a part to declare the frame its shape is expected in, or
   for an assembly to declare the model its placements came from, so that
   substituting one is an error rather than a silent move.


2. **A build stops making progress, and the daemon goes idle without saying
   anything.** It is a cold-cache problem rather than anything about the objects,
   which is why it took so long to characterize - everything named below builds
   perfectly once the shapes it needs are in the cache:

   * `pc render -t svg -P <package>` renders 82 of a package's 101 parts and then
     stops. Named one at a time the same 19 render in a second or two each, which
     is why `tools/render-drawings.sh` is a loop rather than a command.
   * `pc export -t step -a arm` reports `Building these sub-assemblies first:
     ...:gripper`, builds the gripper, and then never returns. After the same
     shapes have been built some other way it exports the 326-part arm in seconds.

   In both cases the daemon logs nothing after its last success, uses no CPU, and
   the client waits. Whatever the cause, the reportable part is the silence: a
   build that has stopped should say so. A separate limit compounds it - the client
   gives up on any single call after 300 s ("The PartCAD service stopped
   responding") while the daemon is still working, so a first build of a 326-part
   assembly would fail on a stopwatch even without this. `PC_DAEMON_IDLE_TIMEOUT=0`
   lifts that one.


3. **A subtractive part that is not 2.5D cannot pass `pc test`** - see "What
   `pc test` finds".


4. **A part's material is invisible to whoever would make it.** The supply path
   reads the `material` *object-type parameter*, which the types whose shape
   comes out of a file refuse; such a part states its material under
   `properties:` instead, and nothing reads it. So every `step` part warns "has
   no 'material'" once per run, and a manufacturer provider is asked "can you
   make this out of nothing" and answers yes - to a bearing as readily as to a
   bracket.

   Reading `properties:` there is three lines, and doing it immediately raises
   the question that has to be settled with it: a provider's capabilities are
   compared to the material as plain strings, so a package's own `pla` and
   `//pub/std/manufacturing/material/plastic:pla` are different materials.
   `examples/produce_assembly_assy` fails the moment the material is read, for
   exactly that reason. Hence a report rather than a patch.


5. **`manufacturing: desc:` is refused for every method but `subtractive`.** It
   is grouped with the keys that describe a cut, which is right for a route and
   leaves an additive part with nowhere to say how it is printed - so the nozzle,
   the layer height and the infill of 39 parts are prose in each part's `desc`,
   where the generated parts list shows them in the Description column rather
   than in the Process one.


6. **A cached test verdict loses its reason and outlives the declaration** - see
   "What `pc test` finds".


7. **A repository plugin's downloads do not go through the proxy** (unchanged,
   and not re-tested this round). `//pub/std/metric/bosl2` answers 403. It no
   longer matters for the bearings or the gear - those are the vendor's own solids
   now, which is a better answer than a generated one - but it is still what stops
   a parametric fastener catalogue from being usable here.


8. **A package document's file name is not configurable.** `path:` under a
   `render:` file type is the path of an *implementation* of that file type, so
   `render: readme: path: readme.md` made PartCAD try to run this folder's readme
   as the readme renderer. That half is fixed upstream this round - the path is
   refused now, with a sentence saying what `path:` is - but the thing it was
   reaching for still does not exist: what is configurable is `prefix`,
   `extension` and `output_dir`, and the basename is `README.md`. So the DM
   folder's `readme.md`, which was the vendor's spelling, is `README.md`. A
   folder whose readme is lowercase is not unusual, and this one's was.


9. **Importing a released STEP assembly does not finish.** Both arms' releases
   were declared as `type: step` objects (`reference/arm-v1.1`,
   `reference/arm-v1.0`) so that PartCAD could read the file the placements come
   from. `pc render` of one decomposes 296 of the file's 326 components into
   temporary STEP files and then stalls - on the same component every time, with
   the daemon idle and nothing logged - so `pc render -P <package>` for the whole
   package never finishes either. The two declarations are gone, and the file is
   read by `tools/assy_from_reference.py` instead, which takes about a minute.


10. **Telemetry retries an unreachable endpoint in the daemon's hot path.** Where
    outbound HTTPS is filtered - a CI runner, an agent sandbox - the daemon's log
    fills with `Tunnel connection failed: 403 Forbidden` retry rounds.
    `PC_TELEMETRY_TYPE=none` turns it off, and something that cannot reach its
    collector should stop trying by itself.

11. **An assembly reports every failing part as "non-manufacturable", whatever
    failed.** An assembly's manufacturability check re-runs *all* the checks on
    each object of its supply bill of materials, and reports any failure as
    `Non-manufacturable part '<name>' is referenced`. So the 47 such lines in this
    round's run are 41 distinct parts that failed the **CAM** check, or - until
    the fix above - the **shell** one. Both arms are therefore described as
    containing parts nobody can make, about parts whose vendor, SKU and process
    are all declared and whose actual complaint is that a 2.5D route could not be
    generated for a turned disc.

    It is a reporting problem rather than a wrong verdict: the assembly *did*
    fail, and a reader who goes looking finds the part's own failure. But the
    sentence is the one a bill of materials is read for, and it names the one
    thing that is not wrong. Naming the check that failed would be enough.

    A correction to what this file said last round: the claim that
    `manufacturable: false` does not exempt a blank from the supply question was
    **wrong**. It does - all 49 blanks pass, tested on their own and in a cleared
    cache. What produced the failures I reported was a stale cached verdict from
    before the flag was added, which is blocker 6 and is the second time this
    round it has cost a false finding.

    What this repository still cannot answer is who supplies the *material*: the
    readme prices all the machined parts at about $250 together, material and
    machining in one figure, and names no metals supplier. That is a gap in the
    published data, not in PartCAD.

## Wish list

Four of last round's items are **done** and are the reason this round got as far as
it did: ports on an alias (0.8.130, which is what lets an arm mate a purchased part
through its own name for it), a cache key that covers the declaration (0.8.132), a
`url:` beside `vendor`/`sku` - which turns out to have been there all along, and is
what `//pub/electronics/sbcs/intel` puts its product page in - and a generated
parts list that *shows* that `url:`, which is contribution 7 above.

That last one takes half of `doc/buying.md`, the one hand-written table left in
each variant package, and the half it takes is the half that goes stale: the link
to the offer. What is left there is a reference price per part, which the
generated list still has no column for - and arguably should not, since
`providers/price_list.csv` and `pc supply quote` are the answer to "what does this
cost" and a figure typed into a document is not. So `buying.md` shrinks rather
than disappears, and the rows it keeps are the ones the readme prices by hand.

What is left, in the order that unblocks the most work here:

1. **Read a labelled STEP assembly into a package.** Still the biggest one. Both
   releases here are STEP files with their product structure intact: names, instance
   counts and transformations, all of it data. Reading it took 120 lines of OCP
   against `STEPCAFControl_Reader` and XCAF (`tools/assy_from_reference.py`), and it
   produced two complete assemblies, every fastener count in both arms, and the
   grouping into base and links. What PartCAD offers for the same file is
   `type: step`, which flattens it to solids named `Link4:1_solid27` - and does not
   finish (blocker 9). A `pc import assembly` that emitted an `.assy` and a part per
   component would be the single most valuable thing in this list for any repository
   whose CAD comes from somebody else's release.
2. **Some record of which model a placement was measured against** (blocker 1).
3. **A build that says so when it stops** (blocker 2).
4. **The `cam` check applying only where a machine is named** (blocker 3), so that
   "this part is machined" and "this part has a 2.5D route" stop being the same
   statement. It is worth two places in this list rather than one, because it is
   also most of blocker 11: a part that fails only the CAM check is what an
   assembly reports as non-manufacturable.
5. **`properties.material` read by the supply path**, with the material-identity
   question settled (blocker 4).
6. **An assembly's manufacturability failure naming the check that failed**
   (blocker 11).
7. **A place for an additive part's settings** (blocker 5).
9. **A cached failure that keeps its reason** (blocker 6), **a field that sets a
   generated document's file name** (blocker 8), and **an import of a big STEP
   assembly that finishes** (blocker 9).
10. **A public metals catalogue.** `//pub/std/manufacturing/material` publishes
   plastics; the alloys are catalogued here instead, which works and is the wrong
   place for 5052 aluminium. It would also give the 49 blanks a supplier.
11. **Somewhere for a step's own words and an image.**
   `doc/power-supply-assembly.md` is the one document here that is neither
   generated nor data: twelve steps, each with a photograph. The words belong on
   the ASSY node (`description:`, which exists); the photograph has nowhere to go.
12. **`pcbBasic`** is accepted by the schema and unknown to the loader.

## Answers to the notes on this round

* **"I don't understand the release-disagrees-with-itself problem and need more
  details."** It has a section of its own now - "Where the release disagrees with
  itself" - which says what the two copies of each part *are*, why both matter at
  once, and what each of the eleven differences is, with the evidence. The short
  version: each arm ships one file per part **and** one file for the whole arm, the
  second holding its own copy of every one of those solids. `arm.assy` takes its
  placements from the assembly and its geometry from the part files, so a part whose
  two copies differ is placed where the assembly says with geometry that belongs
  somewhere else. Two cover file names are swapped (proved vertex for vertex, all
  1848 of them), the base plate is 0.75 mm thinner in one copy than the other - which
  is the entire reason the arm PartCAD builds is 2 mm taller than the release - and
  eight more differ inside the same outline. `tools/check_parts_against_release.py`
  is the check, so the next release can be audited before anybody builds from it.
* **"For the 74 MB source files, see how it is dealt with for Intel SBCs in
  `//pub/electronics`."** Read, and followed. `//pub/electronics/sbcs/intel` is a
  repository of its own holding one 27.8 MB `nuc12.step` as `type: step` with a
  vendor, an SKU and a product URL, which `//pub/electronics/sbcs` reaches through a
  `dependencies:` entry rather than carrying. So the four actuators are vendor solids
  too, and `third_party/README.md` now says what splitting that package off would
  take - one `dependencies:` block - and why it is the one to split: 84 MB of a 434 MB
  tree, depended on by both arms and depending on neither. My holding them out on
  size was the wrong call, and "What `pc test` finds" measures what it cost.
* **"Rebase on the latest changes in all involved repositories."** Done: PartCAD
  0.8.124 to 0.8.136, three of this branch's own changes rebased onto the new
  `manufacturing:` and document code, and this repository's floor moved to
  `>=0.8.136`. "What has landed since the last round" is what that brought.
* **"There is no need to change naming conventions for parts, definitely not by
  the manufacturing method."** Taken, and done: the four prefixes are gone and
  every part is named for what it is. The only name that still says something
  about a part's role is `<part>-blank`, and that is a different object rather
  than a category - the piece of plate the part is cut out of, which exists
  because `subtractive` asks what the part was cut from.
* **"`manufacturing:` instructions are only required if the user is expected to
  follow them."** Taken. Every part that carries one is a part this repository
  expects the user to print or machine; the bought parts carry `vendor`/`sku` and
  no method, and the 49 blanks are marked `manufacturable: false` because nobody
  is asked to supply them - they exist so that the cut can be checked.
* **"If a folder is used primarily for parts and assemblies, its README must be
  generated by PartCAD."** Taken, both folders. The vendor's front matter is in
  `docs.intro`, the `pc` commands are in `docs.usage`, and `render: readme:` writes
  the file. The two sections that did not fit the 5000 character limit are documents
  of their own under `doc/`, linked from the generated one, and each says what would
  have to exist for it to be generated too.

  On "the output filename for a package README can be configured": not the
  basename, and the field that looks like it does something worse. `path:` under a
  `render:` file type is the path of an implementation of that file type, so
  `render: readme: path: readme.md` made PartCAD execute this folder's readme as
  the readme renderer - which broke every render in this repository until it was
  found. That half is fixed upstream this round; the name is still not settable, so
  the DM folder's `readme.md`, which was the vendor's spelling, is `README.md`. See
  blocker 8.
* **"See if two robot designs can reuse more parts and subassemblies."** More
  parts, yes, and provably: the seven machined and printed ones from last round,
  plus most of the purchased ones - the thrust bearing, the rail, its carriages, the
  pad, the gear and two screws are one declaration each now, because both releases
  model them as the same solid in the same frame. Fewer *sub-assemblies*, and that
  is the more useful half of the answer: the shared gripper slide an earlier round
  declared has been removed, because measuring the two releases showed they do not
  place those shared parts to the same numbers. See "What the two arms share".
* **"Evaluate the latest gen-assembly skill, including defining ports and
  interfaces, sufficient to drop all or most `location:`."** See "What it would take
  to drop `location:`". The skill's subject matter now applies, because the
  placements exist; its "do not predict a mate, try it" rule is what produced the
  two derived actuator ports and what falsified the flange's. What still stops
  `connect:` from replacing `location:` wholesale is no longer a PartCAD blocker:
  0.8.130 gave an alias its source's ports, which was the one thing in the way, and
  `check/motor-mount` now proves the whole chain through this package's own name for
  the motor. What is left is the same derivation for the other joint families and
  one open question about naming a node across link groups.
* **"See if `pc test` finds any issues."** 1586 of them, and they are worth reading
  rather than silencing - see "What `pc test` finds". Two findings changed this
  repository: five accessory mounts had no manufacturing tolerance and four
  countersunk screws had no SKU their readme in fact publishes. Three more changed
  PartCAD. And the largest group of geometric findings used to measure the one
  shortcut taken here - the four actuator envelopes - rather than the arm; now that
  the actuators are the vendor's own solids it does not, which took 263 interference
  findings with it and left the five biggest in the one assembly whose placements
  this repository guessed.
* **CAM.** Noted as a conversation for later. What is here now: twenty plates
  produce G-code with the machine declared on the part rather than in a duplicate
  of it, and the routes still cut the outline and the through holes and nothing
  at another depth.

## Next steps on the reBot side

The first three of last round's steps are done - the placements are recovered, the
components are identified, and the fasteners are placed and counted joint by joint -
so what is left starts at what was the fourth.

1. Derive the rest of the joints the way the two actuator ports were derived, and
   convert those placements to `connect:` with a `how:` on each. The recipe is in
   "What it would take to drop `location:`", and nothing in PartCAD is in the way of
   it any more. The joint families, in order of how many placements each would
   retire: a screw in a tapped hole (271 across both arms), a bearing in its housing
   (6), a carriage on its rail (4), a rack against the pinion (4).
2. Find the 10.6 mm between a DM4340P and its rear flange, which is the one thing
   the derivation could not explain. If it is a part, it is a part neither the readme
   nor the released assembly names.
3. Declare the RS arm's joints, which have no measured pattern at all yet: nothing
   in that package carries a mating face that has been read off its own file, so
   `actuator/rs00` and `actuator/rs06` have no port.
4. Place what the released assemblies do not model: the CAN-USB board, the XT30
   separation board, the IEC socket, the AC wiring, the M3 nuts and the harnesses.
   These are the only parts left with no placement, and they will not come out of a
   STEP file - somebody has to say where they go.
5. Unfold one of the four DM links to get its flat blank, and declare the pair
   properly: the blank as `subtractive` with the outline and the holes, the link
   as `sheet_metal` with the bend lines as a sketch. One worked example is enough
   to see whether the other three follow.
6. Finish the CAM jobs once a job can carry several operations: the pockets and
   counterbores of each plate, and the turned and barstock parts of the RS arm,
   which a 2.5D route cannot describe at all.
7. Finish `third_party/`: the CAN-USB board, the XT30 separation board, the IEC
   socket, the M3 nuts and the remaining cable lengths. Everything else that used
   to be on this list - the gear, the dowel pins, the KA3x12 - is the vendor's own
   solid out of the released assembly now.
8. Export the arms as URDF once the joints are interfaces — the repository already
   ships ROS and LeRobot support, and the URDF would then come from the same
   source as the parts list.
9. Price the fasteners. Every fastener of both arms now carries the vendor and SKU
   its readme row links, and no fastener row in either readme carries a price, so
   `pc supply quote` refuses rather than under-counting a whole arm. One number per
   pack is all it needs.
10. Bring the four translated readmes (`readme_zh`, `readme_jp`, `readme_fr`,
   `readme_es` and the RS equivalents) in line with the English ones, whose BOM
   tables are now a pointer to the generated documents. They still carry the old
   hand-written tables, which is exactly the drift the generated list exists to
   end — and translating the replacement is a job for somebody who reads those
   languages.

## Open data questions for the hardware maintainers

Everything in "What the released CAD says that the readme does not" is one, and
in particular: the DM4310 dimensions, the MGN9 rail section, the AS5578 washers,
and every fastener count. Beyond those:

* Are the `KM*` screws hex socket (ISO 10642) or Phillips (ISO 7046)? The readme
  says hex socket and links a Phillips product. ISO 10642 is assumed.
* `KA3*12` self-tapping screws: which standard?
* Where does the silicone pad go? It is placed under the base plate on a guess.
* DM: `readme.md` calls the rail bracket `01-Rail-Bracket.step`; the file is
  `01_Rail_Bracket.step`.
* DM: `Metal_Parts/` contains both `02-RACK.step`/`02_Rack.step` and
  `03-Link*.step`/`03_Link*.step`. One set should be deleted - and they are
  duplicates rather than variants: `03-Link5.step` and `03_Link5.step` are the
  same solid, vertex for vertex.
* DM: `02_Base_Motor_Shim.step` is in the repository and in `images/` but in no
  BOM table — what is it, and how many?
* DM: the repository has `reBot_B601_DM_v1.1_20260425.step` and
  `reBot_B601_DM_v1.1_20260625.step`; the readme mentions only the first, which
  is the one declared here. **The second one is the RS arm.** It opens as
  `reBot_B601_RS_v1.0_20260625` with the RS release's own group names, and it is not
  the same file as the RS folder's copy either - 262 components against 263. So it
  is mislabelled, and one of the two RS exports is stale.
* RS: `README.md` lists `2-M7-STATOR.step` for gripper connector B, but the
  repository has `2-M7-ROTOR.step` and no `2-M7-STATOR.step`. **Answered this
  round**: `2-M7-ROTOR.step` is the DM arm's gear connector, vertex for vertex,
  and the RS package now aliases it under that name.
* Both readmes link one fastener product for several sizes - the DM one links an
  M3x12 product for KM3x7, x9, x12 and x16, the RS one links the M4x75 product for
  M4x8, M4x16 and M4x70. Which SKU is each? Every fastener now carries the vendor
  and SKU its own row links, so the BOM is answerable; what it answers with, for
  those rows, is the readme's own link rather than a checked one.
* Both readmes' fastener quantities are minimums, and the released CAD disagrees
  with all of them - see the table in "What the released CAD says that the readme
  does not". Three cases need a decision rather than a correction: `KM3x9`, where
  the readme's 31+ is three screws short of the 34 the CAD holds; and the RS
  readme's `KM3x16` (8+) and `HM3x26` (6+), neither of which its CAD uses at all.
* The two releases model the **6803ZZ** as two different bearings - a plain 26 mm
  one in the DM arm, a flanged 28 mm one in the RS arm - under one readme row and
  one SKU, which is a plain 6803ZZ. Does the RS arm need a flanged bearing?
* The DM release calls a screw `HM3-26` and models it 27.90 mm long over a 2.90 mm
  head, which is the M3x25 the readme orders. The name or the readme is wrong; the
  geometry says the readme.
* The DM release's dowel pins are 4x7, 4x10, 4x14 and 3x8. The readme orders
  "M4*8mm" and "M4*12mm", quantity "Several", and links one assortment for both.
  Which sizes does that assortment actually contain?
* `S-M4-5-JIMI` is in the released DM assembly twice and in no BOM table. It
  measures 4.0 across and 5.0 long with a socket and no head, so it is an M4x5 set
  screw. What is it, and where is it bought?
* No fastener row in either readme carries a price, so a quote for a whole arm
  refuses rather than under-counting. What does a pack cost?
* **Eleven published part files are not the solid the released assembly holds**
  (`tools/check_parts_against_release.py`). Which copy is authoritative, and which
  should the next release carry? The two arm covers are the clearest and the most
  certain: `01_Upper_Arm_Cover.step` is the release's lower-arm cover vertex for
  vertex, so the two file names are swapped. The base plate differs by 0.75 mm of
  thickness and 2 mm of position, which reads as a revision rather than a mistake -
  but it means a printed base plate is not the one the assembly was checked with.
  The other eight differ only inside the same outline, between 4 and 2050 mm³.
* RS: `2-RSM1-ROTOR-1.step` appears twice in the BOM, as "Motor 1 Bearing Mount"
  (x1) and as "Link1 Bottom Metal" (x3).
* RS: `2-RSM1-STATOR-2.step` and `2-SPACE-M4-STATOR.step` are in the repository
  but in no BOM table. **Answered this round** by the released assembly, which
  places one of each: the first is a 95 x 95 x 8 mm plate in the base, the second a
  63 mm spacer 5.5 mm thick in link 3. Both are declared now; what is still open is
  what they are *for* and whether 5052 is the right alloy for them.
* RS: the power supply BOM lists 10x M4x6 screws while the assembly steps use 8.
