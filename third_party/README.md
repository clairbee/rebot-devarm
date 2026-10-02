# Third-party shapes

The shapes of the parts the reBot DevArm **buys** rather than makes: the
actuators, the bearings, the linear rail and its carriages, the gear, the dowel
pins, the fasteners, the power supplies, the connectors, the wire and the
silicone pad.

Every part of an assembly needs a shape — not to be manufactured from, since
these are ordered by vendor and SKU, but to see the arm, to check that the parts
fit, to place them where the released assembly places them, and eventually to
simulate them.

## Most of these are the vendor's own geometry

34 of them are files under [`vendor/`](./vendor), each one solid taken out of a
released full-arm STEP assembly by
[`../tools/extract_vendor_parts.py`](../tools/extract_vendor_parts.py) and
declared as `type: step` with its vendor, its SKU and its product URL.

They are the vendor's geometry rather than an envelope for a reason that is not
about fidelity. Every placement in `../hardware/*/arm.assy` is read off the
released assembly, and a transformation says where a *model's origin* goes — so it
is only correct for the model it was measured from. Put an envelope there instead
and the part lands origin-on-origin rather than face-on-face. The MGN9 rail was
the clearest case: 170 mm long, laid along X where the release has it along Z.

The four actuators were held out of this on size, and that cost them their
geometry — a cylinder of the full diameter swallows the steps a real motor has, so
`pc test` reported two DM4310s overlapping each other by 30534 mm³. They are
vendor solids now too, at 17–25 MB each.

That is what **`//pub/electronics/sbcs/intel`** does, and it is where the pattern
comes from: that package is a repository of its own holding one 27.8 MB
`nuc12.step`, declared as `type: step` with a vendor, an SKU and a link to the
product page. The bytes live in the package that needs them and nowhere else, and
`//pub/electronics/sbcs` reaches them through a `dependencies:` entry rather than
carrying them.

**So this package is the one to split off** when the size of this repository
starts to matter. It is already a package in its own right — nothing in it
depends on either arm, both arms depend on it, and `vendor/` is 84 MB of the 434
MB this repository's working tree holds. Moving it to a repository of its own and
importing it as a `git` dependency is a change to one `dependencies:` block, and
the result is what the Intel package already looks like.

For scale: the two releases' own full-arm STEP files are 106 MB of that 434, and
they are inputs this repository cannot do without. `vendor/` is geometry *derived*
from them, which is exactly the kind of thing a separate package carries.

## Four of them are still envelopes

The two power supplies, the XT60E panel connector and the 14 AWG wire: the
releases do not model any of them, so there is nothing to take. Each is built by a
script in [`src/`](./src), reproduces the dimensions that decide fit and nothing
else, and says in a comment which of its dimensions are stated by a datasheet and
which are inferred. Use one to check a clearance. Do not use one to locate a
fastener.

## Which is which, and what is still missing

See [`partcad.yaml`](./partcad.yaml) for the declarations — each says where its
shape came from — and [`../PARTCAD.md`](../PARTCAD.md) for how this package fits
into the rest, which parts are still without a shape, and the open data questions
the vendor geometry has raised.
