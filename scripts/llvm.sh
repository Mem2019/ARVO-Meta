set -e

echo "Starting to build and install LLVM."

unset CFLAGS
unset CXXFLAGS
unset LDFLAGS

apt-get update
apt-get install -y ninja-build wget

wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh -O /tmp/Miniconda3.sh
sha256sum /tmp/Miniconda3.sh | grep 78f39f9bae971ec1ae7969f0516017f2413f17796670f7040725dd83fcff5689
bash /tmp/Miniconda3.sh -b
$HOME/miniconda3/bin/conda init
$HOME/miniconda3/bin/conda create --name py9 python=3.9 -y
$HOME/miniconda3/bin/conda install -n py9 -c conda-forge gcc gxx -y
$HOME/miniconda3/bin/conda config --set auto_activate_base false
source $($HOME/miniconda3/bin/conda info --base)/etc/profile.d/conda.sh
conda activate py9

cd /root
wget https://github.com/llvm/llvm-project/releases/download/llvmorg-12.0.1/clang+llvm-12.0.1-x86_64-linux-gnu-ubuntu-16.04.tar.xz
tar xf clang+llvm-12.0.1-x86_64-linux-gnu-ubuntu-16.04.tar.xz
export PATH="/root/clang+llvm-12.0.1-x86_64-linux-gnu-ubuntu-/bin:$PATH"
export CC=clang
export CXX=clang++

cd /root
git clone --depth=1 https://github.com/llvm/llvm-project.git
cd llvm-project
git fetch origin --depth=1 ae42196bc493ffe877a7e3dff8be32035dea4d07
git reset --hard ae42196bc493ffe877a7e3dff8be32035dea4d07

wget https://github.com/Kitware/CMake/releases/download/v3.25.1/cmake-3.25.1-linux-x86_64.tar.gz -O cmake.tar.gz
tar -xf cmake.tar.gz

mkdir build && cd build && mkdir /llvm-16
../cmake-3.25.1-linux-x86_64/bin/cmake -G "Ninja" \
	-DCMAKE_C_COMPILER=clang \
	-DCMAKE_CXX_COMPILER=clang++ \
	-DCMAKE_BUILD_TYPE=Release -DLLVM_TARGETS_TO_BUILD=host \
	-DLLVM_ENABLE_PROJECTS="clang;compiler-rt;lld" \
	-DCMAKE_INSTALL_PREFIX="/llvm-16" \
	-DLLVM_INSTALL_BINUTILS_SYMLINKS=ON $PWD/../llvm/
ninja -j $(nproc) && ninja install
cd /root && rm -rf llvm-project
rm -rf clang+llvm-12.0.1-x86_64-linux-gnu-ubuntu-16.04.tar.xz clang+llvm-12.0.1-x86_64-linux-gnu-ubuntu-