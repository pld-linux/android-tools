%define		rel	1
%define		git_date 20160327
%define		git_commit 3761365735de
%define		packdname core-%{git_commit}
%define		extras_git_commit 7f5999a
%define		extras_packdname extras-%{extras_git_commit}
Summary:	Android platform tools(adb, fastboot)
Name:		android-tools
# use platform version from git (git describe --tags)
# core: android-6.0.1_r21
# extras: android-6.0.1_r68
Version:	6.0.1
Release:	0.%{git_date}git%{git_commit}.%{rel}
Group:		Applications/System
# The entire source code is ASL 2.0 except fastboot/ which is BSD
License:	ASL 2.0 and (ASL 2.0 and BSD)
#  using git archive since upstream hasn't created tarballs.
#  git archive --format=tar --prefix=%%{packdname}/ %%{git_commit} adb fastboot libzipfile libcutils libmincrypt libsparse mkbootimg include/cutils include/zipfile include/mincrypt include/utils include/private | xz  > %%{packdname}.tar.xz
#  https://android.googlesource.com/platform/system/core.git
#  git archive --format=tar --prefix=extras/ %%{extras_git_commit} ext4_utils f2fs_utils | xz  > %%{extras_packdname}.tar.xz
#  https://android.googlesource.com/platform/system/extras.git
Source0:	http://pkgs.fedoraproject.org/repo/pkgs/android-tools/%{packdname}.tar.xz/bdccaa042b73d1f5a29630c69ae5df26/%{packdname}.tar.xz
# Source0-md5:	bdccaa042b73d1f5a29630c69ae5df26
Source1:	http://pkgs.fedoraproject.org/repo/pkgs/android-tools/%{extras_packdname}.tar.xz/2cd5ea576fdf35f5e9ee1c208f6d9fa5/%{extras_packdname}.tar.xz
# Source1-md5:	2cd5ea576fdf35f5e9ee1c208f6d9fa5
Source2:	generate_build.rb
Source5:	51-android.rules
Source6:	adb.service
Patch1:		0001-Add-string-h.patch
URL:		http://developer.android.com/guide/developing/tools/
BuildRequires:	f2fs-tools
BuildRequires:	gtest-devel
BuildRequires:	libselinux-devel
BuildRequires:	openssl-devel
BuildRequires:	rpmbuild(macros) >= 1.671
BuildRequires:	ruby
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

%patch1 -p1
cp -p %{SOURCE5} 51-android.rules

%build
%{__ruby} %{SOURCE2} | tee build.sh
PKGVER=%{git_commit} sh -xe build.sh

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{systemdunitdir},%{_sharedstatedir}/adb}
install -p adb/adb fastboot/fastboot libsparse/simg2img libsparse/img2simg $RPM_BUILD_ROOT%{_bindir}

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
%attr(755,root,root) %{_bindir}/img2simg
%attr(755,root,root) %{_bindir}/simg2img
# ASL2.0 and BSD.
%attr(755,root,root) %{_bindir}/fastboot

%{systemdunitdir}/adb.service
%dir %{_sharedstatedir}/adb
