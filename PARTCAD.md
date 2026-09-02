# PartCAD digital thread for reBot DevArm

This repository carries a [PartCAD](https://partcad.org) package so that the bill
of materials and the assembly instructions of the arm are machine-readable
instead of living only in markdown tables.

```
partcad.yaml                              the root package, //pub/robotics/rebot/devarm
hardware/reBot_B601_DM/partcad.yaml       BOM of the DM (Damiao) variant
hardware/reBot_B601_DM/arm.assy           the arm, part by part
hardware/reBot_B601_DM/power-supply.assy  the power supply enclosure, step by step
hardware/reBot_B601_RS/partcad.yaml       BOM of the RS (RobStride) variant
hardware/reBot_B601_RS/power-supply.assy  the power supply enclosure, step by step
```

Requires PartCAD **0.8.33** or newer.

The readmes stay the human-facing documents. These files are the source of truth
the tooling reads; the goal is to generate the BOM tables of the readmes from
them rather than maintain both by hand.

## Using it

```shell
pip install partcad                     # or: https://partcad.org installers
pc install                              # fetch the packages this one depends on

pc --no-ansi list packages              # the two variants
pc --no-ansi list parts -r              # every part of both variants
pc --no-ansi lint                       # validate partcad.yaml and the .assy files

# the bill of materials, aggregated from the assembly
pc --no-ansi bom -P //pub/robotics/rebot/devarm/b601-dm arm
pc --no-ansi bom -j -P //pub/robotics/rebot/devarm/b601-dm power-supply

# the released STEP file, read as an assembly of its own
pc --no-ansi inspect -a //pub/robotics/rebot/devarm/b601-dm:reference/arm-v1.1

# the assembly instruction book
pc --no-ansi render -t pdf -a power-supply -P //pub/robotics/rebot/devarm/b601-dm
```

Pass `--no-ansi` whenever the output is parsed by a script or an agent, and note
that it routes the logs to stderr. If a change to a `partcad.yaml` does not seem
to be picked up, stop the background daemon that keeps the warm context:
`pc daemon stop`.

## Conventions

* Part names are prefixed by how the part is obtained: `printed/*` (3D printed),
  `cnc/*` (machined), `purchased/*` (bought), `accessory/*` (optional add-ons).
  `reference/*` under `assemblies:` is geometry kept for reference, not a
  product this package claims to build.
* Quantities are **not** stored on the part. A part is declared once and its
  quantity is how many times an assembly places it, which is what makes a BOM
  roll up correctly across sub-assemblies. Until the assemblies are complete,
  each part's `desc` still carries the readme quantity as `(xN)`.
* ASSY has no quantity field by design, and does not need one: it is written for
  a machine to read and a machine to write. Repeated parts are emitted with a
  Jinja2 loop, which keeps the file short without the model losing track of the
  individual instances.
* `properties:` says what a part **is** (its material), `requirements:` carries
  what is **asked of** the manufacturer (print settings, tolerance, finish)
  until PartCAD has a home for that on a file-backed part — see the wish list.
* Standard fasteners are `type: enrich` references to the parametric
  cq-warehouse parts in the public index: an M3x12 socket head cap screw is the
  ISO 4762 part with `size: M3-0.5, length: 12`.
* Anything that could not be entered faithfully is a comment in place, tagged
  `TODO(data)` (a question for the hardware maintainers), `TODO(blocked)` (waits
  on a PartCAD feature) or `TODO(partcad)` (a PartCAD bug).

## Status

Done:

* Every 3D printed and CNC machined part of both variants is declared and points
  at the STEP file in this repository. With the standard fasteners and the
  optional accessories, that is 115 parts: 62 in the DM package, 53 in the RS
  one.
* Printed parts declare `manufacturing: {method: additive}`, machined parts
  `{method: subtractive}`, and both declare their material under `properties:`.
* `arm.assy` (DM) places all 55 manufactured parts with the readme's quantities,
  and `pc bom` reproduces them: 55 line items for the arm, 13 for the DM power
  supply, 15 for the RS one.
* `power-supply.assy` (both variants) follows the readme steps 1-1 to 2-3, with
  the readme's own wording on each node's `description`.
* The released full-arm STEP files are declared as `type: step` assemblies, so
  PartCAD reads their component tree instead of treating them as one solid.
* `pc lint` passes, including the ASSY schema check
  (`pc lint --file <file>.assy`).

Not done — and why:

* **No geometry is verified.** Building a shape needs the sandboxed CAD runtime,
  which this environment could not install (see blocker 4). Everything above is
  validated by `pc lint`, `pc list`, `pc bom` and the ASSY checker — none of
  which open a STEP file — but no shape has been built.
* **Every `location` is the identity location.** Placements were never published
  in machine-readable form. They are now recoverable from the `reference/*`
  assemblies, which is the next step rather than a blocker.
* **No `how` anywhere.** Assembly instructions — the stage, the torque, what to
  hold a part by — attach only to `connect`/`connectPorts` nodes, and every node
  here is placed with `location`. Interfaces and ports have to exist first.
* **Purchased parts without a CAD model are still not declared.** Actuators,
  bearings, linear rail, gear, cables, power supply, self-tapping screws, hex
  nuts. They are listed as comments in the two `partcad.yaml` files, ready to
  enter the moment there is a way to declare them.
* **Fasteners are not placed in `arm.assy`.** The readmes only give arm-wide
  minimums ("14+"), never a per-joint count.
* **RS has no `arm.assy`.** Upstream publishes no assembly instructions for the
  arm itself in either variant — only for the power supply.
* **`pc test` fails every manufactured part**, for a reason that is not about
  this repository — see blocker 1.

## What 0.8.x fixed

Of the eleven blockers reported from 0.7.158, seven are gone:

| Was | Now |
|---|---|
| No `pc bom` | `pc bom` prints the BOM as a table or JSON, and stops at sub-assemblies that can be bought ready-made |
| No assembly instructions in ASSY | `how` (stage, push force, turn torque, thread step, what to hold each end by), `comment` and `exploded`, plus `pc render -t pdf/html` for the instruction book |
| `manufacturing.method` had no value valid in both schema and loader | `additive`/`subtractive`/`forming` are valid in both; an assembly's method is implied by its type |
| `fileFrom`/`fileUrl` documented but rejected by the schema | accepted, and `fileHash` pins the bytes |
| `count_per_sku` read but rejected by the schema | accepted and documented |
| A declared root `name` had to already exist in the index | a name the index does not know is honoured; this package declares `//pub/robotics/rebot/devarm` again |
| No ASSY validation | ASSY files are schema-checked by `pc lint`, by `pc lint --file` and in the editor |

The `count` in ASSY that was asked for is deliberately **not** coming, and that
is the right call: ASSY is written and read by machines, and a Jinja2 loop
already says "this part, N times" without inventing a second way to say it.

Two of the four that remain are unchanged (the offline check, the missing
providers), and the other two are the same problems in a new shape.

## Blockers

1. **A manufactured `step` part cannot pass `pc test`.** `tolerance` is an
   object-type parameter, accepted only on the homogeneous part types (`stl`,
   `cadquery`, `build123d`, `sdf`, `extrude`). A `step` part rejects it. But the
   `cam` check requires a tolerance of anything that is made rather than bought,
   so every part in this repository fails:

   ```
   Test failed: //pub/robotics/rebot/devarm/b601-dm:printed/base-plate:
     cam: No manufacturing tolerance: the part type 'step' does not accept one
   ```

   Every part here is a STEP file that somebody has to make. There is no way to
   satisfy the check and no way to opt out of it. The same reasoning keeps
   `material` off these parts — worked around by declaring it under
   `properties:`, which is not the same claim: `properties.material` says what
   the part is, while a manufacturer needs to be told what to make it *of*.
2. **A part must still resolve to geometry.** `type` is mandatory, so a catalog
   item with a `vendor` and an `sku` and no CAD model cannot be declared at all.
   This is ~25 BOM lines per variant, and they are the lines people actually
   buy. `fileFrom: url` + `fileHash` covers the vendors that publish a STEP
   file; Damiao, RobStride and the bearing and cable suppliers do not.
3. **No provider can quote these parts.** The index publishes store providers
   for goBILDA and Home Depot only — no 3D printing or CNC service, and no
   materials package at `//pub/std/manufacturing/material` for the ones there
   are to select from. `pc test` reports `No suppliers found`, and the BOM
   cannot be priced.
4. **Offline detection breaks behind a proxy.** `Context._check_connectivity()`
   opens a raw TCP connection to `8.8.8.8:53`. In a sandbox or CI where only an
   HTTPS proxy is reachable, PartCAD declares itself offline even though `git`
   and `pip` work, and then cannot install its sandbox runtime — which is why no
   geometry could be built while preparing this package, in either round.

## Wish list

In the order that unblocks the most data entry here:

1. **A manufacturing request section on every part type.** `manufacturing:`
   already says how a part is made; let it also say what it is made of and how
   well — `material`, `tolerance`, `finish` — for any part type, since none of
   that is a claim about the geometry. That removes blocker 1, gives the
   `requirements:` text in this repository a real home, and puts the request
   next to the method it belongs to.
2. **A part with no shape.** `type: catalog` (or a part with `vendor`/`sku` and
   no `type`) that participates in the BOM, in `pc supply quote` and in an
   assembly, and is simply not drawn.
3. **Ports and interfaces inferred from geometry.** A package that imports
   vendor STEP files has no interfaces, and everything good in 0.8 — `connect`,
   `how`, the instruction book, mating, kinematics — is gated on having them.
   Deriving candidate ports from the CAD (cylindrical through-holes of a
   standard diameter, planar mating faces) and writing them into `partcad.yaml`
   for a human to confirm would turn a week of measuring into an afternoon of
   review. `pc import assembly` recovering placements is the same job from the
   other end.
4. **Let a step say what it is for.** The instruction book generates its own
   prose ("Add X to Y"), and the vendor's own wording — "install the XT60
   connector, secure with M3x8 screws and M3x2.5 nuts" — has nowhere to go: node
   `description` is accepted by the schema and read by nothing, and `comment`
   lives only inside `connect`. Rendering `description`/`comment` into the book,
   and allowing an image reference per step, would let this repository's readme
   tables be replaced by the generated book instead of duplicated by it.
5. **More than one method per part.** Links 1, 2, 3 and 5 are "CNC + sheet
   metal": subtractive then forming. `manufacturing.method` takes one value, so
   the second process is lost. A list would keep it.
6. **A machine-readable BOM diff.** The value of `pc bom` here is regenerating
   the readme tables; a mode that compares the generated BOM against the
   committed markdown (or writes it back) is what makes CI able to keep the two
   honest.
7. **Fix the connectivity probe** (blocker 4): try the URL that is actually
   about to be fetched, or respect `HTTPS_PROXY`, rather than a raw socket to a
   public DNS server.
8. **A `pcbBasic` that the loader knows.** The schema accepts it as a part
   method; `PartConfigManufacturing` does not map it, so it logs
   `Unknown manufacturing method`. Not needed here — noted because it is the
   last remnant of the schema/loader mismatch that #4 in the table above fixed.

## Next steps on the reBot side

1. Recover the placements from the `reference/*` assemblies — the released STEP
   files now read as component trees — and replace the identity locations in
   `arm.assy`.
2. Declare interfaces and ports for the seven joints and the fastener patterns,
   then convert the placements to `connect:` and attach `how:` to each step.
   This is what turns `power-supply.assy` from a parts list into an instruction
   book, and `arm.assy` from a pose into kinematics.
3. Write `hardware/reBot_B601_RS/arm.assy` the same way.
4. Add per-joint fastener counts, then drop the arm-wide minimums from the
   readmes.
5. Add `vendor`, `sku` and `count_per_sku` to the purchased parts that Seeed
   Studio sells, and `fileFrom`/`fileUrl`/`fileHash` for every vendor that
   publishes a STEP model.
6. Consider exporting the arm as URDF (`pc export -t urdf`) once the joints are
   interfaces — the repository already ships ROS and LeRobot support, and the
   URDF would then be generated from the same source as the BOM.
7. Answer the `TODO(data)` questions still open in the configuration:
   * Are the `KM*` screws hex socket (ISO 10642) or Phillips (ISO 7046)? The
     readme says hex socket but links a Phillips product. ISO 10642 is assumed.
   * `KA3*12` self-tapping screws: which standard?
   * DM: `readme.md` calls the rail bracket `01-Rail-Bracket.step`; the file is
     `01_Rail_Bracket.step`.
   * DM: `Metal_Parts/` contains both `02-RACK.step`/`02_Rack.step` and
     `03-Link*.step`/`03_Link*.step`. One set should be deleted.
   * DM: `02_Base_Motor_Shim.step` is in the repository and in `images/` but not
     in any BOM table — what is it, and how many?
   * DM: the repository has `reBot_B601_DM_v1.1_20260425.step` and
     `reBot_B601_DM_v1.1_20260625.step`; the readme mentions only the first,
     which is the one declared here.
   * RS: `README.md` lists `2-M7-STATOR.step` for gripper connector B, but the
     repository has `2-M7-ROTOR.step` and no `2-M7-STATOR.step`.
   * RS: `2-RSM1-ROTOR-1.step` appears twice in the BOM, as "Motor 1 Bearing
     Mount" (x1) and as "Link1 Bottom Metal" (x3).
   * RS: `2-RSM1-STATOR-2.step` and `2-SPACE-M4-STATOR.step` are in the
     repository but in no BOM table.
   * RS: the power supply BOM lists 10x M4x6 screws while the assembly steps
     use 8.
