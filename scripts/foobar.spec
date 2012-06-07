Summary: The world famous foo 
Name: foo 
Version: 1.03 
Release: 1
License: GPL 
Group: Applications/System 
Source0: foo-%{version}.tar.bz2 
Source1: foo.sysvinit 
Patch0: foo-fix1.patch 
Patch1: foo-fix2.patch 
BuildRoot: /var/tmp/%{name}-root

%description 
This foo daemon serves bar clients.

%prep 
%setup -q

%build 
%configure 
make

%install 
rm -rf %{buildroot} 
%makeinstall

%clean 
rm -rf %{buildroot}

%files  
%defattr(-,root,root) 
/etc/init.d/foo 
%{_sbindir}/foo 
/usr/share/man/man8/foo.8

%files devel 
%defattr(-,root,root) 
/usr/include/foo.h 
/usr/lib/foo.a

%changelog 
* Mon Apr 30 2003 Dax Kelson 
- ver 1.03

