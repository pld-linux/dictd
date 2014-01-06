Summary:	Dictionary database server
Summary(pl.UTF-8):	Serwer bazy słowników
Name:		dictd
Version:	1.12.1
Release:	1
License:	GPL v1+
Group:		Networking/Daemons
Source0:	http://downloads.sourceforge.net/dict/%{name}-%{version}.tar.gz
# Source0-md5:	62696491174c22079f664830d07c0623
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-umask.patch
URL:		http://www.dict.org/
BuildRequires:	autoconf >= 2.53
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	judy-devel
BuildRequires:	libdbi-devel
BuildRequires:	libmaa-devel
BuildRequires:	perl-base
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		skip_post_check_so	dictdplugin_judy.so.*

# plugins dir
%define		_libexecdir	%{_libdir}/dictd

%define		specflags_ia32	 -fomit-frame-pointer

%description
Server for the Dictionary Server Protocol (DICT), a TCP transaction
based query/response protocol that allows a client to access
dictionary definitions from a set of natural language dictionary
databases.

%description -l pl.UTF-8
Serwer dla Dictionary Server Protocol (DICT), bazującego na TCP
protokołu zapytań i odpowiedzi umożliwiającego klientom na dostęp do
definicji słownikowych z zestawu baz danych.

%package devel
Summary:	Package for dictd plugins development
Summary(pl.UTF-8):	Pakiet programistyczny do tworzenia wtyczek dictd
Group:		Development/Libraries
# doesn't require base

%description devel
Package for dictd plugins development.

%description devel -l pl.UTF-8
Pakiet programistyczny do tworzenia wtyczek dictd.

%package plugin-dbi
Summary:	DBI plugin for dictd server
Summary(pl.UTF-8):	Wtyczka DBI dla serwera dictd
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description plugin-dbi
DBI plugin for dictd server.

%description plugin-dbi -l pl.UTF-8
Wtyczka DBI dla serwera dictd.

%package plugin-judy
Summary:	Judy plugin for dictd server
Summary(pl.UTF-8):	Wtyczka Judy dla serwera dictd
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description plugin-judy
Judy plugin for dictd server.

%description plugin-judy -l pl.UTF-8
Wtyczka Judy dla serwera dictd.

%package -n dict
Summary:	DICT Protocol Client
Summary(pl.UTF-8):	Klient protokołu DICT
Group:		Applications/Networking

%description -n dict
Client for the Dictionary Server Protocol (DICT), a TCP transaction
based query/response protocol that provides access to dictionary
definitions from a set of natural language dictionary databases.

%description -n dict -l pl.UTF-8
Klient dla Dictionary Server Protocol (DICT), bazującego na TCP
protokołu zapytań i odpowiedzi umożliwiającego klientom na dostęp do
definicji słownikowych z zestawu baz danych.

%package -n dictfmt
Summary:	dictfmt utility to convert databases in various formats into dict format
Summary(pl.UTF-8):	Narzędzie dictfmt do konwersji baz w różnych formatach na format dict
Group:		Applications/Text
Obsoletes:	dict-fmt

%description -n dictfmt
dictfmt utility is designed to convert databases in various formats
into working databases and indexes for the DICT server. This package
also includes other tools for formating databases:
dictfmt_{index2suffix,index2word,plugin,virtual} and dictunformat.

%description -n dictfmt -l pl.UTF-8
Narzędzie dictfmt służy do konwertowania baz danych w różnych
formatach na działające bazy danych i indeksy dla serwera słowników
DICT. Ten pakiet zawiera także inne narzędzia do formatowania baz:
dictfmt_{index2suffix,index2word,plugin,virtual} and dictunformat.

%package -n dictzip
Summary:	Compress (or expand) files, allowing random access
Summary(pl.UTF-8):	Kompresja (i dekompresja) plików pozwalająca na swobodny dostęp
Group:		Applications/Archiving

%description -n dictzip
dictzip compresses files using the gzip(1) algorithm (LZ77) in a
manner which is completely compatible with the gzip file format. An
extension to the gzip file format (Extra Field, described in 2.3.1.1
of RFC 1952) allows extra data to be stored in the header of a
compressed file. Dictd, the DICT protocol dictionary server will make
use of this data to perform pseudo-random access on the file.

%description -n dictzip -l pl.UTF-8
dictzip kompresuje pliki korzystając z zawartego w gzip(1) algorytmu
(LZ77) który jest całkowicie kompatybilny z formatem plików gzip.
Rozszerzenie do formatu plików gzip (pole dodatkowe, opisane w 2.3.1.1
RFC 1952) pozwalającego na dodatkowe dane zapisane w nagłówku
skompresowanego pliku. Dictd, serwer protokołu DICT wykorzystuje te
dane do pseudo-swobodnego dostępu do pliku.

%prep
%setup -q
%patch0 -p1

%build
cp -f /usr/share/automake/config.* .
%{__aclocal}
%{__autoconf}
CFLAGS="%{rpmcflags} -DUID_NOBODY=99 -DGID_NOBODY=99"
%configure \
	--with-plugin-dbi \
	--with-plugin-judy \
	--with-system-utf8-funcs

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{_sysconfdir}/%{name},%{_datadir}/%{name}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

echo "server localhost" > dict.conf
echo -e "access {\n\tallow localhost\n\tdeny *\n}\n" > %{name}-main.conf

install dict.conf $RPM_BUILD_ROOT%{_sysconfdir}
install dictd-main.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
:> $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%{__rm} $RPM_BUILD_ROOT%{_libexecdir}/dictdplugin_*.{la,a}

mv -f doc/security.doc security.txt

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%service dictd restart

%preun
if [ "$1" = "0" ]; then
	%service dictd stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc ANNOUNCE ChangeLog NEWS README TODO examples/dictd* security.txt
%ghost %{_sysconfdir}/%{name}.conf
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}-main.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_sbindir}/%{name}
%dir %{_datadir}/%{name}
%dir %{_libexecdir}
%{_mandir}/man8/dictd.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dictdplugin-config
%{_includedir}/dictdplugin.h

%files plugin-dbi
%defattr(644,root,root,755)
%attr(755,root,root) %{_libexecdir}/dictdplugin_dbi.so*

%files plugin-judy
%defattr(644,root,root,755)
%attr(755,root,root) %{_libexecdir}/dictdplugin_judy.so*

%files -n dict
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dict.conf
%attr(755,root,root) %{_bindir}/colorit
%attr(755,root,root) %{_bindir}/dict
%attr(755,root,root) %{_bindir}/dictl
%attr(755,root,root) %{_bindir}/dict_lookup
%{_mandir}/man1/colorit.1*
%{_mandir}/man1/dict.1*
%{_mandir}/man1/dictl.1*
%{_mandir}/man1/dict_lookup.1*

%files -n dictfmt
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dictfmt*
%attr(755,root,root) %{_bindir}/dictunformat
%{_mandir}/man1/dictfmt*.1*
%{_mandir}/man1/dictunformat.1*

%files -n dictzip
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dictzip
%{_mandir}/man1/dictzip.1*
