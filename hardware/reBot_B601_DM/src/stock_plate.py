# The plate a machined part is cut from.
#
# 'method: subtractive' says a part is what is left of something that existed
# first, and PartCAD asks for that something: the part has to fit inside it, and
# the stock has to be bigger than the part somewhere. For every machined part of
# this arm that something is a rectangular piece of 5052 plate, in the thickness
# the part is thick.
#
# So the stock is derived from the part rather than typed out beside it: this
# reads the part's own STEP file, takes its bounding box, and returns a plate of
# exactly that thickness and 'margin' larger in the two directions across it.
# Nothing here is a number somebody copied, and a part that changes shape gets a
# blank that still holds it.
#
# 'step' is the part's file, relative to the package; 'margin' is how much wider
# the plate is than the part, in millimetres, on each of the four sides.

import build123d as bd

# The parameters of the part; PartCAD substitutes the declared values.
step = ""
margin = 5.0

# The wrapper runs with the package directory as the working directory, so the
# path is the one the part's own declaration uses.
part = bd.import_step(step)
box = part.bounding_box()
size = [box.size.X, box.size.Y, box.size.Z]

# The thickness is the smallest dimension: plate is bought by thickness and cut
# to shape, so that is the one direction the blank has nothing to spare in.
thin = min(range(3), key=lambda axis: size[axis])
grown = [value + 2.0 * margin for value in size]
grown[thin] = size[thin]

# Box() is centred on the origin, and the blank has to sit where the part sits:
# the checks compare the two in one frame.
plate = bd.Box(*grown).moved(bd.Location(box.center()))

if "show_object" in locals():
    show_object(plate.wrapped, name="stock")  # noqa: F821
