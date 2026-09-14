# PartCAD digital thread for reBot DevArm

This repository carries a [PartCAD](https://partcad.org) package so that the bill
of materials and the assembly instructions of the arm are machine-readable
instead of living only in markdown tables.

```
partcad.yaml                              the root package, //pub/robotics/rebot/devarm
hardware/reBot_B601_DM/partcad.yaml       BOM of the DM (Damiao) variant
hardware/reBot_B601_DM/arm.assy           the arm, part by part
hardware/reBot_B601_DM/arm.md             its bill of materials, generated
hardware/reBot_B601_DM/power-supply.assy  the power supply enclosure, step by step
hardware/reBot_B601_DM/power-supply.md    its bill of materials, generated
hardware/reBot_B601_RS/partcad.yaml       BOM of the RS (RobStride) variant
hardware/reBot_B601_RS/power-supply.assy  the power supply enclosure, step by step
third_party/partcad.yaml                  envelope shapes for the purchased parts
third_party/src/*.py                      the scripts those shapes are built by
.github/workflows/partcad.yml             lints, and keeps the generated BOMs honest
```

Requires PartCAD **0.8.80** or newer.

The readmes stay the human-facing documents. These files are the source of truth
the tooling reads, and the `*.md` bills of materials beside each assembly are
generated from them — the readme BOM tables are next.

## Using it

```shell
pip install partcad                     # or: https://partcad.org installers
pc install                              # fetch the packages this one depends on

pc --no-ansi list parts -r              # every part of both variants
pc --no-ansi lint                       # partcad.yaml and every .assy

# the bill of materials, aggregated from the assembly
pc --no-ansi bom -P //pub/robotics/rebot/devarm/b601-dm arm
pc --no-ansi render -t readme -a -P //pub/robotics/rebot/devarm/b601-dm arm

# the released STEP file, read as an assembly of its own
pc --no-ansi bom -P //pub/robotics/rebot/devarm/b601-dm reference/arm-v1.1

# a shape, in the viewer or as a file
pc --no-ansi inspect //pub/robotics/rebot/devarm/third_party:actuator/dm4310
mkdir -p /tmp/out/printed && pc --no-ansi export -t stl -O /tmp/out \
    //pub/robotics/rebot/devarm/b601-dm:printed/base-plate
```

Pass `--no-ansi` whenever the output is parsed by a script or an agent, and note
that it routes the logs to stderr. If a change to a `partcad.yaml` does not seem
to be picked up, stop the background daemon that keeps the warm context:
`pc daemon stop`.

## Conventions

* Part names are prefixed by how the part is obtained: `printed/*` (3D printed),
  `cnc/*` (machined), `purchased/*` (bought — an alias to the `third_party`
  package), `accessory/*` (optional add-ons). `reference/*` under `assemblies:`
  is geometry kept for reference, not a product this package claims to build.
* Quantities are **not** stored on the part. A part is declared once and its
  quantity is how many times an assembly places it, which is what makes a BOM
  roll up correctly across sub-assemblies. Until the assemblies are complete,
  each part's `desc` still carries the readme quantity as `(xN)`.
* ASSY has no quantity field and does not need one: it is written and read by
  machines. Repeated parts are emitted with a Jinja2 loop.
* `properties:` says what a part **is** — its material and colour, with the
  material naming a catalogued object (`//pub/std/manufacturing/material/...`)
  wherever one exists. `requirements:` carries what is **asked of** whoever makes
  it (print settings, machining tolerance, finish), because a `step` part has
  nowhere else to put those; see the wish list.
* Standard fasteners are `type: enrich` references to the parametric
  cq-warehouse parts in the public index. Purchased parts that no vendor models
  are envelopes in `third_party/`, aliased into the variant that buys them.
* Anything that could not be entered faithfully is a comment in place, tagged
  `TODO(data)` (a question for the hardware maintainers), `TODO(blocked)` (waits
  on a PartCAD feature) or `TODO(partcad)` (a PartCAD bug).

## Status

Done:

* Every 3D printed and CNC machined part of both variants is declared and points
  at the STEP file in this repository. Printed parts declare
  `manufacturing: {method: additive}` and a catalogued material; machined parts
  `{method: subtractive}` and their alloy.
* **Geometry is verified for the first time.** PartCAD reads these STEP files and
  builds shapes from them here, which it could not do in either earlier round —
  `pc export -t stl` of `printed/base-plate` produces a 431 KB mesh, and all 15
  third-party scripts build.
* **The purchased parts are in the BOM.** `third_party/` declares envelopes for
  the actuators, bearings, linear rail and carriage, power supplies, the XT30 and
  XT60 connectors, wire and the silicone pad — 15 shapes, all building — and the
  variants alias them. `pc bom` for the DM arm is now 71 line items, up from 55.
* Two of them are **measured rather than guessed**: the DM4340P and the RobStride
  RS06, whose vendors publish no dimensions at all, are sized from the solids in
  the released full-arm STEP files that match their BOM quantities.
* A cable is modelled the way a cable is: `third_party/cable-xt30-2x2.assy` is
  two connectors and a wire, with the wire's route belonging to the assembly.
* The released full-arm STEP files are `type: step` assemblies. PartCAD reads
  **389 components** out of the DM one and 370 out of the RS one.
* The bill of materials of each assembly is generated as markdown
  (`pc render -t readme -a`) and checked in, and `.github/workflows/partcad.yml`
  regenerates it in CI and fails on a difference.
* `pc lint` passes, configuration and ASSY schemas both.

Not done — and why:

* **Every `location` is still the identity location.** The placements are in the
  released STEP, which is now readable; extracting them is the next step.
* **No `how` anywhere.** Assembly instructions attach only to
  `connect`/`connectPorts` nodes, and every node here is placed with `location`.
  Interfaces and ports have to exist first.
* **Fasteners are not placed**, and neither is the gear, the CAN-USB board, the
  IEC socket, the AC wiring or the M3 nuts. What the fasteners need is not a
  shape — cq-warehouse serves them — but a per-joint count, and the readmes give
  only arm-wide minimums. The released CAD does give exact counts; see below.
* **`pc test` fails every manufactured part.** Still the tolerance rule; see
  blocker 1.

## What the released CAD says that the readme does not

Reading the two released STEP files (with OCP, grouping the solids by bounding
box) settles several of the open data questions and raises new ones. All of this
is measured, not inferred from the readme:

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

## What has landed since the last round

Of the four blockers reported against 0.8.33, two are gone and both were the
expensive ones:

| Was | Now |
|---|---|
| Offline detection broke behind an HTTP proxy, so no sandbox and no geometry, ever | `connectivity_probe()` asks the proxy when one is configured. This is why there is verified geometry in this round at all |
| A declared root `name` had to exist in the public index | Honoured as declared |

`pc bom`, the `how`/`comment`/`exploded` fields, the ASSY schema, `fileHash`,
`count_per_sku`, the `assy` manufacturing method and now `materials:` and
`type: step` assemblies all arrived in the 0.8 line and all of them are in use
here.

## Blockers

1. **A manufactured `step` part cannot pass `pc test`.** `tolerance` is an
   object-type parameter, accepted only on the homogeneous part types (`stl`,
   `cadquery`, `build123d`, `sdf`, `scad`, `extrude`) and refused on `step`. The
   `cam` check requires one of anything that is made rather than bought, so every
   part in this repository fails:

   ```
   Test failed: //pub/robotics/rebot/devarm/b601-dm:printed/base-plate:
     cam: No manufacturing tolerance: the part type 'step' does not accept one
   ```

   45 parts, all of them a STEP file somebody has to make. There is no way to
   satisfy the check and no way to opt out of it. The same rule keeps `material`
   off these parts, worked around by declaring it under `properties:` — which is
   a different claim: `properties.material` says what the part *is*, and a shop
   needs to be told what to make it *of*.

   The stated intent is that manufacturability data can be supplemented in the
   part declaration where the STEP file does not carry it. That is exactly right,
   and as of 0.8.80 it is not what the code does.

2. **No metals catalogue.** `//pub/std/manufacturing/material` publishes
   plastics, so the printed parts name catalogued PLA and ABS while every
   machined part names "Aluminum Alloy 5052" as a string. An aluminium catalogue
   with 5052 in it would finish the job — density is what a mass estimate for a
   7 kg arm needs.

3. **No provider can quote any of this.** The index publishes store providers for
   goBILDA and Home Depot only — no 3D printing service, no machine shop, and
   none of the vendors these parts actually come from (Amazon, Seeed Studio,
   AliExpress). Every purchased part here carries a real `vendor` and `sku`, and
   nothing can act on them.

4. **`vendor`/`sku` declared on an `enrich` or an `alias` are ignored.** Only the
   ones on the part underneath are read, so an enriched part that names a vendor
   and an SKU is a part nothing can order — `pc test` says
   `Cannot be purchased or manufactured` about a part whose `pc info` shows both
   values. A four-line package tells the whole story:

   | declaration | purchasable |
   |---|---|
   | a part with `vendor`/`sku` | yes (`No suppliers found` — it got past the check) |
   | an alias to that part | yes, inherited |
   | an `enrich` with `vendor`/`sku` on the enrich | **no** |
   | an alias with `vendor`/`sku` on the alias | **no** |

   It matters for exactly the pattern you recommended: a catalogue of purchased
   parts is naturally one parametric shape plus an enrich per SKU — three
   bearings off one script — and that is the one spelling that loses the SKU.
   This repository worked around it by declaring each bearing separately.

5. **`pc export`/`pc render` do not create the directory a part's name implies.**
   A part named `printed/base-plate` — a slash being explicitly allowed, and the
   documented way to group parts — exports to `<output>/printed/base-plate.stl`,
   and fails with `Failed to create STL file` unless `printed/` already exists.
   One `os.makedirs` in the writer.

6. **A repository plugin's downloads do not go through the proxy.** The BOSL2
   plugin fetches its tarball with `urllib.request.urlopen`, which ignores the
   `HTTPS_PROXY` this environment requires, so `//pub/std/metric/bosl2` answers
   `HTTP Error 403: Forbidden` and none of its parts can be listed or built.
   That is why the bearings and the module-1 gear here are local envelopes
   instead of enriched BOSL2 parts, which is what they should be. The core now
   knows about the proxy (blocker 4 of the last round); the plugins do not.

## Wish list

Reworked against your notes, in the order that unblocks the most data entry here:

1. **Let a part say how precisely it has to be made, whatever its type.** This is
   blocker 1 and it is the one thing holding `pc test` over this whole
   repository. No new section is needed — `parameters:` is where it goes, exactly
   as it does for a `cadquery` part. What has to change is which types accept it:
   a tolerance is a demand on a process, not a statement about geometry, so the
   argument that a STEP file might carry several materials does not apply to it.
   Where the file does carry the data, read it and let the declaration
   supplement what is missing rather than refusing the declaration.
2. **A metals catalogue** (blocker 2), and a place for a surface finish beside
   the tolerance. Between them, `manufacturing: {method: subtractive}` becomes a
   request a shop could actually quote.
3. **Honour `vendor`/`sku` on an enrich and an alias** (blocker 4). Without it,
   a catalogue of purchased parts cannot be built the obvious way, and the
   symptom — a part that reports a vendor and an SKU and is called unpurchasable
   — costs an afternoon to track down.
4. **Three small fixes**, blockers 5 and 6: `makedirs` for a slash-named part,
   and a proxy-aware fetch in the plugin runtime. The second is worth more than
   it looks — it is the difference between a bearing this repository maintains
   and a bearing BOSL2 maintains.
5. **A provider for one 3D printing service and one machine shop** (blocker 3),
   even a stub that only quotes. The BOM is complete enough to price, and nothing
   can price it.
6. **Somewhere for a step's own words.** Acknowledged as in flight. What this
   repository needs from it: the readme's wording per step (already carried in
   each node's `description:`, which the schema accepts and nothing reads), and
   an image reference per step, since the vendor's instructions are photographs.
7. **Help identifying what is inside a vendor STEP file.** `type: step` gives 389
   parts named `Link4:1_solid27`, and the actuators, bearings and rail are among
   them. Grouping the solids by bounding box found the actuators in one pass, and
   `pc describe` plus renders is how a human or an LLM would confirm it — but the
   cheap half of that could come from PartCAD itself: a listing of an imported
   assembly's components with their bounding box, volume and instance count. The
   BOM table it prints today has the names and the counts; adding the geometry
   would make it the tool for this job. (An `--identify` that matched components
   against declared parts by shape would be the whole job, and is a bigger ask.)
8. **`pc bom --diff`, or the equivalent.** Rendering the readme per assembly is a
   good answer and it is what CI does here now. What is still manual is the other
   direction: the readme BOM tables in this repository are the *published*
   document, and reconciling them with the generated one is a human reading two
   tables. A mode that compared a generated BOM against a markdown table and
   reported the differences would let the two converge.
9. **`pcbBasic`** is accepted by the schema and unknown to the loader, which
   logs `Unknown manufacturing method`. Noted as backlogged.

## Answers to the notes on this round

* **A method is one step, not a sequence.** That resolves it, and the
  configuration now says so where the "CNC + sheet metal" links are declared: the
  machined blank and the formed part are two declarations, the blank being a part
  for stock-keeping that never enters the assembly. What stops this repository
  from writing that chain today is not PartCAD — it is that unfolding the
  finished part to get the blank is a CAM operation nobody here can perform, and
  the vendor publishes only the finished shape. Tell us where the sheet-metal
  method landed and the four links can be split the moment there is a blank to
  point at; at 0.8.80 the methods are `additive`, `subtractive`, `forming` and
  `pcbBasic`, with no sheet metal among them and no open pull request adding one.
* **No "request" field.** Agreed and withdrawn. The declaration is the right
  place; the problem is that the declaration refuses the values — blocker 1.
* **Purchased parts need shapes anyway.** Taken, and done: `third_party/` is that
  package, every shape says in its `summary:` what it is an envelope of and what
  it leaves out, and the two actuators whose vendors publish nothing are measured
  off the released CAD rather than invented. The cable pattern is taken too, and
  `//pub` is where the bearings and the gear should come from — blocker 5 is what
  stopped that here.
* **Ports from `pc describe` plus an LLM.** Understood, and that is the plan for
  the next round. Item 7 above is the only thing we would ask PartCAD for.

## Next steps on the reBot side

1. Recover the placements. The released STEP is readable as an assembly now, so
   the component transforms are there to be read; `pc convert assembly` and
   `pc import assembly` are the two routes into the package.
2. Identify the components: match the 389 named solids against the declared
   parts, name them, and retire the envelopes in `third_party/` for anything the
   vendor's own geometry covers.
3. Count the fasteners off the CAD (the table above) and place them joint by
   joint in `arm.assy`, then drop the arm-wide minimums from the readmes.
4. Declare interfaces and ports for the seven joints and the fastener patterns
   (`/pc:add-interfaces`), convert the placements to `connect:`, and attach
   `how:` to each step. That is what turns `power-supply.assy` into an
   instruction book and `arm.assy` into kinematics.
5. Write `hardware/reBot_B601_RS/arm.assy`.
6. Finish `third_party/`: the gear (from BOSL2 once it can be fetched), the
   CAN-USB board, the IEC socket, the M3 nuts, the dowel pins, and the three
   remaining cable lengths.
7. Export the arm as URDF once the joints are interfaces — the repository already
   ships ROS and LeRobot support, and the URDF would then come from the same
   source as the BOM.
8. Generate the readme BOM tables from `pc bom`, replacing the hand-maintained
   ones, and use Jinja2 in `partcad.yaml` (it is a template) to generate the
   repetitive part declarations from a table rather than writing each one out.

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
  `03-Link*.step`/`03_Link*.step`. One set should be deleted.
* DM: `02_Base_Motor_Shim.step` is in the repository and in `images/` but in no
  BOM table — what is it, and how many?
* DM: the repository has `reBot_B601_DM_v1.1_20260425.step` and
  `reBot_B601_DM_v1.1_20260625.step`; the readme mentions only the first, which
  is the one declared here.
* RS: `README.md` lists `2-M7-STATOR.step` for gripper connector B, but the
  repository has `2-M7-ROTOR.step` and no `2-M7-STATOR.step`.
* RS: `2-RSM1-ROTOR-1.step` appears twice in the BOM, as "Motor 1 Bearing Mount"
  (x1) and as "Link1 Bottom Metal" (x3).
* RS: `2-RSM1-STATOR-2.step` and `2-SPACE-M4-STATOR.step` are in the repository
  but in no BOM table.
* RS: the power supply BOM lists 10x M4x6 screws while the assembly steps use 8.
