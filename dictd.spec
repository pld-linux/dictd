Summary:	Dictionary database server
Summary(pl):	Serwer bazy s³owników
Name:		dictd
Version:	1.9.11
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://dl.sourceforge.net/sourceforge/dict/%{name}-%{version}.tar.gz
# Source0-md5:	4d06aabf573c862fd29e409984f71a67
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-no_libnsl.patch
Patch1:		%{name}-opt.patch
URL:		http://www.dict.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libltdl-devel
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		specflags_ia32	"-fomit-frame-pointer"

%description
Server for the Dictionary Server Protocol (DICT), a TCP transaction
based query/response protocol that allows a client to access
dictionary definitions from a set of natural language dictionary
databases.

%description -l pl
Serwer dla Dictionary Server Protocol (DICT), bazuj±cego na TCP
protoko³u zapytañ i odpowiedzi umo¿liwiaj±cego klientom na dostêp do
definicji s³ownikowych z zestawu baz danych.

%package -n dict
Summary:	DICT Protocol Client
Summary(pl):	Klient protoko³u DICT
Group:		Applications/Networking

%description -n dict
Client for the Dictionary Server Protocol (DICT), a TCP transaction
based query/response protocol that provides access to dictionary
definitions from a set of natural language dictionary databases.

%description -n dict -l pl
Klient dla Dictionary Server Protocol (DICT), bazuj±cego na TCP
protoko³u zapytañ i odpowiedzi umo¿liwiaj±cego klientom na dostêp do
definicji s³ownikowych z zestawu baz danych.

%package -n dictfmt
Summary:	dictfmt utility to convert databases in various formats into dict format
Summary(pl):	Narzêdzie dictfmt do konwersji baz w ró¿nych formatach na format dict
Group:		Applications/Text
Obsoletes:	dict-fmt
Obsoletes:	dictfmt

%description -n dictfmt
dictfmt utility is designed to convert databases in various formats
into working databases and indexes for the DICT server.
This package also includes other tools for formating databases:
dictfmt_{index2suffix,index2word,plugin,virtual} and dictunformat.

%description -n dictfmt -l pl
Narzêdzie dictfmt s³u¿y do konwertowania baz danych w ró¿nych
formatach na dzia³aj±ce bazy danych i indeksy dla serwera s³owników
DICT.
Ten pakiet zawiera tak¿e inne narzêdzia do formatowania baz:
dictfmt_{index2suffix,index2word,plugin,virtual} and dictunformat.

%package -n dictzip
Summary:	Compress (or expand) files, allowing random access
Summary(pl):	Kompresja (i dekompresja) plików pozwalaj±ca na swobodny dostêp
Group:		Applications/Archiving

%description -n dictzip
dictzip compresses files using the gzip(1) algorithm (LZ77) in a
manner which is completely compatible with the gzip file format. An
extension to the gzip file format (Extra Field, described in 2.3.1.1
of RFC 1952) allows extra data to be stored in the header of a
compressed file. Dictd, the DICT protocol dictionary server will make
use of this data to perform pseudo-random access on the file.

%description -n dictzip -l pl
dictzip kompresuje pliki korzystaj±c z zawartego w gzip(1) algorytmu
(LZ77) który jest ca³kowicie kompatybilny z formatem plików gzip.
Rozszerzenie do formatu plików gzip (pole dodatkowe, opisane w 2.3.1.1
RFC 1952) pozwalaj±cego na dodatkowe dane zapisane w nag³ówku
skompresowanego pliku. Dictd, serwer protoko³u DICT wykorzystuje te
dane do pseudo-swobodnego dostêpu do pliku.

%prep
%setup -q
#%patch0 -p1
%patch1 -p1

%build
cp -f %{_datadir}/automake/config.* .
%{__aclocal}
%{__autoconf}
cd libmaa
cp -f %{_datadir}/automake/config.* .
%{__aclocal}
%{__autoconf}
cd ..
CFLAGS="%{rpmcflags} -DUID_NOBODY=99 -DGID_NOBODY=99"
%configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig,%{name}},%{_bindir},%{_sbindir}} \
		$RPM_BUILD_ROOT{%{_datadir}/%{name},%{_mandir}/man{1,8}}

install dict dictzip dictfmt{,_{index2suffix,index2word,plugin,virtual}} \
	dictunformat $RPM_BUILD_ROOT%{_bindir}
install dict*.1 $RPM_BUILD_ROOT%{_mandir}/man1

install %{name} $RPM_BUILD_ROOT%{_sbindir}
install %{name}.8 $RPM_BUILD_ROOT%{_mandir}/man8

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
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/%{name}/%{name}-main.conf
%config(noreplace) %verify(not md5 size mtime) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_sbindir}/%{name}
%dir %{_datadir}/%{name}
%{_mandir}/man8/%{name}*

%files -n dict
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/dict.conf
%attr(755,root,root) %{_bindir}/dict
%{_mandir}/man1/dict.1*

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
