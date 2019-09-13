eIQ Heterogenous DEMO i.MX8MMini
================================
This a basic smart door implementation using face recognition. The usage scenario is the following:
- All Cortex-A's and attached peripherals are in sleep mode
- A user comes and wakes the system by saying the keyword 'GO'
- All Cortex-A's and attached peripherals wake up
- The user can try face recognition to unlock the door

The implementation of the demo is based on the [eIQ ML Software Development Environment](https://www.nxp.com/eIQ):
- Cortex A53: eIQ OpenCV Face Detection & Recognition ([Yocto integrated]([https://www.nxp.com/design/software/development-software/eiq-ml-development-environment/eiq-opencv-neural-network-and-ml-algorithm-support:eIQOpenCV](https://www.nxp.com/design/software/development-software/eiq-ml-development-environment/eiq-opencv-neural-network-and-ml-algorithm-support:eIQOpenCV)))
- Cortex M4: eIQ CMSIS-NN Keyword Spotting ([ported from RT](https://www.nxp.com/design/software/development-software/eiq-ml-development-environment/eiq-for-arm-cmsis-nn:eIQArmCMSISNN))

HW requirements
---------------
- [i.MX 8MMini Kit](https://www.nxp.com/products/processors-and-microcontrollers/arm-processors/i.mx-applications-processors/i.mx-8-processors/i.mx-8m-mini-arm-cortex-a53-cortex-m4-audio-voice-video:i.MX8MMINI)
- Touch screen display (preferred resolution 1920x1080)
NOTE: if the display does not support touch, a mouse can be connected to the board and used instead
- [MIPI-CSI Camera module](https://www.nxp.com/part/MINISASTOCSI)
- Microphone: [Synaptics CONEXANT AudioSmart® DS20921](https://www.synaptics.com/partners/amazon/ds20921)
- Ribbon, 4 female-female wires and 60 pins connector to connect mic to board
- Optional: headphones

Run the demo
------------
### Start Key Word Spotting on Cortex M4:
Stop in u-boot and run the kws.bin executable in DDR:
```
u-boot=>fatload mmc 0 0x80000000 kws.bin
u-boot=>dcache flush
u-boot=>bootaux 0x80000000
u-boot=>boot
```
### Start Face Recognition on Cortex-A:
##### Insert updated rpmsg driver located in $HOME foder:
```bash
$: cd ~
$: modprobe imx_rpmsg_pingpong
```
##### First time only
```bash
$: cd ~/eiq-hetero
$: python3 wrap_migrate.py
$: python3 wrap_createsuperuser.py
```
##### Start:
```bash
$: python3 manage.py runserver 0.0.0.0:8000 --noreload &
$: /opt/src/bin/src
```
**NOTE:** the first instruction will start the django server, the second instruction will show the pin-pad on the display.

### Browser access from HOST PC:
- [http://$BOARD_IP:8000/dashboard/](http://board_ip:8000/dashboard/): Dashboard that facilitates managing users and view access logs.
- [http://$BOARD_IP:8000/admin/](http://board_ip:8000/admin/): manage users database 

Build instructions
------------------
### Yocto image with eIQ OpenCV and hetero demo layer
**Requirements:** Ubuntu 16 Host PC 
1. Project initialization
```bash
$: mkdir imx-linux-bsp
$: cd imx-linux-bsp
$: repo init -u https://source.codeaurora.org/external/imx/imx-manifest -b imx-linux-sumo -m imx-4.14.98-2.0.0_machinelearning.xml
$: repo sync
$: EULA=1 MACHINE=imx8mmevk DISTRO=fsl-imx-xwayland source ./fsl-setup-release.sh -b bld-xwayland
```
2. Clone **meta-eiq-hetero** demo layer in **${BSPDIR}/sources/**
3. Add eIQ and demo layers. Add the following line into conf/bblayers.conf:
```
BBLAYERS += " ${BSPDIR}/sources/meta-imx-machinelearning "
BBLAYERS += " ${BSPDIR}/sources/meta-eiq-hetero "
```
4. Enable eIQ and other dependencies. Add the following lines into conf/local.conf:
```
EXTRA_IMAGE_FEATURES = " dev-pkgs debug-tweaks tools-debug \
                         tools-sdk ssh-server-openssh"
 
IMAGE_INSTALL_append = " net-tools iputils dhcpcd which gzip \
                         python3 python3-pip wget cmake gtest \
                         git zlib patchelf nano grep vim tmux \
                         swig tar unzip parted \
                         e2fsprogs e2fsprogs-resize2fs"

IMAGE_INSTALL_append = " python3-pytz python3-django-cors-headers"
 
IMAGE_INSTALL_append = " opencv python3-opencv"
PACKAGECONFIG_append_pn-opencv_mx8 = " dnn python3 qt5 jasper \
                                       openmp test neon"
 
PACKAGECONFIG_remove_pn-opencv_mx8 = "opencl"
PACKAGECONFIG_remove_pn-arm-compute-library = "opencl"
 
TOOLCHAIN_HOST_TASK_append = " nativesdk-cmake nativesdk-make"
 
PREFERRED_VERSION_opencv = "4.0.1%"
PREFERRED_VERSION_python3-django = "2.1%"
 
IMAGE_ROOTFS_EXTRA_SPACE = "20971520"
```
5. Bake the image:
```bash
$: bitbake image-eiq-hetero
```

6. Apply patches:
```bash
$: cd ${BSPDIR}/bld-xwayland/tmp/work-shared/imx8mmlpddr4evk/kernel-source
$: git apply eiq-hetero-linux-imx.patch
$: cd ${BSPDIR}/bld-xwayland/tmp/work/imx8mmddr4evk-poky-linux/imx-atf/2.0+gitAUTOINC+1cb68fa0a0-r0/git 
$: git apply eiq-hetero-imx-atf.patch
```
- Rebuild kernel: ```$: bitbake linux-imx```
- Rebuild ATF: ```$: bitbake imx-atf```
- Update sdcard image with the new binaries: kernel image (Image), rpmsg ping-pong driver (imx_rpmsg_pingpong.ko), i.MX8MMini DTB (fsl-imx8mm-evk.dtb) and atf (imx-boot-imx8mmevk-sd.bin-flash_evk).
