#!/usr/bin/env bash
APP=$(basename "$PWD")
OUT="output"
DIR="$OUT|build|Makefile|config.status|config.log|pybuilddir.txt"


ln -s $(which python3) /var/tmp/myFRpy3
export PATH="/var/tmp:$PATH"

do_rename() {
    ROOT="$(realpath "${1:-.}")"
    S=(-e 's/PYTHON/MYFRPY/g' -e 's/Python/MyFRpy/g' -e 's/python/myFRpy/g')

    find "$ROOT" -type f -not -path '*/.git/*' \
      -not -name 'make.sh'\
      -not -name 'LICENSE'\
      -not -name 'LICENSE.old'\
      -not -name 'README.md'\
      -not -name 'README.old.rst'\
      -not -name 'README.rst'\
       -print0 \
      | xargs -0 grep -liI 'python' -- 2>/dev/null \
      | tr '\n' '\0' \
      | xargs -0 --no-run-if-empty sed -i "${S[@]}"

    find "$ROOT" -depth -not -path '*/.git' -not -path '*/.git/*' \
      -not -name 'make.sh'\
      -not -name 'LICENSE'\
      -not -name 'LICENSE.old'\
      -not -name 'README.md'\
      -not -name 'README.old.rst'\
      -not -name 'README.rst'\
      -print0 \
      | while IFS= read -r -d '' p; do
          d=$(dirname "$p"); b=$(basename "$p")
          n=$(printf '%s' "$b" | sed "${S[@]}")
          [[ "$b" != "$n" ]] && mv -- "$p" "$d/$n"
        done
}

do_run() {
    # run if exists
    [[ -e "$APP" ]]; ./$APP
}

do_regen() {
    # regenerate everything
    make regen-all
    make regen-frozen
}

do_build() {
    # build
    make -j8
}

do_install() {
    # build to output folder
    make install
}

do_erase() {
    # remove all build artifacts
    items=(
        Makefile config.status config.log pybuilddir.txt
        MyFRpy/frozen_modules build output
        $APP
    )
    for item in "${items[@]}"; do
        [ -e "$item" ] && rm -rf "$item"
    done
}

do_clean() {
    do_erase

    # configure
    # use 2>&1 >/dev/null to hide checks
    ./configure --prefix="$(pwd)/$OUT" --enable-optimizations

    # clean (now that Makefile exists)
    make clean
}

do_dir_project() {
    tree -I $DIR -L 2 -f
}

do_default() {
    do_clear_screen
    do_menu
}

do_clear_screen() {
    clear
}

do_menu() {
    echo ""
    echo "   project <$APP>"
    echo ""
    echo "   t -- rename  | renommer"
    echo "   d -- tree    | arborescence"
    echo "   p -- regen   | configurer"
    echo "   b -- build   | construire"
    echo "   i -- install | installer"
    echo "   r -- run     | exécuter"
    echo "   c -- clean   | nettoyer"
    echo "   e -- erase   | effacer"
    echo "   x -- exit    | quitter"
    echo ""
}

do_input() {
    read -p '>> ' value
    echo "$value"
}

main() {
    do_menu
    while true; do
        value=$(do_input)

        case "$value" in
            t) do_rename;;
            d) do_dir_project;;
            p) do_regen;;
            b) do_build;;
            i) do_install;;
            r) do_run;;
            c) do_clean;;
            e) do_erase;;
            x) break;;
            *) do_default;;
        esac
    done
}

if [ -t 0 ]; then
    main
else
    title="$BIN"
    xfce4-terminal\
        --title="$title"\
        -e "bash -c './make.sh $@; exec bash'"
fi
