# Copyright (c) 2017 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%global libname      libargon2
%global gh_commit    1c4fc41f81f358283755eea88d4ecd05e43b7fd3
%global gh_short     %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner     P-H-C
%global gh_project   phc-winner-argon2
%global soname       0

%define ns_prefix ea
%define base_name argon2
%define pkg_base  %{libname}
%define pkg_name  %{ns_prefix}-%{pkg_base}
%define _prefix   /opt/cpanel/%{pkg_base}
%define prefix_dir /opt/cpanel/%{pkg_base}
%define prefix_lib %{prefix_dir}/%{_lib}
%define prefix_bin %{prefix_dir}/bin
%define prefix_inc %{prefix_dir}/include
%define _unpackaged_files_terminate_build 0
%define _defaultdocdir %{_prefix}/share/doc

%global upstream_version 20161029
#global upstream_prever  RC1

Name:    %{ns_prefix}-%{base_name}
Version: %{upstream_version}%{?upstream_prever:~%{upstream_prever}}
%define  release_prefix 3
Release: %{release_prefix}%{?dist}.cpanel
Vendor:  cPanel, Inc.
Group:   Applications/System
Summary: The password-hashing tools

BuildRoot: %{_tmppath}/%{pkg_name}-%{version}-%{release}-root

License: Public Domain or ASL 2.0
URL:     https://github.com/%{gh_owner}/%{gh_project}
Source0: https://github.com/%{gh_owner}/%{gh_project}/archive/%{gh_commit}/%{gh_project}-%{upstream_version}%{?upstream_prever}-%{gh_short}.tar.gz

Requires: %{pkg_name}%{?_isa} = %{version}-%{release}


%description
Argon2 is a password-hashing function that summarizes the state of the art
in the design of memory-hard functions and can be used to hash passwords
for credential storage, key derivation, or other applications.

It has a simple design aimed at the highest memory filling rate and
effective use of multiple computing units, while still providing defense
against tradeoff attacks (by exploiting the cache and memory organization
of the recent processors).

Argon2 has three variants: Argon2i, Argon2d, and Argon2id.

* Argon2d is faster and uses data-depending memory access, which makes it
  highly resistant against GPU cracking attacks and suitable for applications
  with no threats from side-channel timing attacks (eg. cryptocurrencies).
* Argon2i instead uses data-independent memory access, which is preferred for
  password hashing and password-based key derivation, but it is slower as it
  makes more passes over the memory to protect from tradeoff attacks.
* Argon2id is a hybrid of Argon2i and Argon2d, using a combination of
  data-depending and data-independent memory accesses, which gives some of
  Argon2i's resistance to side-channel cache timing attacks and much of
  Argon2d's resistance to GPU cracking attacks.


%package -n %{pkg_name}
Group:    System Environment/Libraries
Summary:  The password-hashing library

%description -n %{pkg_name}
Argon2 is a password-hashing function that summarizes the state of the art
in the design of memory-hard functions and can be used to hash passwords
for credential storage, key derivation, or other applications.


%package -n %{pkg_name}-devel
Group:    Development/Libraries
Summary:  Development files for %{pkg_name}
Requires: %{pkg_name}%{?_isa} = %{version}-%{release}

%description -n %{pkg_name}-devel
The %{pkg_name}-devel package contains libraries and header files for
developing applications that use %{pkg_name}.


%prep
%setup -qn %{gh_project}-%{gh_commit}

if ! grep -q 'soname,%{libname}.so.%{soname}' Makefile; then
  : soname have changed
  grep soname Makefile
  exit 1
fi

# Fix pkgconfig file
sed -e 's:lib/@HOST_MULTIARCH@:%{_lib}:;s/@UPSTREAM_VER@/%{version}/' -i %{libname}.pc

# Honours default RPM build options and library path, do not use -march=native
sed -e 's:-O3 -Wall:%{optflags}:' \
    -e '/^LIBRARY_REL/s:lib:%{_lib}:' \
    -e 's:-march=\$(OPTTARGET) :${CFLAGS} :' \
    -e 's:CFLAGS += -march=\$(OPTTARGET)::' \
    -i Makefile

%build
# parallel build is not supported
make -j1


%install
make install DESTDIR=%{buildroot} PREFIX=%{prefix_dir}

# Drop static library
rm %{buildroot}%{_libdir}/%{libname}.a

# Create link to soname, see Makefile for value
mv %{buildroot}%{_libdir}/%{libname}.so %{buildroot}%{_libdir}/%{libname}.so.%{soname}
ln -s %{libname}.so.%{soname} %{buildroot}%{_libdir}/%{libname}.so

# pkgconfig file
install -Dpm 644 %{libname}.pc %{buildroot}%{_libdir}/pkgconfig/%{libname}.pc

# Fix perms
chmod -x %{buildroot}%{_includedir}/%{base_name}.h


%check
make test


%post   -n %{pkg_name} -p /sbin/ldconfig
%postun -n %{pkg_name} -p /sbin/ldconfig


%files
%{_bindir}/%{base_name}

%files -n %{pkg_name}
%{!?_licensedir:%global license %%doc}
%license LICENSE
%{_libdir}/%{libname}.so.%{soname}

%files -n %{pkg_name}-devel
%doc *md
%{_includedir}/%{base_name}.h
%{_libdir}/%{libname}.so
%{_libdir}/pkgconfig/%{libname}.pc


%changelog
* Mon Jan 28 2019 Tim Mullin <tim@cpanel.net> - 20161029-3
- EA-7397: Added package to be distributed with EA4

* Thu Nov 16 2017 Milan Broz <gmazyland@gmail.com> - 20161029-2
- Do not use -march=native in build, use system flags (rh #1512845).

* Wed Oct 18 2017 Remi Collet <remi@remirepo.net> - 20161029-1
- initial package
