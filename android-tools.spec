#
# Conditional build:
%bcond_without	system_libusb	# system libusb library (ssplus support required)
%bcond_with	sse2		# SSE2 instructions

%ifarch %{x8664} x32 pentium4
%define	with_sse2	1
%endif
Summary:	Android platform tools
Summary(pl.UTF-8):	Narzędzia dla platformy Android
Name:		android-tools
Version:	35.0.2
Release:	3
# The entire source code is ASL 2.0 except boringssl which is BSD
License:	ASL 2.0, BSD
Group:		Applications/System
#Source0Download: https://github.com/nmeum/android-tools/releases
Source0:	https://github.com/nmeum/android-tools/releases/download/%{version}/%{name}-%{version}.tar.xz
# Source0-md5:	cc05807cb167d7fc8842df82aa3d4620
Source1:	51-android.rules
Source2:	adb.service
URL:		http://developer.android.com/guide/developing/tools/
BuildRequires:	cmake >= 3.12.0
BuildRequires:	golang
BuildRequires:	gtest-devel
BuildRequires:	libbrotli-devel
BuildRequires:	libfmt-devel
BuildRequires:	libstdc++-devel
%{?with_system_libusb:BuildRequires:	libusb-devel >= 1.0.28}
BuildRequires:	lz4-devel
BuildRequires:	pcre2-8-devel
BuildRequires:	perl-base
BuildRequires:	protobuf-devel
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 2.009
BuildRequires:	tar >= 1:1.22
BuildRequires:	udev-devel
BuildRequires:	xz
BuildRequires:	zlib-devel
BuildRequires:	zstd-devel
%ifarch %{ix86}
Requires:	cpuinfo(sse2)
%endif
%{?with_system_libusb:Requires:	libusb >= 1.0.28}
Requires:	systemd-units >= 38
ExclusiveArch:	%{go_arches}
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
phone flash.

%description -l pl.UTF-8
ADB (Android Debug Bridge - mostek diagnostyczny Android) służy do:
- śledzenia wszystkich instancji urządzeń i emulatorów Androida
  podłączonych lub uruchomionych na danej maszynie programisty

- implementowania różnych poleceń sterujących (np. "adb shell", "adb
  pull" itp.) do wykorzystania przez klientów (użytkowników linii
  poleceń, programów pomocniczych typu DDMS). Polecenia te są potem
  nazywane "usługami" w ADB.

Fastboot służy do operacji na partycjach flash telefonów Android. Może
także uruchomić telefon przy użyciu obrazu jądra lub obrazu głównego
systemu plików obecnego na maszynie programisty zamiast w pamięci
flash telefonu.

%package -n bash-completion-android-tools
Summary:	bash-completion for android-tools
Summary(pl.UTF-8):	Bashowe dopełnianie poleceń android-tools
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion >= 1:2.0
BuildArch:	noarch

%description -n bash-completion-android-tools
This package provides bash-completion for android-tools.

%description -n bash-completion-android-tools -l pl.UTF-8
Ten pakiet zapewnia dopełnianie poleceń narzędzi z pakietu
android-tools w powłoce bash.

%prep
%setup -q

%{__sed} -i -e '1 s,/usr/bin/env python3,%{__python3},' \
	vendor/avb/avbtool.py \
	vendor/libufdt/utils/src/mkdtboimg.py \
	vendor/mkbootimg/mkbootimg.py \
	vendor/mkbootimg/repack_bootimg.py \
	vendor/mkbootimg/unpack_bootimg.py

# don't package empty dir
rmdir vendor/adb/docs/dev/adb_wifi_assets

%build
export GO111MODULE=off
install -d build
cd build
%ifarch %{ix86}
%if %{with sse2}
CFLAGS="%{rpmcflags} -msse2"
CXXFLAGS="%{rpmcxxflags} -msse2"
%endif
%endif
%cmake .. \
	%{!?with_system_libusb:-DANDROID_TOOLS_USE_BUNDLED_LIBUSB:BOOL=ON} \
	-DANDROID_TOOLS_LIBUSB_ENABLE_UDEV:BOOL=ON \
	-DBUILD_SHARED_LIBS:BOOL=OFF \
	%{!?with_sse2:-DOPENSSL_NO_ASM:BOOL=ON}

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
%doc vendor/adb/{NOTICE,README.md} vendor/adb/docs/dev
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
%attr(755,root,root) %{_bindir}/make_f2fs
%attr(755,root,root) %{_bindir}/mkbootimg
%attr(755,root,root) %{_bindir}/mkdtboimg
%attr(755,root,root) %{_bindir}/repack_bootimg
%attr(755,root,root) %{_bindir}/sload_f2fs
%attr(755,root,root) %{_bindir}/unpack_bootimg
/lib/udev/rules.d/51-android.rules
%{systemdunitdir}/adb.service
%dir %{_datadir}/android-tools
%dir %{_datadir}/android-tools/completions
%{_datadir}/android-tools/completions/adb
%{_datadir}/android-tools/completions/fastboot
%dir %{_datadir}/android-tools/mkbootimg
%{_datadir}/android-tools/mkbootimg/mkbootimg.py
%dir %{_datadir}/android-tools/mkbootimg/gki
%{_datadir}/android-tools/mkbootimg/gki/generate_gki_certificate.py
%dir /var/lib/adb
%{_mandir}/man1/adb.1*

%files -n bash-completion-android-tools
%defattr(644,root,root,755)
%{bash_compdir}/adb
%{bash_compdir}/fastboot
