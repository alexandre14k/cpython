#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# auteur : alexander14k28@gmail.com
# date   : 2026-05-21
# desc   : compile & pack bins to AppImage
# -----------------------------------------------------------------------------

# --- paths ---
DIR_INPUT="app"
DIR_OUTPUT="tmp"
DIR_ENV="env"
DIR_DEPS="${DIR_OUTPUT}/deps"
DIR_SHIP="out"

# --- configuration ---
BIN_EXEC="myFRpy3.12"
# tool source origin : https://github.com/AppImage/appimagetool
APPIMAGE_BUILDER="appimagetool-x86_64.appimage"
APPIMAGE_OUT="myFRpy3.12-x86_64.AppImage"

# --- functions ---

init_folders() {
    mkdir -p "${DIR_OUTPUT}" "${DIR_DEPS}"
}

copy_binaries() {
    cp "${DIR_INPUT}/${BIN_EXEC}/bin/${BIN_EXEC}" "${DIR_OUTPUT}/${BIN_EXEC}"
    chmod +x "${DIR_OUTPUT}/${BIN_EXEC}"
}

fetch_dependencies() {
    ldd "${DIR_INPUT}/${BIN_EXEC}/bin/${BIN_EXEC}" \
        | awk '{print $3}' \
        | grep '^/'
}

MYFRPY_VERSION="3.12"
MYFRPY_STDLIB="${DIR_INPUT}/${BIN_EXEC}/lib/myFRpy${MYFRPY_VERSION}"
DIR_STDLIB="${DIR_OUTPUT}/lib/myFRpy${MYFRPY_VERSION}"

copy_dependencies() {
    local paths="$1"
    mkdir -p "${DIR_DEPS}"
    while IFS= read -r lib; do
        cp "$lib" "${DIR_DEPS}/"
    done <<< "$paths"
}

fetch_dependencies_dynload() {
    find "${DIR_STDLIB}/lib-dynload" -name "*.so*" 2>/dev/null | while read -r so; do
        ldd "$so" 2>/dev/null | awk '{print $3}' | grep '^/'
    done | sort -u
}

copy_dependencies_dynload() {
    local paths
    paths="$(fetch_dependencies_dynload)"
    while IFS= read -r lib; do
        cp "$lib" "${DIR_DEPS}/"
    done <<< "$paths"
}

copy_stdlib() {
    mkdir -p "${DIR_STDLIB}"
    cp -r "${MYFRPY_STDLIB}/." "${DIR_STDLIB}/"
}

create_desktop_file() {
    cat > "${DIR_OUTPUT}/${BIN_EXEC}.desktop" << DESKTOP
[Desktop Entry]
Name=${BIN_EXEC}
Exec=${BIN_EXEC}
Icon=${BIN_EXEC}
Type=Application
Categories=Utility;
DESKTOP
}

copy_icon_file() {
    if [[ ! -f "ress/icon.png" ]]; then
        echo "icon not found -- do check"
        echo "enter to quit ..."
        read
        exit
    else
        cp "ress/icon.png" "${DIR_INPUT}/${BIN_EXEC}.png"
        cp "${DIR_INPUT}/${BIN_EXEC}.png" "${DIR_OUTPUT}/${BIN_EXEC}.png"
    fi
}

create_apprun() {
    cat > "${DIR_OUTPUT}/AppRun" << APPRUN
#!/usr/bin/env bash
HERE="\$(dirname "\$(readlink -f "\$0")")"
export LD_LIBRARY_PATH="\${HERE}/deps:\${HERE}/lib/myFRpy${MYFRPY_VERSION}/lib-dynload:\${LD_LIBRARY_PATH}"
export MYFRPYHOME="\${HERE}"
export MYFRPYPATH="\${HERE}/lib/myFRpy${MYFRPY_VERSION}:\${HERE}/lib/myFRpy${MYFRPY_VERSION}/lib-dynload"
exec "\${HERE}/${BIN_EXEC}" "\$@"
APPRUN
    chmod +x "${DIR_OUTPUT}/AppRun"
}

build_appimage() {
    mksquashfs "${DIR_OUTPUT}" myFRpy3.12.squashfs \
    -comp zstd -Xcompression-level 19 -b 1M -noappend

    if "./${APPIMAGE_BUILDER}" --no-appstream "${DIR_OUTPUT}" "${APPIMAGE_OUT}"; then
        mkdir -p "${DIR_SHIP}"
        cp "${APPIMAGE_OUT}" "${DIR_SHIP}/"
        cd "${DIR_SHIP}"
        sha256sum "myFRpy3.12-x86_64.AppImage" > "myFRpy3.12-x86_64.AppImage.sha256sum"
        cp "../../LICENSE"* .
        cp "../../README"* .
        cp "../ress/test.py" .
        cd ..
    fi
}

do_build() {
    check_setup
    init_folders
    copy_binaries
    DEP_PATHS="$(fetch_dependencies)"
    copy_dependencies "$DEP_PATHS"
    copy_stdlib
    copy_dependencies_dynload
    create_desktop_file
    copy_icon_file
    create_apprun
    build_appimage
}

open_venv() {
    if [ ! -d "$DIR_ENV" ]; then
        echo "  no venv found, build it with <e>"
        return
    fi
    bash --rcfile <(echo 'export PATH="'$(pwd)'/env/bin:$PATH"
source '$(pwd)'/env/bin/activate') -i
}

build_venv() {
    "${APPIMAGE_OUT}" -m venv env
    local appimage_abs
    appimage_abs="$(readlink -f "${APPIMAGE_OUT}")"
    sed -i "s|^home = .*|home = $(dirname "$appimage_abs")|" env/pyvenv.cfg
    sed -i "s|^executable = .*|executable = $appimage_abs|" env/pyvenv.cfg
    ln -sf "$appimage_abs" "env/bin/myFRpy3"
    ln -sf "$appimage_abs" "env/bin/myFRpy"
    ln -sf "$appimage_abs" "env/bin/${BIN_EXEC}"
}

do_clean() {
    if [[ -d "${DIR_OUTPUT}" ]]; then
        rm -rf "${DIR_OUTPUT}"
    fi
    if [[ -d "${DIR_ENV}" ]]; then
        rm -rf "${DIR_ENV}"
    fi
    if [[ -d "${DIR_INPUT}/${BIN_EXEC}" ]]; then
        rm -rf "${DIR_INPUT}/${BIN_EXEC}"
    fi
    if [[ -f "${BIN_EXEC}.squashfs" ]]; then
        rm "${BIN_EXEC}.squashfs"
    fi
    if [[ -f "${APPIMAGE_OUT}" ]]; then
        rm "${APPIMAGE_OUT}"
    fi
    if [[ -f "${DIR_INPUT}/${BIN_EXEC}.png" ]]; then
        rm "${DIR_INPUT}/${BIN_EXEC}.png"
    fi
    find "${DIR_INPUT}" -name "*.pyc" -delete
    find "${DIR_INPUT}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
}

do_run() {
    ./"${APPIMAGE_OUT}"
}

open_console() {
    local title="$1"
    local cmd="$2"
    xfce4-terminal --title="${title}" -e "bash -c '${cmd}'"
}

show_menu() {
    clear
    echo "  release"
    echo ""
    echo "  b : build      -- construire"
    echo "  r : run        -- executer"
    echo "  c : clean      -- nettoyer"
    echo "  e : setup venv -- construire venv"
    echo "  o : open venv  -- ouvrir venv"
    echo "  x : exit       -- sortir"
    echo ""
    printf "  > "
}

check_setup() {
    if [[ ! -d "../output" ]]; then
        echo "setup not found -- do check"
        echo "enter to continue ..."
        read
    else
        copy_setup
    fi

    if [[ ! -d "$DIR_INPUT/$BIN_EXEC" ]]; then
        echo "$DIR_INPUT/$BIN_EXEC not found -- do check"
        echo "enter to quit ..."
        read
        exit
    else
        check_appimagetool
    fi
}

check_appimagetool() {
    if ! command -v $APPIMAGE_BUILDER >/dev/null 2>&1; then
        echo "$APPIMAGE_BUILDER not found"
        echo "check : https://github.com/AppImage/appimagetool"
        echo "enter to quit ..."
        read
        exit
    fi
}

copy_setup() {
    cp -rf "../output" "$DIR_INPUT/$BIN_EXEC"
}

menu_loop() {
    local choice

    show_menu
    while IFS= read -r choice; do
        case "${choice}" in
            b) do_build ;;
            r) do_run ;;
            c) do_clean ;;
            e) build_venv ;;
            o) open_venv ;;
            x) exit 0 ;;
            "") show_menu; continue ;;
            *) echo "  unsupported: ${choice}" ;;
        esac
        printf "  > "
    done
}

# --- main ---

# if called from desktop (no tty), open a console and relaunch
if [ ! -t 0 ]; then
    open_console "${BIN_EXEC} release" "bash -i '$(readlink -f "$0")'"
    exit 0
fi

menu_loop