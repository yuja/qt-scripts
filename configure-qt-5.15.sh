#!/bin/sh

set -x
~/mirrors/qt5/configure \
    -commercial \
    -confirm-license \
    -xcb \
    -nomake examples \
    -skip qtconnectivity \
    -skip qtpurchasing \
    -skip qtwebengine \
    -force-debug-info \
    -separate-debug-info \
    -gdb-index \
    -linker lld \
    -prefix $HOME/opt/qt-5.15-`date -I` \
    QMAKE_CFLAGS+=-fno-omit-frame-pointer \
    QMAKE_CXXFLAGS+=-fno-omit-frame-pointer \
    "$@"
