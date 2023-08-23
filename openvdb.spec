# TODO: cuda in nanovdb
#
# Conditional build:
%bcond_with	apidocs		# API documentation (gs permission errors as of 10.0.1)
%bcond_with	llvm		# OpenVDB AX (requires LLVM in [10..14])
%bcond_without	static_libs	# static libraries
%bcond_with	avx		# AVX x86 SIMD instructions
%bcond_with	sse4		# SSE4.2 x86 SIMD instructions

Summary:	C++ library for sparse volumetric data discretized on three-dimensional grids
Summary(pl.UTF-8):	Biblioteka C++ do rzadkich danych wolumetrycznych dyskretyzowanych na siatkach trójwymiarowych
Name:		openvdb
Version:	10.0.1
Release:	4
License:	MPL v2.0
Group:		Libraries
#Source0Download: https://github.com/AcademySoftwareFoundation/openvdb/releases
Source0:	https://github.com/AcademySoftwareFoundation/openvdb/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	0239ff0c912a3eac76bd6a4ae1b03522
URL:		https://www.openvdb.org/
BuildRequires:	Imath-devel >= 2.4
BuildRequires:	OpenEXR-devel >= 2.4
BuildRequires:	boost-devel >= 1.73
BuildRequires:	c-blosc-devel >= 1.17.0
BuildRequires:	cmake >= 3.18
%{?with_apidocs:BuildRequires:	doxygen >= 1.8.8}
%{?with_apidocs:BuildRequires:	ghostscript}
BuildRequires:	glfw-devel >= 3.1
BuildRequires:	libpng-devel
BuildRequires:	libstdc++-devel >= 6:9.3.1
%if %{with llvm}
BuildRequires:	llvm-devel >= 10.0.0
BuildRequires:	llvm-devel < 15
%endif
BuildRequires:	log4cplus-devel >= 1.1.2
BuildRequires:	python3-devel >= 1:3.7
BuildRequires:	python3-numpy-devel >= 1.19.0
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 1.605
BuildRequires:	tbb-devel >= 2020.2
BuildRequires:	zlib-devel >= 1.2.7
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%ifarch %{ix86} x32
# ld (at last 2.41) fails to link with debuginfo (probably too big)
%define		_enable_debug_packages		0
%endif

%description
OpenVDB is an open source C++ library comprising a novel hierarchical
data structure and a large suite of tools for the efficient storage
and manipulation of sparse volumetric data discretized on
three-dimensional grids. It was developed by DreamWorks Animation for
use in volumetric applications typically encountered in feature film
production.

%description -l pl.UTF-8
OpenVDB to mająca otwarte źródła biblioteka C++, obejmująca nową
hierarchiczną strukturę danych oraz duży zbiór narzędzi do wydajnego
przechowywania i obrabiania rzadkich danych wolumetrycznych,
dyskretyzowanych na siatkach trójwymiarowych. Powstała w DreamWorks
Animation do zastosowań wolumetrycznych, zwykle spotykanych przy
produkcji filmów fabularnych.

%package devel
Summary:	Header files for OpenVDB library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki OpenVDB
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	Imath-devel >= 2.4
Requires:	OpenEXR-devel >= 2.4
Requires:	boost-devel >= 1.73
Requires:	libstdc++-devel >= 6:9.3.1
Requires:	tbb-devel >= 2020.2

%description devel
Header files for OpenVDB library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki OpenVDB.

%package static
Summary:	Static OpenVDB library
Summary(pl.UTF-8):	Statyczna biblioteka OpenVDB
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static OpenVDB library.

%description static -l pl.UTF-8
Statyczna biblioteka OpenVDB.

%package -n python3-pyopenvdb
Summary:	Python interface to OpenVDB library
Summary(pl.UTF-8):	Interfejs Pythona do biblioteki OpenVDB
Group:		Python/Libraries
Requires:	%{name} = %{version}-%{release}

%description -n python3-pyopenvdb
Python interface to OpenVDB library.

%description -n python3-pyopenvdb -l pl.UTF-8
Interfejs Pythona do biblioteki OpenVDB.

%package apidocs
Summary:	API documentation for OpenVDB library
Summary(pl.UTF-8):	Dokumentacja API biblioteki OpenVDB
Group:		Documentation
BuildArch:	noarch

%description apidocs
API documentation for OpenVDB library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki OpenVDB.

%prep
%setup -q

%build
%ifarch %{ix86} x32
# with default settings g++ fails with virtual memory exhausted on 32-bit x86 systems
CXXFLAGS="%{rpmcxxflags} --param ggc-min-expand=20 --param ggc-min-heapsize=65536"
%endif
%cmake -B build \
	-DCMAKE_INSTALL_DOCDIR=%{_docdir}/openvdb \
	%{?with_llvm:-DOPENVDB_BUILD_AX=ON} \
	%{?with_apidocs:-DOPENVDB_BUILD_DOCS=ON} \
	-DOPENVDB_BUILD_NANOVDB=ON \
	-DOPENVDB_BUILD_PYTHON_MODULE=ON \
	-DOPENVDB_ENABLE_RPATH=OFF \
%if %{with avx}
	-DOPENVDB_SIMD=AVX \
%else
%if %{with sse4}
	-DOPENVDB_SIMD=SSE42 \
%endif
%endif
	-DUSE_EXR=ON \
	-DUSE_LOG4CPLUS=ON \
	-DUSE_PNG=ON \

%{__make} -C build

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc CHANGES MAINTAINERS.md README.md
%attr(755,root,root) %{_bindir}/nanovdb_print
%attr(755,root,root) %{_bindir}/nanovdb_validate
%attr(755,root,root) %{_bindir}/vdb_print
%attr(755,root,root) %{_libdir}/libopenvdb.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libopenvdb.so.10.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libopenvdb.so
%{_includedir}/nanovdb
%{_includedir}/openvdb
%{_libdir}/cmake/OpenVDB

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libopenvdb.a
%endif

%files -n python3-pyopenvdb
%defattr(644,root,root,755)
%attr(755,root,root) %{py3_sitedir}/pyopenvdb.so

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%{_docdir}/openvdb
%endif
