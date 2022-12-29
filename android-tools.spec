Summary:	Android platform tools
Name:		android-tools
Version:	33.0.3p1
Release:	1
# The entire source code is ASL 2.0 except boringssl which is BSD
License:	ASL 2.0, BSD
Group:		Applications/System
Source0:	https://github.com/nmeum/android-tools/releases/download/%{version}/%{name}-%{version}.tar.xz
# Source0-md5:	d0474aac5d7ca6e02906705a5c9307ac
Source1:	51-android.rules
Source2:	adb.service
URL:		http://developer.android.com/guide/developing/tools/
BuildRequires:	cmake >= 3.12.0
BuildRequires:	golang
BuildRequires:	gtest-devel
BuildRequires:	libbrotli-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libusb-devel
BuildRequires:	lz4-devel
BuildRequires:	pcre2-8-devel
BuildRequires:	perl-base
BuildRequires:	protobuf-devel
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 1.605
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	zlib-devel
BuildRequires:	zstd-devel
Requires:	systemd-units >= 38
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Android Debug Bridge (ADB) is used to:

- keep track of all Android devices and emulators instances connected
  to or running on a given host developer machine

- implement various control commands (e.g. "adb shell", "adb pull",
  etc.) for the benefit of clients (command-line users, or helper
  programs like DDMS). These commands are what is called a 'service' in
  ADB.

Fastboot is used to manipulate the flash partitions of the Android
phone. It can also boot the phone using a kernel image or root
filesystem image which reside on the host machine rather than in the
phone flash. In order to use it, it is important to understand the
flash partition layout for the phone. The fastboot program works in
conjunction with firmware on the phone to read and write the flash
partitions. It needs the same USB device setup between the host and
the target phone as adb.

%package -n bash-completion-android-tools
Summary:	bash-completion for android-tools
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion >= 1:2.0
BuildArch:	noarch

%description -n bash-completion-android-tools
This package provides bash-completion for android-tools.

%prep
%setup -q

%{__sed} -i -e '1 s,#!.*env python3,#!%{__python3},' \
	vendor/mkbootimg/mkbootimg.py \
	vendor/mkbootimg/unpack_bootimg.py \
	vendor/avb/avbtool.py \
	vendor/mkbootimg/repack_bootimg.py \
	vendor/libufdt/utils/src/mkdtboimg.py

%build
export GO111MODULE=off
install -d build
cd build
%cmake .. \
	-DBUILD_SHARED_LIBS:BOOL=OFF

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{systemdunitdir},/var/lib/adb,/lib/udev/rules.d}

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

cp -p %{SOURCE1} $RPM_BUILD_ROOT/lib/udev/rules.d/51-android.rules
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{systemdunitdir}/adb.service

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post adb.service

%preun
%systemd_preun adb.service

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc vendor/adb/{OVERVIEW.TXT,SERVICES.TXT,NOTICE,protocol.txt}
%attr(755,root,root) %{_bindir}/adb
%attr(755,root,root) %{_bindir}/avbtool
%attr(755,root,root) %{_bindir}/mke2fs.android
%attr(755,root,root) %{_bindir}/simg2img
%attr(755,root,root) %{_bindir}/img2simg
%attr(755,root,root) %{_bindir}/fastboot
%attr(755,root,root) %{_bindir}/append2simg
%attr(755,root,root) %{_bindir}/e2fsdroid
%attr(755,root,root) %{_bindir}/ext2simg
%attr(755,root,root) %{_bindir}/lpadd
%attr(755,root,root) %{_bindir}/lpdump
%attr(755,root,root) %{_bindir}/lpflash
%attr(755,root,root) %{_bindir}/lpmake
%attr(755,root,root) %{_bindir}/lpunpack
%attr(755,root,root) %{_bindir}/mkbootimg
%attr(755,root,root) %{_bindir}/mkdtboimg
%attr(755,root,root) %{_bindir}/repack_bootimg
%attr(755,root,root) %{_bindir}/unpack_bootimg
/lib/udev/rules.d/51-android.rules
%{systemdunitdir}/adb.service
%dir %{_datadir}/android-tools
%dir %{_datadir}/android-tools/completions
%{_datadir}/android-tools/completions/adb
%{_datadir}/android-tools/completions/fastboot
%dir %{_datadir}/android-tools/mkbootimg
%{_datadir}/android-tools/mkbootimg/gki/generate_gki_certificate.py
%{_datadir}/android-tools/mkbootimg/mkbootimg.py
%dir /var/lib/adb

%files -n bash-completion-android-tools
%defattr(644,root,root,755)
%{bash_compdir}/adb
%{bash_compdir}/fastboot
