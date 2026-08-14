# PartCAD digital thread for reBot DevArm

This repository carries a [PartCAD](https://partcad.org) package so that the bill
of materials and the assembly instructions of the arm are machine-readable
instead of living only in markdown tables.

```
partcad.yaml                              the root package
hardware/reBot_B601_DM/partcad.yaml       BOM of the DM (Damiao) variant
hardware/reBot_B601_DM/arm.assy           the arm, part by part
hardware/reBot_B601_DM/power-supply.assy  the power supply enclosure, step by step
hardware/reBot_B601_RS/partcad.yaml       BOM of the RS (RobStride) variant
hardware/reBot_B601_RS/power-supply.assy  the power supply enclosure, step by step
```

The readmes stay the human-facing documents. These files are the source of truth
the tooling reads; the long-term goal is to generate the BOM tables of the
readmes from them rather than maintain both by hand.

## Using it

```shell
pip install partcad-cli                 # or: https://partcad.org installers

pc --no-ansi list packages              # the two variants
pc --no-ansi list parts -r              # every part of both variants
pc --no-ansi list assemblies -r
pc --no-ansi lint                       # validate partcad.yaml against the schema
pc --no-ansi inspect //b601-dm:arm      # open the arm in the CAD viewer
```

Pass `--no-ansi` whenever the output is parsed by a script or an agent, and note
that it routes the logs to stderr.

If a change to a `partcad.yaml` does not seem to be picked up, stop the
background daemon that keeps the warm context: `pc daemon stop`.

## Conventions

* Part names are prefixed by how the part is obtained: `printed/*` (3D printed),
  `cnc/*` (machined), `purchased/*` (bought), `accessory/*` (optional add-ons),
  `reference/*` (geometry kept for reference only, not a BOM line).
* Quantities are **not** stored on the part. In PartCAD a part is declared once
  and its quantity is how many times an assembly places it, which is what makes
  a BOM roll up correctly across sub-assemblies. Until the assemblies are
  complete, each part's `desc` still carries the readme quantity as `(xN)` so
  that no data is lost.
* Standard fasteners are not modelled here. They are `type: enrich` references
  to the parametric cq-warehouse parts in the public PartCAD index, so an M3x12
  socket head cap screw is the ISO 4762 part with `size: M3-0.5, length: 12`.
* Repeated parts inside an `.assy` are emitted with a Jinja loop, because ASSY
  has no quantity field - see "Blockers" below.
* Anything that could not be entered faithfully is a comment in place, tagged
  `TODO(data)` (a question for the hardware maintainers), `TODO(blocked)` (waits
  on a PartCAD feature) or `TODO(partcad)` (a PartCAD bug).

## Status

Done:

* Every 3D printed and CNC machined part of both variants is declared and points
  at the STEP file in this repository.
* The fasteners that map onto a standard (ISO 4762 / 10642 / 7046 / 7045) are
  declared for both variants.
* `arm.assy` (DM) places all 55 manufactured parts with the quantities from the
  readme.
* `power-supply.assy` (both variants) follows the readme's assembly steps 1-1 to
  2-3, one container node per step.
* `pc lint` passes and `pc list parts -r` resolves all 167 parts, including the
  cq-warehouse dependencies pulled from the public index.

Not done - and why:

* **No geometry is verified.** Building a shape needs the sandboxed CAD runtime,
  which this work could not install (see blocker 8). The configuration is
  validated by `pc lint`, by `pc list`, and by rendering every `.assy` through
  Jinja and YAML and checking that every referenced part and every referenced
  file exists - but no STEP file has been opened by PartCAD yet.
* **Every `location` is the identity location.** Placements were never published
  in machine-readable form; they have to be recovered from the released full-arm
  STEP.
* **Purchased parts without a CAD model are not declared.** Actuators, bearings,
  linear rail, gear, cables, power supply, self-tapping screws, hex nuts. They
  are listed as comments in the two `partcad.yaml` files so the data entry is
  ready to go the moment blocker 1 is lifted.
* **Fasteners are not placed in `arm.assy`.** The readmes only give arm-wide
  minimums ("14+"), never a per-joint count.
* **RS has no `arm.assy`.** Upstream publishes no assembly instructions for the
  arm itself in either variant - only for the power supply.

## Blockers on the PartCAD side

Each of these stops data entry that is otherwise ready to be done here.

1. **A part must resolve to geometry.** `type` is mandatory and every type builds
   a shape, so a catalog item that has `vendor` and `sku` but no CAD model cannot
   be declared at all. This blocks ~25 BOM lines per variant (every actuator,
   bearing, rail, cable and the power supply) - the most valuable lines, since
   they are the ones that are actually bought. Wanted: a part with no shape, e.g.
   `type: catalog`, that still participates in the BOM and in `pc supply quote`.
2. **ASSY has no quantity.** A part appears in the BOM once per link, so 76
   screws mean 76 nodes. The Jinja loop used here keeps the file short but not
   the model: each screw is still a distinct instance with a distinct name. A
   `count: <n>` on a link would make fastener entry tractable.
3. **ASSY cannot carry assembly instructions.** There is no field for a step's
   text, image, tool, torque, or for the ordering between steps. The reBot
   readmes are exactly that kind of document, so the instructions currently
   survive in `power-supply.assy` only as YAML comments. Wanted: first-class
   steps, so that `pc` can render the assembly guide instead of a human
   maintaining it in markdown.
4. **`manufacturing.method` has no valid value for a machined part.** The JSON
   schema accepts `basic|additive|pcbBasic`
   (`partcad/src/partcad/schema/partcad.json`) while the loader accepts
   `additive|subtractive|forming`
   (`partcad/src/partcad/part_config_manufacturing.py`). `subtractive` fails
   `pc lint`; `basic` passes lint and then logs `Unknown manufacturing method`.
   Every CNC part in this repository is therefore declared without a
   manufacturing method.
5. **`fileFrom` / `fileUrl` are documented but rejected.** `docs/source/configuration.rst`
   documents pulling an object's file from a URL, and the schema has no such
   properties, so `pc lint` fails on it. That is the natural way to attach a
   vendor-hosted STEP model to a purchased part.
6. **`count_per_sku` is read but rejected.** `shape_config_store.py` reads it;
   the schema does not allow it. It is needed for the parts sold in packs -
   which is how every screw in this BOM is sold.
7. **A declared root `name` must already exist in the loaded tree.** Setting
   `name: /pub/robotics/rebot/devarm` makes `pc test`, `pc inspect` and
   `pc render` abort with `Package ... is not found`, because
   `/pub/robotics/rebot` is not in the public index. The root package here
   therefore declares no name, which also means it cannot yet be developed under
   the path its consumers will use.
8. **Offline detection breaks behind a proxy.** `Context._check_connectivity()`
   opens a raw TCP connection to `8.8.8.8:53`. In a sandbox or CI where only an
   HTTPS proxy is reachable, PartCAD declares itself offline even though `git`
   and `pip` work, and then cannot install its sandbox runtime - which is why no
   geometry could be built while preparing this package.
9. **No material objects exist.** The docs point `material` at
   `//pub/std/manufacturing/material/...`; no such package is in the index, so
   materials here are free-text strings ("Bambu ABS Black", "Aluminum Alloy
   5052").
10. **No provider can quote these parts.** The index publishes store providers
    for goBILDA and Home Depot only - no 3D printing or CNC service - so
    `pc test` reports `No suppliers found` for every manufacturable part and the
    BOM cannot be priced.
11. **There is no BOM command.** `Assembly.get_bom()` exists but is only reachable
    through `pc test` and `pc supply quote`. A `pc bom <assembly>` that prints
    markdown/CSV would let the readme tables be generated from these files
    instead of hand-maintained - the outcome this whole exercise is aiming at.

## Next steps

On the reBot side (data entry):

1. Recover the placements of `arm.assy` from `reBot_B601_DM_v1.1_20260425.step`
   (`pc import assembly` reads a STEP assembly) and replace the identity
   locations.
2. Replace those coordinates with interfaces and ports (`implements:` on the
   parts, `connect:` in the ASSY) for the seven joints, so the model describes
   the kinematics instead of a frozen pose.
3. Write `hardware/reBot_B601_RS/arm.assy` the same way.
4. Add per-joint fastener counts to the assemblies, then remove the arm-wide
   minimums from the readmes.
5. Add `vendor` and `sku` to the purchased parts that are sold by Seeed Studio,
   so a store provider can quote them.
6. Answer the `TODO(data)` questions now open in the configuration:
   * Are the `KM*` screws hex socket (ISO 10642) or Phillips (ISO 7046)? The
     readme says hex socket but links a Phillips product. ISO 10642 is assumed.
   * `KA3*12` self-tapping screws: which standard?
   * DM: `readme.md` calls the rail bracket `01-Rail-Bracket.step`; the file is
     `01_Rail_Bracket.step`.
   * DM: `Metal_Parts/` contains both `02-RACK.step`/`02_Rack.step` and
     `03-Link*.step`/`03_Link*.step`. One set should be deleted.
   * DM: `02_Base_Motor_Shim.step` is in the repository and in `images/` but not
     in any BOM table - what is it, and how many?
   * DM: the repository has `reBot_B601_DM_v1.1_20260425.step` and
     `reBot_B601_DM_v1.1_20260625.step`; the readme mentions only the first.
   * RS: `README.md` lists `2-M7-STATOR.step` for gripper connector B, but the
     repository has `2-M7-ROTOR.step` and no `2-M7-STATOR.step`.
   * RS: `2-RSM1-ROTOR-1.step` appears twice in the BOM, as "Motor 1 Bearing
     Mount" (x1) and as "Link1 Bottom Metal" (x3).
   * RS: `2-RSM1-STATOR-2.step` and `2-SPACE-M4-STATOR.step` are in the
     repository but in no BOM table.
   * RS: the power supply BOM lists 10x M4x6 screws while the assembly steps use
     8.
7. Once `pc bom` exists (blocker 11), generate the readme BOM tables from these
   files in CI and drop the hand-maintained ones.

On the PartCAD side (feature work), in the order that unblocks the most data
entry here: blocker 1 (catalog parts), blocker 2 (`count` in ASSY), blocker 3
(assembly instructions), blocker 11 (`pc bom`), then the schema/loader
mismatches 4-6, then 7-10.
