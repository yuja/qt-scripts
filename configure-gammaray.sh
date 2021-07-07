#/!bin/sh

set -x

cmake -G Ninja \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX="$HOME/opt/gammaray" \
      -DCMAKE_PREFIX_PATH=$HOME/opt/qt-5.15 \
      ~/mirrors/GammaRay
