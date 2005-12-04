Summary:	Dictionary database server
Summary(pl):	Serwer bazy s�ownik�w
Name:		dictd
Version:	1.10.2
Release:	2
License:	GPL
Group:		Networking/Daemons
Source0:	http://dl.sourceforge.net/dict/%{name}-%{version}.tar.gz
# Source0-md5:	5bafbdb3adfcfcc3d82fb219a8f50595
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-opt.patch
URL:		http://www.dict.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	judy-devel
BuildRequires:	libdbi-devel
BuildRequires:	perl-base
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
Requires:	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		specflags_ia32	 -fomit-frame-pointer 

%description
Server for the Dictionary Server Protocol (DICT), a TCP transaction
based query/response protocol that allows a client to access
dictionary definitions from a set of natural language dictionary
databases.

%description -l pl
Serwer dla Dictionary Server Protocol (DICT), bazuj�cego na TCP
protoko�u zapyta� i odpowiedzi umo�liwiaj�cego klientom na dost�p do
definicji s�ownikowych z zestawu baz danych.

%package devel
Summary:	Package for dictd plugins development
Summary(pl):	Pakiet programistyczny do tworzenia wtyczek dictd
Group:		Development/Libraries
# doesn't require base

%description devel
Package for dictd plugins development.

%description devel -l pl
Pakiet programistyczny do tworzenia wtyczek dictd.

%package plugin-dbi
Summary:	DBI plygin for dictd server
Summary(pl):	Wtyczka DBI dla serwera dictd
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description plugin-dbi
DBI plygin for dictd server.

%description plugin-dbi -l pl
Wtyczka DBI dla serwera dictd.

%package plugin-judy
Summary:	Judy plygin for dictd server
Summary(pl):	Wtyczka Judy dla serwera dictd
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description plugin-judy
Judy plygin for dictd server.

%description plugin-judy -l pl
Wtyczka Judy dla serwera dictd.

%package -n dict
Summary:	DICT Protocol Client
Summary(pl):	Klient protoko�u DICT
Group:		Applications/Networking

%description -n dict
Client for the Dictionary Server Protocol (DICT), a TCP transaction
based query/response protocol that provides access to dictionary
definitions from a set of natural language dictionary databases.

%description -n dict -l pl
Klient dla Dictionary Server Protocol (DICT), bazuj�cego na TCP
protoko�u zapyta� i odpowiedzi umo�liwiaj�cego klientom na dost�p do
definicji s�ownikowych z zestawu baz danych.

%package -n dictfmt
Summary:	dictfmt utility to convert databases in various formats into dict format
Summary(pl):	Narz�dzie dictfmt do konwersji baz w r�nych formatach na format dict
Group:		Applications/Text
Obsoletes:	dict-fmt

%description -n dictfmt
dictfmt utility is designed to convert databases in various formats
into working databases and indexes for the DICT server. This package
also includes other tools for formating databases:
dictfmt_{index2suffix,index2word,plugin,virtual} and dictunformat.

%description -n dictfmt -l pl
Narz�dzie dictfmt s�u�y do konwertowania baz danych w r�nych
formatach na dzia�aj�ce bazy danych i indeksy dla serwera s�ownik�w
DICT. Ten pakiet zawiera tak�e inne narz�dzia do formatowania baz:
dictfmt_{index2suffix,index2word,plugin,virtual} and dictunformat.

%package -n dictzip
Summary:	Compress (or expand) files, allowing random access
Summary(pl):	Kompresja (i dekompresja) plik�w pozwalaj�ca na swobodny dost�p
Group:		Applications/Archiving

%description -n dictzip
dictzip compresses files using the gzip(1) algorithm (LZ77) in a
manner which is completely compatible with the gzip file format. An
extension to the gzip file format (Extra Field, described in 2.3.1.1
of RFC 1952) allows extra data to be stored in the header of a
compressed file. Dictd, the DICT protocol dictionary server will make
use of this data to perform pseudo-random access on the file.

%description -n dictzip -l pl
dictzip kompresuje pliki korzystaj�c z zawartego w gzip(1) algorytmu
(LZ77) kt�ry jest ca�kowicie kompatybilny z formatem plik�w gzip.
Rozszerzenie do formatu plik�w gzip (pole dodatkowe, opisane w 2.3.1.1
RFC 1952) pozwalaj�cego na dodatkowe dane zapisane w nag��wku
skompresowanego pliku. Dictd, serwer protoko�u DICT wykorzystuje te
dane do pseudo-swobodnego dost�pu do pliku.

%prep
%setup -q
%patch0 -p1

# broken test if >1 plugins
%{__perl} -pi -e 's/test \$\(PLUGINS\)/test "\$\(PLUGINS\)"/' Makefile.in

%build
cp -f /usr/share/automake/config.* .
%{__aclocal}
%{__autoconf}
cd libmaa
cp -f /usr/share/automake/config.* .
%{__aclocal}
%{__autoconf}
cd ..
CFLAGS="%{rpmcflags} -DUID_NOBODY=99 -DGID_NOBODY=99"
%configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig,%{name}},%{_datadir}/%{name}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

echo "server localhost" > dict.conf
echo -e "access {\n\tallow localhost\n\tdeny *\n}\n" > %{name}-main.conf

install dict.conf $RPM_BUILD_ROOT%{_sysconfdir}
install dictd-main.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
:> $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

mv -f doc/security.doc security.txt

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
if [ -f /var/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} restart >&2
else
	echo "Run \"/etc/rc.d/init.d/%{name} start\" to start %{name} daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop >&2
	fi
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc ANNOUNCE NEWS README* TODO dictd.conf example* security.txt
%ghost %{_sysconfdir}/%{name}.conf
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}-main.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_sbindir}/%{name}
%dir %{_datadir}/%{name}
%{_mandir}/man8/%{name}*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dictdplugin-config
%{_includedir}/dictdplugin.h

%files plugin-dbi
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/dictdplugin_dbi.so

%files plugin-judy
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/dictdplugin_judy.so

%files -n dict
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dict.conf
%attr(755,root,root) %{_bindir}/colorit
%attr(755,root,root) %{_bindir}/dict
%attr(755,root,root) %{_bindir}/dictl
%{_mandir}/man1/colorit.1*
%{_mandir}/man1/dict.1*
%{_mandir}/man1/dictl.1*

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
