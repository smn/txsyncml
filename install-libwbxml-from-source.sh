wget http://downloads.sourceforge.net/project/libwbxml/libwbxml/0.11.2/libwbxml-0.11.2.tar.gz &&
tar zxvf libwbxml-0.11.2.tar.gz &&
cd libwbxml-0.11.2 &&
mkdir build &&
cd build &&
cmake -DCMAKE_INSTALL_PREFIX=$prefix ../ &&
make &&
make test &&
make install