#!/usr/bin/env bash
#
# Render every drawing this repository keeps, one object at a time.
#
# The drawings are the projections the generated parts lists show in their first
# column - `render: svg:` with a `doc/` prefix in each variant package - and the
# obvious way to produce them is `pc render -t svg -P <package>`, which renders
# every object of a package in one go. That does not finish: it writes 82 of a
# package's 101 parts and then stops making progress, with the daemon idle and
# nothing logged. Named one at a time, the same objects render in a second or two
# each. See ../PARTCAD.md, "A build stops making progress".
#
# So this is a loop rather than a command, and it is deliberately dumb: it asks
# PartCAD what each package declares, skips what is already drawn, and gives each
# object its own process and its own timeout - so one object that hangs costs its
# timeout instead of the rest of the run.
#
# The two arms are the objects that genuinely cannot be drawn: an assembly's
# projection needs its shape built, and a build with a sub-assembly to stage first
# does not return. They are attempted last, and a failure there is expected.
#
# Usage, from the repository root:
#
#     tools/render-drawings.sh              # what is missing
#     tools/render-drawings.sh --all        # everything, from scratch
#
set -u

PACKAGES="b601-dm b601-rs"
TIMEOUT_PER_OBJECT=900
PC="${PC:-pc}"
ALL=false
[ "${1:-}" = "--all" ] && ALL=true

# PartCAD keeps a warm context per workspace, and the drawings depend on the
# configuration; a daemon started before an edit serves the configuration it read.
"$PC" --no-ansi daemon stop >/dev/null 2>&1 || true

dir_of() {
	case "$1" in
	b601-dm) echo hardware/reBot_B601_DM ;;
	b601-rs) echo hardware/reBot_B601_RS ;;
	*)
		echo "unknown package: $1" >&2
		exit 1
		;;
	esac
}

render() { # <package> <object> [-a]
	local package="$1" object="$2" assembly="${3:-}"
	local target
	target="$(dir_of "$package")/doc/$object.svg"
	if [ "$ALL" = false ] && [ -f "$target" ]; then
		return 0
	fi
	# shellcheck disable=SC2086 # $assembly is a single optional flag
	if timeout "$TIMEOUT_PER_OBJECT" "$PC" --no-ansi render -t svg $assembly -p \
		-P "//pub/robotics/rebot/devarm/$package" "$object" >/dev/null 2>&1; then
		echo "  drawn    $package:$object"
	else
		echo "  FAILED   $package:$object"
	fi
}

for package in $PACKAGES; do
	echo "$package: parts"
	for object in $("$PC" --no-ansi list parts -P "//pub/robotics/rebot/devarm/$package" 2>/dev/null |
		awk '/^\t/ {print $1}' | sed 's|.*:||'); do
		render "$package" "$object"
	done
done

echo "assemblies that can be built"
for spec in "b601-dm gripper" "b601-dm power-supply" "b601-dm check/motor-mount" \
	"b601-rs gripper" "b601-rs power-supply"; do
	# shellcheck disable=SC2086 # two words, deliberately split
	set -- $spec
	render "$1" "$2" -a
done

echo "the two arms, which are expected to fail - see the comment at the top"
for package in $PACKAGES; do
	render "$package" arm -a
done

echo "drawings on disk: $(find hardware -name '*.svg' | wc -l)"
