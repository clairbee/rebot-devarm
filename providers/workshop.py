# What this arm can be made with, and what that costs: the first, not the second.
#
# Every printed and machined part of both arms is made rather than bought, so
# nothing in a store's catalogue answers for it and 'pc test' has no supplier to
# find. What answers for it is a manufacturer - a printer or a shop - and the
# question PartCAD asks one is a capability question: can you make this, out of
# this material, in this colour, with this finish. That is a question this
# repository can answer honestly, because the answer is in the readmes: the
# printed parts are ABS and PLA at stated settings, the machined parts are 5052
# aluminium, anodized or sandblasted.
#
# What it does not answer is price. The readmes give two aggregate reference
# figures - about $50 for all the printed parts and about $250 for all the
# machined ones - and spreading those over the parts by volume would produce a
# number for every line of a quote that nobody quoted. So 'quote' refuses and
# says what it would need. A wrong price in a machine-readable BOM is worse than
# no price: somebody would build on it.
#
# The materials are the references the parts declare, because that is what
# PartCAD matches a part against (see 'is_part_available' in
# plugin_factory_provider_manufacturer.py). The colours are the hex values the
# parts declare for the same reason.
#
# As of 0.8.124 none of it is read for a part whose shape comes out of a file:
# the material of such a part is stated under 'properties:', and the supply path
# reads only the object-type parameter, which those types refuse. So this
# workshop is currently asked "can you make something, material unspecified" and
# answers yes to everything - including a bearing. What it lists below is what it
# would be held to the moment that is read. See ../PARTCAD.md.

if "request" not in globals():
    request = {"api": "caps"}

FINISHES = [{"name": "none"}, {"name": "anodized"}, {"name": "sandblasted"}]

if __name__ == "caps":
    output = {
        "materials": {
            # The printed parts: ABS for anything load-bearing or hot, PLA for
            # the rest, in the two colours the arm is drawn in.
            "//pub/std/manufacturing/material/plastic:abs": {
                "colors": [{"name": "#1A1A1A"}, {"name": "#2E7D32"}, {"name": "black"}],
                "finishes": FINISHES,
            },
            "//pub/std/manufacturing/material/plastic:pla": {
                "colors": [{"name": "#1A1A1A"}, {"name": "#2E7D32"}, {"name": "green"}],
                "finishes": FINISHES,
            },
            # The machined parts, and the plate they are cut from.
            "//pub/robotics/rebot/devarm:aluminium-5052": {
                "colors": [{"name": "none"}],
                "finishes": FINISHES,
            },
        },
        # A shop is sent the geometry, and STEP is what both arms are published
        # in.
        "formats": ["step"],
    }

elif __name__ == "quote":
    raise Exception(
        "No rate card is published for this workshop. The readmes give one figure for all "
        "the printed parts (~$50) and one for all the machined parts (~$250), which is not "
        "a price per part and must not be spread over them as if it were. Quote the parts "
        "with a real shop and record what it says here."
    )

elif __name__ == "order":
    raise Exception("This provider reports what can be made, not who will make it")

else:
    raise Exception("Unknown API: {}".format(__name__))
