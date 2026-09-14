# Third-party shapes

Envelope shapes for the parts the reBot DevArm **buys** rather than makes: the
actuators, the bearings, the linear rail and its carriages, the power supplies,
the connectors, the wire and the silicone pad.

Every part of an assembly needs a shape — not to be manufactured from, since
these are ordered by vendor and SKU, but to see the arm, to check that the parts
fit and eventually to simulate them. Their vendors publish no CAD model, so the
shapes live here.

**These are envelopes, not models.** Each one reproduces the dimensions that
decide fit and nothing else, each says in its `summary:` which dimensions are
stated by a datasheet and which are inferred, and two of them — the DM4340P and
the RobStride RS06, whose vendors publish no dimensions at all — are measured off
the released full-arm STEP files. Use them to check a clearance. Do not use one
to locate a fastener.

See [`partcad.yaml`](./partcad.yaml) for the declarations and where a better
shape would come from, and [`../PARTCAD.md`](../PARTCAD.md) for how this package
fits into the repository.

```shell
pc --no-ansi list parts //pub/robotics/rebot/devarm/third_party
pc --no-ansi inspect //pub/robotics/rebot/devarm/third_party:actuator/dm4340p
```
