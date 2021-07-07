#!/bin/sh

set -x
"$(dirname "$0")/qt5/configure" \
    -commercial \
    -confirm-license \
    -developer-build \
    -xcb \
    -nomake examples \
    -skip qtconnectivity \
    -skip qtmultimedia \
    -skip qtpurchasing \
    -skip qtvirtualkeyboard \
    -skip qtwebengine \
    -skip qtwebsockets \
    -force-debug-info \
    -separate-debug-info \
    -gdb-index \
    -linker lld \
    QMAKE_CFLAGS+=-fno-omit-frame-pointer \
    QMAKE_CXXFLAGS+=-fno-omit-frame-pointer \
    "$@"
