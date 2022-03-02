#!/bin/sh

set -x

export CFLAGS=-fno-omit-frame-pointer
export CXXFLAGS=-fno-omit-frame-pointer

"$(dirname "$0")/qt-dev/configure" \
    -commercial \
    -confirm-license \
    -developer-build \
    -xcb \
    -nomake examples \
    -skip qtcoap \
    -skip qtconnectivity \
    -skip qtgraphicaleffects \
    -skip qtlocation \
    -skip qtmultimedia \
    -skip qtopcua \
    -skip qtpurchasing \
    -skip qtquickcontrols2 \
    -skip qtscxml \
    -skip qtsensors \
    -skip qtserialbus \
    -skip qtvirtualkeyboard \
    -skip qtwebengine \
    -skip qtwebsockets \
    -force-asserts \
    -force-debug-info \
    -separate-debug-info \
    -gdb-index \
    -linker lld \
    -ccache \
    "$@"
