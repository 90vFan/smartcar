sudo apt-get install build-essential cmake unzip pkg-config libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libcanberra-gtk* libatlas-base-dev gfortran python3-dev

cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D OPENCV_GENERATE_PKGCONFIG=YES \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/home/pi/packages/opencv_contrib/modules \
    -D BUILD_TESTS=OFF \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D INSTALL_C_EXAMPLES=ON \
    -D BUILD_EXAMPLES=ON ..

make -j4
sudo make install
