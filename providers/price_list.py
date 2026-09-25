# A store that carries exactly what this repository's published BOM carries.
#
# The readmes list, for every bought part, a vendor, a product and a reference
# price. The vendor and the product live on the part (its 'vendor:' and 'sku:');
# the price does not belong there at all - a price written into a part
# declaration goes stale on the first market change, which is the whole argument
# against keeping a parts table in markdown. A price belongs to whoever is
# selling, which in PartCAD is a provider. This is that provider, reading
# ./price_list.csv.
#
# Three APIs, and what each of them is for:
#
#   avail  Is this vendor's product on the shelf, and enough of it? That is a
#          question about the catalogue, not about money, so a part whose price
#          nobody has published is still available.
#   quote  What would this cart cost? Here a missing price is fatal, and it says
#          which SKUs it is missing rather than quietly leaving them out: a total
#          that silently omits the fasteners is worse than no total.
#   order  Not implemented. Nothing here can place an order.
#
# The CSV has one row per product: vendor, sku, count (how many the pack holds
# on the shelf, in packs), price (per pack, in 'currency'), and a note. An empty
# price means the published BOM gives no price for it.

import csv
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone.utc)

if "request" not in globals():
    request = {"api": "caps"}

shelf = {}


def load():
    """The price list, as {(vendor, sku): (count, price or None)}."""
    with open(request["parameters"]["file"], newline="\n") as handle:
        for row in csv.DictReader(handle, lineterminator="\n"):
            if not row.get("vendor") or row["vendor"].startswith("#"):
                continue
            price = row.get("price", "").strip()
            shelf[(row["vendor"], row["sku"])] = (
                int(row["count"]),
                float(price) if price else None,
            )


if __name__ == "caps":
    raise Exception("A store has no manufacturing capabilities to report")

elif __name__ == "avail":
    load()
    entry = shelf.get((request["vendor"], request["sku"]))
    if entry is None:
        output = {"available": False}
    else:
        packs, price = entry
        output = {
            "available": packs * request["count_per_sku"] >= request["count"],
            "count": packs,
        }
        if price is not None:
            output["price"] = price

elif __name__ == "quote":
    load()
    price = 0.0
    unpriced = []
    for spec, part in request["cart"]["parts"].items():
        entry = shelf.get((part["vendor"], part["sku"]))
        if entry is None:
            raise Exception("%s (%s %s) is not on this price list" % (spec, part["vendor"], part["sku"]))
        packs, unit = entry
        per_pack = part["count_per_sku"]
        if packs * per_pack < part["count"]:
            raise Exception("%s: %d wanted, %d on the shelf" % (spec, part["count"], packs * per_pack))
        if unit is None:
            unpriced.append("%s (%s %s)" % (spec, part["vendor"], part["sku"]))
            continue
        # Bought by the pack, so a part needed 76 times at 120 to a pack is one
        # pack and not 76 of anything.
        packs_needed = (part["count"] + per_pack - 1) // per_pack
        price += unit * float(packs_needed)
    if unpriced:
        raise Exception(
            "The published BOM gives no price for %d of these, so this quote would be "
            "wrong rather than incomplete: %s" % (len(unpriced), "; ".join(sorted(unpriced)))
        )
    output = {
        "qos": request["cart"]["qos"],
        "price": price,
        "expire": (NOW + timedelta(hours=1)).timestamp(),
        "cartId": "reference-prices",
        "etaMin": (NOW + timedelta(days=2)).timestamp(),
        "etaMax": (NOW + timedelta(days=14)).timestamp(),
    }

elif __name__ == "order":
    raise Exception("This provider is a published price list, not a shop: order from the vendor named on the part")

else:
    raise Exception("Unknown API: {}".format(__name__))
