# PartCAD digital thread for reBot DevArm

This repository carries a [PartCAD](https://partcad.org) package so that the bill
of materials, the manufacturing data and the assembly instructions of the arm are
machine-readable instead of living only in markdown tables.

```
partcad.yaml                              the root package, //pub/robotics/rebot/devarm,
                                          and the catalogue of the alloys both arms are cut from
hardware/reBot_B601_DM/partcad.yaml       every part of the DM (Damiao) variant
hardware/reBot_B601_DM/arm.assy           the arm, part by part
hardware/reBot_B601_DM/arm.md             its parts list, generated
hardware/reBot_B601_DM/power-supply.assy  the power supply enclosure, step by step
hardware/reBot_B601_DM/power-supply.md    its parts list, generated
hardware/reBot_B601_DM/doc/*.svg          a projection of every object, generated;
                                          the pictures in the parts lists
hardware/reBot_B601_RS/*                  the same for the RS (RobStride) variant
third_party/partcad.yaml                  envelope shapes for the purchased parts
third_party/src/*.py                      the scripts those shapes are built by
.github/workflows/partcad.yml             lints, and keeps the generated parts lists honest
```

Requires PartCAD **0.8.91** or newer.

**The readme BOM tables are gone.** `hardware/reBot_B601_DM/readme.md` and
`hardware/reBot_B601_RS/README.md` used to carry three hand-written tables each -
printed parts, machined parts, purchased parts - with a picture, a file name, a
material, a quantity and a process note per row. Those tables are now generated:
`arm.md` and `power-supply.md` beside each assembly are what PartCAD reads back
out of `partcad.yaml` and the `.assy` files, they carry every column the
hand-written ones did, and CI fails if they are out of date. The readmes keep what
a generated table cannot say - what the parts are for, what to watch out for when
making them, and what they cost.

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

# the machining routes of every plate that declares a 'cam:' job
mkdir -p /tmp/routes
pc --no-ansi cam -p -O /tmp/routes -P //pub/robotics/rebot/devarm/b601-dm

# what a part says about how it is made, and whether it holds up
pc --no-ansi info //pub/robotics/rebot/devarm/b601-dm:cnc/flange
pc --no-ansi test -P //pub/robotics/rebot/devarm/b601-dm cnc/flange

# a shape, in the viewer or as a file
pc --no-ansi inspect //pub/robotics/rebot/devarm/third_party:actuator/dm4310
pc --no-ansi export -t stl -p -O /tmp/out \
    //pub/robotics/rebot/devarm/b601-dm:printed/base-plate
```

`-p` on `export`, `render` and `cam` creates the directory a slash-named part
implies (`printed/base-plate.stl`); it does not create the `-O` directory itself.

Render `-t readme` with `-a <assembly>`, as above, and not for a whole package:
a package-wide readme render writes a generated `README.md` over whatever is
there (see the blockers).

Pass `--no-ansi` whenever the output is parsed by a script or an agent, and note
that it routes the logs to stderr. If a change to a `partcad.yaml` does not seem
to be picked up, stop the background daemon that keeps the warm context:
`pc daemon stop`.

## Conventions

* Part names are prefixed by how the part is obtained: `printed/*` (3D printed),
  `cnc/*` (machined), `purchased/*` (bought — an alias to the `third_party`
  package), `accessory/*` (optional add-ons), `cam/*` (the machined plates again,
  laid flat as jobs on a machine — see below). `reference/*` under `assemblies:`
  is geometry kept for reference, not a product this package claims to build.
* Quantities are **not** stored on the part. A part is declared once and its
  quantity is how many times an assembly places it, which is what makes a parts
  list roll up correctly across sub-assemblies. Until the assemblies are
  complete, each part's `desc` still carries the readme quantity as `(xN)`.
* ASSY has no quantity field and does not need one: it is written and read by
  machines. Repeated parts are emitted with a Jinja2 loop.
* Everything a shop is told lives on the part, and nothing lives in a comment:
  `properties:` says what the part **is** (material, colour), `tolerance:` how
  precisely it has to be made, and `manufacturing: {method, parameters}` how it
  is made and with what settings — the nozzle, layer height and infill of a
  printed part, the finish and the fit of a machined one. All of it is a column
  of the generated parts list, which is the whole reason for declaring it rather
  than writing it in the part's description.
* Materials are catalogued objects. The plastics come from
  `//pub/std/manufacturing/material/plastic`; the alloys are catalogued in this
  repository's root `partcad.yaml`, because the public index publishes plastics
  only. The parts lists print a material's formal name ("AL 5052", "ABS") rather
  than the reference that resolves it.
* Standard fasteners are `type: enrich` references to the parametric
  cq-warehouse parts in the public index. Purchased parts that no vendor models
  are envelopes in `third_party/`, aliased into the variant that buys them.
* Anything that could not be entered faithfully is a comment in place, tagged
  `TODO(data)` (a question for the hardware maintainers), `TODO(blocked)` (waits
  on a PartCAD feature) or `TODO(partcad)` (a PartCAD bug).

## Status

Done:

* Every printed, machined and purchased part of **both** variants is declared,
  with its material, its manufacturing method, its process parameters and its
  tolerance, and points at the STEP file in this repository.
* **Both arms are assembled.** `hardware/reBot_B601_DM/arm.assy` and
  `hardware/reBot_B601_RS/arm.assy` place every part of each arm as many times as
  its readme says, so both parts lists are aggregated from an assembly rather
  than typed. Same for the two power supply enclosures.
* **The readme BOM tables are replaced by generated documents.** `arm.md` and
  `power-supply.md` carry the picture, the material, the method, the process
  parameters, the tolerance, the vendor, the SKU, the source file, the
  description and the count — every column the hand-written tables had. CI
  regenerates them and fails on a difference.
* **The machined parts are validated as machining jobs.** Sixteen DM plates and
  four RS ones are declared a second time as `cam/*`, laid flat with the cutter
  that cuts them, and `pc cam` writes G-code for all twenty: `cam/flange`, for
  instance, comes out as a climb-milled profile 9.75 mm deep in 13 passes with
  1.6 m of cutting moves. `pc test`'s `cam` check runs the same code, so
  `method: subtractive` on those parts is a claim something checked.
* Geometry is verified: PartCAD reads every STEP file here, builds every
  third-party script, and the pictures in the parts lists are projections it
  rendered (`doc/**.svg`, checked in). Every object that appears in a parts list
  has one; the objects that do not appear in one were left unrendered, because a
  package-wide render silently skips a third of them — blocker 4.
* Two purchased parts are **measured rather than guessed**: the DM4340P and the
  RobStride RS06, whose vendors publish no dimensions, are sized from the solids
  in the released full-arm STEP files that match their BOM quantities.
* A cable is modelled the way a cable is: `third_party/cable-xt30-2x2.assy` is
  two connectors and a wire, with the wire's route belonging to the assembly.
* The released full-arm STEP files are `type: step` assemblies — PartCAD reads
  **389 components** out of the DM one and 370 out of the RS one.
* `pc lint` passes, configuration and ASSY schemas both.

Not done — and why:

* **Every `location` is still the identity location.** The placements are in the
  released STEP, which is readable; extracting them is the next step.
* **No `how` anywhere.** Assembly instructions attach only to
  `connect`/`connectPorts` nodes, and every node here is placed with `location`.
  Interfaces and ports have to exist first.
* **Fasteners are not placed**, and neither is the gear, the CAN-USB board, the
  IEC socket, the AC wiring or the M3 nuts. What the fasteners need is not a
  shape — cq-warehouse serves them — but a per-joint count, and the readmes give
  only arm-wide minimums. The released CAD does give exact counts; see below.
* **The sheet metal chain is still one link short.** The DM links 1, 2, 3 and 5
  are machined *and* formed, which is now expressible: `method: sheet_metal` with
  a `source:` naming the flat blank and an `instructions:` sketch of the bend
  lines. What is missing is the blank — unfolding the released part is a CAM
  operation this repository cannot perform, and the vendor publishes only the
  finished shape. So each is declared once, as `subtractive`, and says so.
* **Nothing can be priced.** See the blockers.

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

Of the six blockers reported against 0.8.80, **four are gone**, and the two
biggest of them were the ones holding the manufacturing data:

| Was | Now (0.8.91) |
|---|---|
| A manufactured `step` part could not declare a tolerance, so `pc test` failed all 45 of them | `tolerance:` is a **field** on the types whose file could have carried one, outranking the file. Every part here declares it, and the manufacturability check passes on it |
| No way to say a part is machined *and* formed | `method: sheet_metal`, with `source:` naming the flat blank and `instructions:` the sketch of the bend lines. Exactly the one-step-per-declaration model, and the four DM links are ready for it the moment there is a blank |
| `vendor`/`sku` on an `enrich` or an `alias` were ignored | Honoured. An `enrich` that names a vendor and an SKU is purchasable, which is what lets a catalogue of bought parts be one parametric shape plus an enrich per SKU |
| `pc export`/`pc render` would not create the directory a slash-named part implies | `-p` / `--create-dirs`, on `export`, `render` **and** `cam`. The blocker was wrong: the flag existed and we had not found it |

And three things arrived that were not asked for and are used here:

* **`materials:` in any package.** The alloys are catalogued in this repository
  instead of being strings, with density, tags and a formal name — which is what
  the parts lists print.
* **`cam:` and `pc cam`.** A part can carry the job that makes it, and
  `//builtin/cam:gcode` turns it into G-code. This is the first thing in the
  digital thread that is *checkable*: a plate whose holes are smaller than the
  cutter produces no route, and `pc test` says so.
* **`pc render -t readme` per assembly**, which is what replaced the readme
  tables — together with the columns contributed below.

### What this round contributed back to PartCAD

Five changes, each found by trying to use PartCAD on this repository:

1. **`offset:` moved the label and not the geometry.** Laying a plate flat for
   its machining route is what `offset:` is for, and it did nothing: the wrapper
   applied build123d's `relocate()`, which re-labels a shape's frame without
   moving it, so the route came back cut through the part's 34 mm depth instead
   of its 9.75 mm thickness. Now `moved()`, with a test that fails if `relocate()`
   comes back, and a note in the documentation because a cached shape survives
   the change of meaning.
2. **Every route with a degenerate arc in it was lost.** `//builtin/cam:gcode`
   ordered a contour's edges by projecting each of them back onto the contour,
   and `offset_2d` leaves arcs a few tens of nanometres long where two edges met.
   OCCT refuses to parametrize a point on one of those and refuses with an empty
   message, so the whole route disappeared and nothing said why — one of the 16
   DM plates. Now the wire's own topological order, which needs no projection.
   The same function crashed on a contour that came back as a single closed
   `Edge` rather than a `Wire`, which is what the inside of a small hole offset by
   the tool's radius is — a second plate.
3. **The generated parts list carries what a published one carries.** It had a
   part, a count and a description; it now also has a picture, the material, the
   method, the process parameters, the tolerance, the vendor, the SKU and the
   source file, each column appearing only where some row has something to say in
   it. That is what made replacing the readme tables possible rather than
   aspirational.
4. **`manufacturing.parameters`** — a free-form mapping for how the process is
   set up (nozzle, layer height, infill, finish, fit), which PartCAD does not
   interpret and the parts list prints. Before it, the three columns of print
   settings in the readme had nowhere to go but a part's description.
5. **`pc test -f cam` could not pass for a grouped object.** The check writes the
   route into a temporary directory of its own and the route is named after the
   object, so `cam/flange` needed `<tmp>/cam/` to exist. It did not, and there is
   no `--create-dirs` on `pc test`, so every one of the twenty jobs here failed
   the check on a missing file rather than on anything about its route. The check
   now makes that directory, which is its own tree to make.

## Blockers

1. **A 2.5D route follows the section at the bottom of the cut, whichever end is
   wider.** That is the safe choice when the widest section is at the bottom and
   destructive when it is at the top: the route then traces the pocket floor at
   full depth and cuts the part in half. Eight of the sixteen DM plates were in
   that orientation, and the workaround is to flip each one with `offset:` so the
   widest face goes down — which is also the physical truth about how a plate is
   held, so it is not a bad outcome, but nothing says so. `pc cam` does warn that
   the outline changes over the depth of the cut; it does not say that this one is
   dangerous and that one is merely conservative.

   A `section: bottom | top | widest` parameter would settle it, and `widest`
   would be the safe default for `profile`: following the widest outline leaves
   material, which is recoverable, where following the narrowest gouges, which is
   not.

2. **A route describes one operation at one depth, and a machined part is
   several.** These plates are an outline, some through holes, and pockets and
   counterbores at other depths. The outline route is right and the pockets are
   simply absent — the `cam:` section takes one `operation:`, one `tool:` and one
   `depth:`, so a second operation means a second object declaring the same file,
   which is a second route file and no statement that the two are one job in an
   order. `cam: operations: [...]`, a list, each entry with its own operation,
   tool, depth and top, would let a part carry the whole of what makes it. Until
   then no route in this repository should be sent to a machine without reading
   it first, and the readmes say so.

3. **`cam:` on an `alias` is dropped.** "The same part, laid flat as a job on the
   machine" is exactly an alias with an `offset:` and a `cam:` section, and it
   comes back as `declares no 'cam:' section`. So the 20 jobs here are second
   `type: step` declarations of the same file: the path is repeated, and a part
   and its job can drift.

4. **`pc render -t <type> -P <package>` silently renders only some of the
   package's objects.** For the DM package it enumerates 91 objects, writes 61
   files and exits 0. The missing 30 are every `alias`, every `enrich`, every
   assembly and — the part that makes it look like nothing — the five plain
   `type: step` parts under `accessory/`. Each of them renders correctly when
   named on the command line, and `_enumerate_shapes()` and
   `_should_render_format()` both include them, so the loss is downstream of
   both. It is a silent partial success, which is the worst shape a bug can have:
   the parts lists were missing a third of their pictures and nothing failed.

5. **`pc render -t readme -P <package>` overwrites a hand-written `README.md`.**
   The package document is generated to `README.md` in the package directory
   whether or not the package asked for one, so running that command in this
   repository destroyed `hardware/reBot_B601_RS/README.md` — the vendor's
   published document — and in the PartCAD repository itself it rewrote several
   hand-written `examples/*/README.md`. Both were recovered from git, and the safe
   spelling is `-a <assembly>`, which writes `<assembly>.md` only. Two fixes
   suggest themselves: generate a package README only where the package declares
   `readme` in its `render:` section, and refuse to overwrite a file that does not
   carry PartCAD's own generated-by marker.

6. **Nothing can price any of this.** The index publishes store providers for
   goBILDA and Home Depot only — no 3D printing service, no machine shop, and
   none of the vendors these parts come from (Amazon, Seeed Studio, AliExpress).
   Every purchased part carries a real vendor and SKU and every made part now
   carries a material, a tolerance and a process, and the one column the
   generated parts list still cannot replace in the readme is the price. It
   belongs to a provider rather than to a declaration — a price written into
   `partcad.yaml` goes stale on the first market change, which is the whole
   argument against hand-written tables — so what is missing is a provider that
   quotes, not a field.

7. **No URL beside `vendor`/`sku`.** The other column the readme keeps. This one
   *is* declaration data: which offer a SKU refers to does not change when the
   price does, and today the generated list can say `amazon` / `B0D54JSWBZ` but
   not link to it. A `url:` beside the two would retire the last hand-written
   purchased-parts table in this repository.

8. **A cached test failure loses its reason.** A second `pc test` of a part that
   failed reports `Failed test result loaded from cache` instead of what failed.

9. **An unknown key on a part is reported against the one key that is right.**
   `third_party/partcad.yaml` carried a `summary:` on each envelope — a key this
   repository invented and the schema does not have. What `pc lint` says about it
   is:

   ```
   third_party/partcad.yaml:71:11: 'build123d' does not match '^(:[^:]+|[^:]+:[^:]+)$'
   ```

   Column 11 of line 71 is the value of `type:`, which is correct and has nothing
   to do with it; the pattern is a *reference* pattern from a different branch of
   the `oneOf` the declaration fell through to. Nothing names `summary`, nothing
   names the line it is on, and the reported location is 20 lines away from the
   mistake. A `oneOf` over object variants can report the additional property
   instead — it is the one error that tells the user what to delete. (The
   summaries are comments now; the message is what is worth fixing.)

10. **A repository plugin's downloads do not go through the proxy** (unchanged, and
   not re-tested this round). The BOSL2 plugin fetches its tarball with
    `urllib.request.urlopen`, which ignores `HTTPS_PROXY`, so
    `//pub/std/metric/bosl2` answers 403 and the bearings and the module-1 gear
    here are local envelopes instead of enriched BOSL2 parts.

## Wish list

In the order that unblocks the most work here:

1. **`section:` on a CAM job, defaulting to the widest for `profile`** (blocker
   1). It is the one thing in this round that could have produced a wrong part
   rather than no part.
2. **A list of operations per CAM job** (blocker 2). Between this and item 1, a
   machined plate in this repository would be fully described by its declaration
   rather than by its outline alone.
3. **Fix the silent partial render** (blocker 4), and make the package README
   generation explicit (blocker 5). Neither is about features; both are about a
   command that reports success while doing part of the job or the wrong job.
   **A schema error that names the offending key** (blocker 9) belongs with them:
   all three are about a tool saying what actually happened.
4. **`cam:` honoured on an alias** (blocker 3), so that a part and its job are one
   declaration.
5. **A `url:` beside `vendor` and `sku`** (blocker 7), and **one provider that
   quotes printing and machining** (blocker 6). Together they retire the last
   table.
6. **A public metals catalogue.** `//pub/std/manufacturing/material` publishes
   plastics; the alloys are catalogued here instead, which works and is the wrong
   place for 5052 aluminium.
7. **Somewhere for a step's own words and an image.** Understood to be in flight.
   What this repository needs from it: the readme's wording per step (already in
   each node's `description:`) and an image reference per step, since the vendor's
   instructions are photographs.
8. **Help identifying what is inside a vendor STEP file.** `type: step` gives 389
   components named `Link4:1_solid27`. Grouping the solids by bounding box found
   the actuators in one pass, and `pc describe` plus renders is how a human or an
   LLM confirms the rest — but the cheap half could come from PartCAD: a listing
   of an imported assembly's components with their bounding box, volume and
   instance count. The table `pc bom` prints has the names and the counts;
   adding the geometry would make it the tool for this job.
9. **`pcbBasic`** is accepted by the schema and unknown to the loader, which logs
   `Unknown manufacturing method`. Noted as backlogged.

## Answers to the notes on this round

* **"The request to reconcile the generated BOM against a published markdown
  table is not fair."** Agreed, and withdrawn — the previous wish list asked for a
  `pc bom --diff` against the readme tables, which was asking PartCAD to keep a
  document alive that should not exist. The tables are gone: `arm.md` and
  `power-supply.md` are the parts lists now, and the readmes point at them. What
  made that possible was giving the generated document the columns the
  hand-written ones had — the picture, the material, the method, the process
  settings, the tolerance, the vendor, the SKU and the file — which is the third
  contribution above. Two columns are still only in the readme, a reference price
  and a link to the offer, and both are blockers rather than wishes now (6 and 7).
* **"See how the subtractive step can be defined now and validated by generating
  CAM routes."** Done for twenty plates, and it found two defects in
  `//builtin/cam:gcode` and one in `offset:` — see above. It also found the limit
  of a single-section route (blockers 1 and 2), which is the honest answer to how
  far "validated" goes: these routes cut the right outline to the right depth with
  the right cutter, and they do not cut the pockets. The RS variant is the sharper
  version of the same point — only four of its machined parts are plate at all;
  the joint discs are turned and the rotators are cut from bar, so no route is
  claimed for the rest rather than a wrong one being published.
* **A method is one step, not a sequence.** Settled, and the configuration says
  so where the "CNC + sheet metal" links are declared. `sheet_metal` landing means
  the chain is expressible; what is still missing is the blank's geometry, which
  is this repository's problem and not PartCAD's.
* **Purchased parts need shapes anyway.** Done, and now visible: every
  `purchased/*` line of both parts lists carries a picture of its envelope, and
  the two actuators whose vendors publish nothing are measured off the released
  CAD.
* **Ports from `pc describe` plus an LLM.** Still the plan for the next round;
  wish-list item 8 is the only thing we would ask PartCAD for.

## Next steps on the reBot side

1. Recover the placements. The released STEP is readable as an assembly, so the
   component transforms are there to be read; `pc convert assembly` and
   `pc import assembly` are the two routes into the package.
2. Identify the components: match the 389 named solids against the declared
   parts, name them, and retire the envelopes in `third_party/` for anything the
   vendor's own geometry covers.
3. Count the fasteners off the CAD (the table above) and place them joint by
   joint in both `arm.assy` files, then drop the arm-wide minimums from the
   readmes.
4. Declare interfaces and ports for the seven joints and the fastener patterns
   (`/pc:add-interfaces`), convert the placements to `connect:`, and attach
   `how:` to each step. That is what turns the power supply assemblies into
   instruction books and the arms into kinematics.
5. Unfold one of the four DM links to get its flat blank, and declare the pair
   properly: the blank as `subtractive` with the outline and the holes, the link
   as `sheet_metal` with the bend lines as a sketch. One worked example is enough
   to see whether the other three follow.
6. Finish the CAM jobs once a job can carry several operations: the pockets and
   counterbores of each plate, and the turned and barstock parts of the RS arm,
   which a 2.5D route cannot describe at all.
7. Finish `third_party/`: the gear (from BOSL2 once it can be fetched), the
   CAN-USB board, the XT30 separation board, the IEC socket, the M3 nuts, the
   dowel pins, and the remaining cable lengths.
8. Export the arms as URDF once the joints are interfaces — the repository already
   ships ROS and LeRobot support, and the URDF would then come from the same
   source as the parts list.
9. Bring the four translated readmes (`readme_zh`, `readme_jp`, `readme_fr`,
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
