Summary:	Dictionary database server
Summary(pl):	Serwer bazy s³owników
Name:		dictd
Version:	1.5.5
Release:	1
License:	GPL
Group:		Daemons
Group(de):	Server
Group(pl):	Serwery
Source0:	ftp://ftp.dict.org/pub/dict/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://www.dict.org/
Requires:	/bin/cat
Requires:	/bin/ls
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description 
Server for the Dictionary Server Protocol (DICT), a TCP transaction
based query/response protocol that allows a client to access
dictionary definitions from a set of natural language dictionary
databases.

%description -l pl
Serwer dla Dictionary Server Protocol(DICT), bazuj±cego na TCP
protoko³u zapytañ i odpowiedzi umo¿liwiaj±cego klientom na dostêp do
definicji s³ownikowych z zestawu baz danych.

%package -n dict
Summary:	DICT Protocol Client
Summary(pl):	Klient protoko³u DICT
Group:		Applications/Networking
Group(de):	Applikationen/Netzwerkwesen
Group(pl):	Aplikacje/Sieciowe

%description -n dict
Client for the Dictionary Server Protocol (DICT), a TCP transaction
based query/response protocol that provides access to dictionary
definitions from a set of natural language dictionary databases.

%description -n dict -l pl
Klient dla Dictionary Server Protocol(DICT), bazuj±cego na TCP
protoko³u zapytañ i odpowiedzi umo¿liwiaj±cego klientom na dostêp do
definicji s³ownikowych z zestawu baz danych.

%package -n dictzip
Summary:	Compress (or expand) files, allowing random access
Group:		Applications/Archiving
Group(de):	Applikationen/Archivierung
Group(pl):	Aplikacje/Archiwizacja

%description -n dictzip
dictzip compresses files using the gzip(1) algorithm (LZ77) in a
manner which is completely compatible with the gzip file format. An
extension to the gzip file format (Extra Field, described in 2.3.1.1
of RFC 1952) allows extra data to be stored in the header of a
compressed file. Dictd, the DICT protocol dictionary server will make
use of this data to perform pseudo-random access on the file.

%description -n dictzip -l pl
dictzip kompresuje pliki ko¿ystaj±c z zawartego w gzip(1) algorytmu
(LZ77) który jest ca³kowicie kompatybilny z formatem plików gzip.
Rozszerzenie do formatu plików gzip(pole dodatkowe, opisane w 2.3.1.1
RFC 1952) pozwalaj±cego na dodatkowe dane zapisane w nag³ówku
skompresowanego pliku. Dictd, serwer protoko³u DICT wykorzystuje te
dane do pseudo-losowego dostêpu do pliku.

%prep
%setup -q

%build
# --without-local-zlib option gives no effect. Usage of zlib from dictd tarball 
# is hardcoded in configure. 
# 
# TODO: 
# - patch needed instead of use -DUID_NOBODY=`id -u nobody`
#
CFLAGS="%{rpmcflags} -DUID_NOBODY=`id -u nobody`"
export CFLAGS
%configure \
	--with-local-zlib=no
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/{rc.d/init.d,sysconfig,%{name}},%{_bindir},%{_sbindir}} \
	   $RPM_BUILD_ROOT{%{_datadir}/%{name},%{_mandir}/man{1,8}}

install dict dictzip $RPM_BUILD_ROOT/%{_bindir}
install {dict,dictzip}.1 $RPM_BUILD_ROOT/%{_mandir}/man1

install %{name} $RPM_BUILD_ROOT/%{_sbindir}
install %{name}.8 $RPM_BUILD_ROOT/%{_mandir}/man8

echo "server localhost" > dict.conf
echo -e "access {\n\tallow localhost\n\tdeny *\n}\n" > %{name}-main.conf 

install dict.conf $RPM_BUILD_ROOT%{_sysconfdir}/
install dictd-main.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/
touch %{buildroot}%{_sysconfdir}/%{name}.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}

mv -f doc/security.doc security.txt
gzip -9nf {ANNOUNCE,ChangeLog,README,TODO,%{name}.conf,example*.conf,example.site,security.txt}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
if [ -f /var/lock/subsystem/%{name} ]; then
        /etc/rc.d/init.d/%{name} restart >&2
else
        echo "Run \"/etc/rc.d/init.d/%{name} start\" to start %{name} daemon."
fi
    
%preun
if [ $1 = 0 ]; then
        /sbin/chkconfig --del %{name}
        /etc/rc.d/init.d/%{name} stop >&2 || true
fi

%files
%defattr(644,root,root,755)
%ghost %{_sysconfdir}/%{name}.conf
%attr(755,root,root) %{_sbindir}/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/sysconfig/%{name}
%dir %{_datadir}/%{name}
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/%{name}-main.conf
%{_mandir}/man8/%{name}*
%doc {ANNOUNCE,ChangeLog,README,TODO,%{name}.conf,example*.conf,example.site,security.txt}.gz

%files -n dict
%defattr(644,root,root,755)
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/dict.conf
%attr(755,root,root) %{_bindir}/dict
%{_mandir}/man1/dict.1*

%files -n dictzip
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dictzip
%{_mandir}/man1/dictzip.1*
