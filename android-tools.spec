%define		rel	1
%define		git_date 20130123
%define		git_commit 98d0789
%define		packdname core-%{git_commit}
# last extras ext4_utils  commit without custom libselinux requirement
%define		extras_git_commit 4ff85ad
%define		extras_packdname extras-%{extras_git_commit}
Summary:	Android platform tools(adb, fastboot)
Name:		android-tools
# use platform version from git (git describe --tags)
# core: android-4.2.1_r1.1-281-g98d0789
# extras: android-cts-4.1_r4-101-g4ff85ad
Version:	4.2.1
Release:	0.%{git_date}git%{git_commit}.%{rel}
Group:		Applications/System
# The entire source code is ASL 2.0 except fastboot/ which is BSD
License:	ASL 2.0 and (ASL 2.0 and BSD)
#  using git archive since upstream hasn't created tarballs.
#  git archive --format=tar --prefix=%%{packdname}/ %%{git_commit} adb fastboot libzipfile libcutils libmincrypt libsparse mkbootimg include/cutils include/zipfile include/mincrypt | xz  > %%{packdname}.tar.xz
#  https://android.googlesource.com/platform/system/core.git
#  git archive --format=tar --prefix=extras/ %%{extras_git_commit} ext4_utils | xz  > %%{extras_packdname}.tar.xz
#  https://android.googlesource.com/platform/system/extras.git
Source0:	http://pkgs.fedoraproject.org/repo/pkgs/android-tools/core-98d0789.tar.xz/8852699267ef36482ea917cc4381f583/%{packdname}.tar.xz
# Source0-md5:	8852699267ef36482ea917cc4381f583
Source1:	http://pkgs.fedoraproject.org/repo/pkgs/android-tools/extras-4ff85ad.tar.xz/e6c0b8dd70952e97a068c3a61f812968/%{extras_packdname}.tar.xz
# Source1-md5:	e6c0b8dd70952e97a068c3a61f812968
Source2:	core-Makefile
Source3:	adb-Makefile
Source4:	fastboot-Makefile
Source5:	51-android.rules
Source6:	adb.service
URL:		http://developer.android.com/guide/developing/tools/
BuildRequires:	libselinux-devel
BuildRequires:	openssl-devel
BuildRequires:	rpmbuild(macros) >= 1.671
BuildRequires:	systemd-devel
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	zlib-devel
Requires:	systemd-units >= 38
Provides:	adb
Provides:	fastboot
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

%prep
%setup -qc -a1
mv %{packdname}/* .

cp -p %{SOURCE2} Makefile
cp -p %{SOURCE3} adb/Makefile
cp -p %{SOURCE4} fastboot/Makefile
cp -p %{SOURCE5} 51-android.rules

%build
%{__make} \
	CC="%{__cc}" \
	LD="%{__cc}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{systemdunitdir}}
%{__make} install \
	BINDIR=%{_bindir} \
	DESTDIR=$RPM_BUILD_ROOT

cp -p %{SOURCE6} $RPM_BUILD_ROOT%{systemdunitdir}/adb.service

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
%doc adb/OVERVIEW.TXT adb/SERVICES.TXT adb/NOTICE adb/protocol.txt 51-android.rules
# ASL2.0
%attr(755,root,root) %{_bindir}/adb
# ASL2.0 and BSD.
%attr(755,root,root) %{_bindir}/fastboot
%{systemdunitdir}/adb.service
