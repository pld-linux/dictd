Summary:	Dictionary database server
Name:		dictd
Version:	1.5.0
Release:	1
License:	GPL
Group:		Daemons
Group(pl):	Serwery
URL:		http://www.dict.org/
Source0:	ftp://ftp.dict.org/pub/dict/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description 
Server for the Dictionary Server Protocol (DICT), a TCP transaction
based query/response protocol that allows a client to access
dictionary definitions from a set of natural language dictionary
databases.

%package        -n dict
Summary:	DICT Protocol Client
Group:		Applications/Networking
Group(pl):	Aplikacje/Sieciowe

%description -n dict
Client for the Dictionary Server Protocol (DICT), a TCP transaction
based query/response protocol that provides access to dictionary
definitions from a set of natural language dictionary databases.

%package        -n dictzip
Summary:	Compress (or expand) files, allowing random access
Group:		Utilities/Archiving
Group(pl):	Narzêdzia/Archiwizacja

%description -n dictzip
dictzip compresses files using the gzip(1) algorithm (LZ77) in a
manner which is completely compatible with the gzip file format. An
extension to the gzip file format (Extra Field, described in 2.3.1.1
of RFC 1952) allows extra data to be stored in the header of a
compressed file. Dictd, the DICT protocol dictionary server will make
use of this data to perform pseudo-random access on the file.

%prep
%setup -q -n %{name}-%{version}

%build
# --without-local-zlib option gives no effect. Usage of zlib from dictd tarball 
# is hardcoded in configure. 
# 
# TODO: 
# - patch needed instead of use -DUID_NOBODY=`id -u nobody`
#
%configure --with-cflags="-DUID_NOBODY=`id -u nobody` $RPM_OPT_FLAGS"
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{_bindir},%{_sbindir}} \
	   $RPM_BUILD_ROOT{%{_datadir}/dictd,%{_mandir}/man{1,8}}

for f in dict dictzip; do
	install -s $f $RPM_BUILD_ROOT/%{_bindir}
        gzip -9nf $f.1
	install $f.1.gz $RPM_BUILD_ROOT/%{_mandir}/man1
done 

install -s dictd $RPM_BUILD_ROOT/%{_sbindir}
gzip -9nf dictd.8
install dictd.8.gz $RPM_BUILD_ROOT/%{_mandir}/man8

echo "server localhost" > dict.conf
echo -e "access {\n\tallow localhost\n\tdeny *\n}\n" > dictd.conf 

install dict.conf dictd.conf $RPM_BUILD_ROOT%{_sysconfdir}/
touch %{buildroot}%{_sysconfdir}/%{name}.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}

mv -f doc/security.doc security.txt
gzip -9nf {ANNOUNCE,ChangeLog,README,TODO,%{name}.conf,example*.conf,example.site,security.txt}
gzip -9nf example.dictrc

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
%config(noreplace) %{_sysconfdir}/%{name}.conf
%attr(755,root,root) %{_sbindir}/%{name}
%attr(755,root,root) /etc/rc.d/init.d/%{name}
%{_sysconfdir}/sysconfig/%{name}
%dir %{_datadir}/dictd
%{_mandir}/man8/%{name}*
%doc {ANNOUNCE,ChangeLog,README,TODO,%{name}.conf,example*.conf,example.site,security.txt}.gz

%files -n dict
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/dict.conf
%attr(755,root,root) %{_bindir}/dict
%{_mandir}/man1/dict.1.gz

%files -n dictzip
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dictzip
%{_mandir}/man1/dictzip.1.gz
