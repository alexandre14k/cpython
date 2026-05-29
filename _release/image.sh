#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# auteur : alexander14k28@gmail.com
# date   : 2026-05-21
# desc   : compiler et empaqueter un binaire en AppImage
# -----------------------------------------------------------------------------

# --- chemins ---
DIR_INPUT="app"
DIR_OUTPUT="tmp"
DIR_DEPS="${DIR_OUTPUT}/deps"
DIR_SHIP="out"

# --- configuration ---
BIN_EXEC="myFRpy3.12"
# télécharger appimagetool ici : https://github.com/AppImage/appimagetool
APPIMAGE_BUILDER="appimagetool-x86_64.appimage"
APPIMAGE_OUT="${DIR_OUTPUT}/${BIN_EXEC}.AppImage"

# --- fonctions ---

init_dossiers() {
    mkdir -p "${DIR_OUTPUT}" "${DIR_DEPS}"
}

copier_binaire() {
    cp "${DIR_INPUT}/${BIN_EXEC}/bin/${BIN_EXEC}" "${DIR_OUTPUT}/${BIN_EXEC}"
    chmod +x "${DIR_OUTPUT}/${BIN_EXEC}"
}

collecter_deps() {
    ldd "${DIR_INPUT}/${BIN_EXEC}/bin/${BIN_EXEC}" \
        | awk '{print $3}' \
        | grep '^/'
}

MYFRPY_VERSION="3.12"
MYFRPY_STDLIB="${DIR_INPUT}/${BIN_EXEC}/lib/myFRpy${MYFRPY_VERSION}"
DIR_STDLIB="${DIR_OUTPUT}/lib/myFRpy${MYFRPY_VERSION}"

copier_deps() {
    local paths="$1"
    mkdir -p "${DIR_DEPS}"
    while IFS= read -r lib; do
        cp "$lib" "${DIR_DEPS}/"
    done <<< "$paths"
}

collecter_deps_dynload() {
    find "${DIR_STDLIB}/lib-dynload" -name "*.so*" 2>/dev/null | while read -r so; do
        ldd "$so" 2>/dev/null | awk '{print $3}' | grep '^/'
    done | sort -u
}

copier_deps_dynload() {
    local paths
    paths="$(collecter_deps_dynload)"
    while IFS= read -r lib; do
        cp "$lib" "${DIR_DEPS}/"
    done <<< "$paths"
}

copier_stdlib() {
    mkdir -p "${DIR_STDLIB}"
    cp -r "${MYFRPY_STDLIB}/." "${DIR_STDLIB}/"
}

creer_bureau() {
    cat > "${DIR_OUTPUT}/${BIN_EXEC}.desktop" << DESKTOP
[Desktop Entry]
Name=${BIN_EXEC}
Exec=${BIN_EXEC}
Icon=${BIN_EXEC}
Type=Application
Categories=Utility;
DESKTOP
}

copier_icone() {
    if [[ ! -f "ress/icon.png" ]]; then
        echo "icone absente -- veuillez vérifier"
        echo "entrer pour quitter ..."
        read
        exit
    else
        cp "ress/icon.png" "${DIR_INPUT}/${BIN_EXEC}.png"
        cp "${DIR_INPUT}/${BIN_EXEC}.png" "${DIR_OUTPUT}/${BIN_EXEC}.png"
    fi
}

creer_apprun() {
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

construire_appimage() {
    if "${APPIMAGE_BUILDER}" "${DIR_OUTPUT}" "${APPIMAGE_OUT}"; then
        mkdir -p "${DIR_SHIP}"
        cp "${APPIMAGE_OUT}" "${DIR_SHIP}/"
        (cd "${DIR_SHIP}" && md5sum "${BIN_EXEC}.AppImage" > "${BIN_EXEC}.AppImage.md5sum")
        cp "${APPIMAGE_OUT}" "$(dirname "$(readlink -f "$0")")/"
    fi
}

faire_construire() {
    verifier_installation

    init_dossiers
    copier_binaire
    DEP_PATHS="$(collecter_deps)"
    copier_deps "$DEP_PATHS"
    copier_stdlib
    copier_deps_dynload
    creer_bureau
    copier_icone
    creer_apprun
    construire_appimage
}

ouvrir_venv() {
    if [ ! -d "env" ]; then
        echo "  aucun venv trouvé, lancez m d'abord"
        return
    fi
    bash --rcfile <(echo 'export PATH="'$(pwd)'/env/bin:$PATH"
source '$(pwd)'/env/bin/activate') -i
}

faire_venv() {
    "${APPIMAGE_OUT}" -m venv env
    local appimage_abs
    appimage_abs="$(readlink -f "${APPIMAGE_OUT}")"
    sed -i "s|^home = .*|home = $(dirname "$appimage_abs")|" env/pyvenv.cfg
    sed -i "s|^executable = .*|executable = $appimage_abs|" env/pyvenv.cfg
    ln -sf "$appimage_abs" "env/bin/myFRpy3"
    ln -sf "$appimage_abs" "env/bin/myFRpy"
    ln -sf "$appimage_abs" "env/bin/${BIN_EXEC}"
}

faire_nettoyer() {
    rm -rf "${DIR_SHIP}" "${DIR_OUTPUT}" "env"
    find "${DIR_INPUT}" -name "*.pyc" -delete
    find "${DIR_INPUT}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
}

faire_executer() {
    "${APPIMAGE_OUT}"
}

appeler_terminal() {
    local title="$1"
    local cmd="$2"
    xfce4-terminal --title="${title}" -e "bash -c '${cmd}'"
}

afficher_menu() {
    clear
    echo ""
    echo "  c : construire"
    echo "  e : executer"
    echo "  f : nettoyer"
    echo "  m : env virtuel"
    echo "  o : ouvrir venv"
    echo "  s : sortir"
    echo ""
    printf "  > "
}

verifier_installation() {
    if [[ ! -d "../output" ]]; then
        echo "installation absente -- veuillez vérifier"
        echo "entrer pour continuer ..."
        read
    else
        copier_installation
    fi

    if [[ ! -d "$DIR_INPUT/$BIN_EXEC" ]]; then
        echo "$DIR_INPUT/$BIN_EXEC absent -- veuillez vérifier"
        echo "entrer pour quitter ..."
        read
        exit
    else
        verifier_appimagetool
    fi
}

verifier_appimagetool() {
    if ! command -v $APPIMAGE_BUILDER >/dev/null 2>&1; then
        echo "$APPIMAGE_BUILDER pas trouvé"
        echo "voir ici : https://github.com/AppImage/appimagetool"
        echo "entrer pour quitter ..."
        read
        exit
    fi
}

copier_installation() {
    mv "../output" "$DIR_INPUT/$BIN_EXEC"
}

boucle_menu() {
    local choice

    afficher_menu
    while IFS= read -r choice; do
        case "${choice}" in
            c) faire_construire ;;
            e) faire_executer ;;
            f) faire_nettoyer ;;
            m) faire_venv ;;
            o) ouvrir_venv ;;
            s) exit 0 ;;
            "") afficher_menu; continue ;;
            *) echo "  option inconnue : ${choice}" ;;
        esac
        printf "  > "
    done
}

# --- principal ---

# si lancé depuis le bureau (sans tty), ouvrir un terminal et se relancer
if [ ! -t 0 ]; then
    appeler_terminal "${BIN_EXEC} lanceur" "bash -i '$(readlink -f "$0")'"
    exit 0
fi

boucle_menu