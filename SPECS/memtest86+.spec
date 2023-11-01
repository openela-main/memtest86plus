%bcond_with update_grub

# Prevent stripping
%global __spec_install_post /usr/lib/rpm/brp-compress
# Turn off debuginfo package
%global debug_package %{nil}

%global readme_suffix %{?rhel:redhat}%{!?rhel:fedora}

Name:     memtest86+
Version:  5.01
Release:  20%{?dist}
License:  GPLv2
Summary:  Stand-alone memory tester for x86 and x86-64 computers
Group:    System Environment/Base
Source0:  http://www.memtest.org/download/%{version}/%{name}-%{version}.tar.gz
Source1:  memtest-setup
Source2:  new-memtest-pkg
Source3:  20_memtest86+
Source4:  memtest-setup.8
Source5:  memtest86+.conf
Source6:  README
# reported upstream
Patch0:   memtest86+-5.01-no-scp.patch
# patches to get memtest86+ working with gcc-4.7.2 or later + PCI scan fix
# these patches were taken from Mageia
# upstream report containing link to the patches:
# http://forum.canardpc.com/threads/83443-Memtest86-V5.01-crashes-with-gcc-4.7.2-or-later
Patch1:   memtest86+-5.01-no-optimization.patch
Patch2:   memtest86+-5.01-compile-fix.patch
Patch3:   memtest86+-5.01-crash-fix.patch
Patch4:   memtest86+-5.01-fgnu89-inline.patch
Patch5:   memtest86+-5.01-serial-console-fix.patch
URL:      http://www.memtest.org
# require glibc-devel.i386 via this file:
BuildRequires: %{_includedir}/gnu/stubs-32.h
Requires: grubby sed coreutils util-linux
ExclusiveArch: %{ix86} x86_64

%description
Memtest86+ is a thorough stand-alone memory test for x86 and x86-64
architecture computers. BIOS based memory tests are only a quick
check and often miss many of the failures that are detected by
Memtest86+.

The ELF version should be used for booting from grub,
and avoids the following errors:
"Error 7: Loading below 1MB is not supported"
"Error 13: Invalid or unsupported executable format"
"Error 28: Selected item cannot fit into memory"

The script '%{_sbindir}/memtest-setup' can be run (as root)
to add the %{name} entry to your GRUB boot menu.

%prep
%setup -q
cp -p %{SOURCE6} README.%{readme_suffix}
%patch0 -p1 -b .no-scp
%patch1 -p1 -b .no-optimization
%patch2 -p1 -b .compile-fix
%patch3 -p1 -b .crash-fix
%patch4 -p1 -b .fgnu89-inline
%patch5 -p1 -b .serial-console-fix

#sed -i -e's,0x10000,0x100000,' memtest.lds
%ifarch x86_64
sed -i -e's,$(LD) -s -T memtest.lds,$(LD) -s -T memtest.lds -z max-page-size=0x1000,' Makefile
%endif

%build
# Regular build flags not wanted for this binary
# Note: i486 minimum runtime arch
# It makes no sense to use smp flags here.
make

%install
mkdir -p %{buildroot}/{boot,%{_sbindir}}

# the ELF (memtest) version.
install -m644 memtest %{buildroot}/boot/elf-%{name}-%{version}

# the floppy (memtest.bin) version.
install -m644 memtest.bin %{buildroot}/boot/%{name}-%{version}

install -m755 %{SOURCE2} %{buildroot}%{_sbindir}/new-memtest-pkg
install -m755 %{SOURCE1} %{buildroot}%{_sbindir}/memtest-setup
sed -i 's/\r//' $RPM_BUILD_DIR/%{name}-%{version}/README

mkdir -p %{buildroot}%{_sysconfdir}/grub.d
touch %{buildroot}%{_sysconfdir}/grub.d/20_memtest86+

install -Dd %{buildroot}%{_datadir}/%{name}
install -m644 %{SOURCE3} %{buildroot}%{_datadir}/%{name}

# install manual page
install -Dpm 0644 %{SOURCE4} %{buildroot}%{_mandir}/man8/memtest-setup.8

# install configuration file
install -Dpm 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/memtest86+.conf

%post
%if %{with update_grub}
/usr/sbin/memtest-setup
%endif

%preun
if [ -f /boot/grub/grub.conf ]
then
  sed -i -e's,kernel --type=netbsd /elf-%{name}-%{version},kernel /elf-%{name}-%{version},' /boot/grub/grub.conf
  %{_sbindir}/new-memtest-pkg --remove %{version}
fi

%files
%doc README README.%{readme_suffix}
%config(noreplace) %{_sysconfdir}/memtest86+.conf
/boot/%{name}-%{version}
/boot/elf-%{name}-%{version}
%{_sbindir}/new-memtest-pkg
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/20_memtest86+
%ghost %attr(0755,-,-) %{_sysconfdir}/grub.d/20_memtest86+
%{_sbindir}/memtest-setup
%{_mandir}/man8/*.8.gz

%changelog
* Thu Oct 22 2020 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-20
- Fixed serial console
  Resolves: rhbz#1696877

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 5.01-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.01-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.01-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.01-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Apr  5 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-15
- Various improvements to memtest-setup, e.g. now exits with error if
  run by non root user

* Tue Feb 23 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-14
- Removed some spec artifacts (like buildroot cleaning)
- Fixed malformed "Loading" banner
- Not relocating memtest86+ above 1 MB
  Related: rhbz#1303804
- Introduced new configuration file (/etc/memtest86+.conf)
- Introduced new memtest-setup switches for selecting ELF/non-ELF versions
  Resolves: rhbz#1303804

* Fri Feb 12 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-13
- Updated distribution specific README

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 5.01-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 28 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-11
- Fixed memtest86+ binary (non-ELF) to run from floppy

* Fri Jan  8 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-10
- Fixed memtest86+ to run even if relocated above 1 MB
  (by real-mode-reloc patch)
- Relocated memtest86+ above 1 MB (as we always did in Fedora)
- Fixed compilation of inline assembly with new gcc
  (by fgnu89-inline patch)

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.01-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Oct 21 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-8
- More crash fixes (by crash-fix patch from David McInnis)

* Fri Sep  5 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-7
- Fixed typo in memtest-setup help, added its options to man / help

* Wed Sep  3 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-6
- Fixed memtest-setup script

* Tue Aug 26 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-5
- Added documentation regarding memtest-setup

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.01-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.01-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Apr  3 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-2
- Switched back to latest distro gcc

* Mon Feb 17 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 5.01-1
- New version
  Resolves: rhbz#1013110
- Switched to the gcc-34 due to upstream non-compatiblity with
  the latest gccs (#1013110)
- Removed trailing whitespaces from the description

* Mon Sep 16 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 4.20-11
- Fixed grubby requirement
- Fixed bogus dates in changelog (best effort)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.20-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.20-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Jan  8 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 4.20-8
- Fixed packaging regarding usrmove

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.20-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Mar 27 2012 Jaroslav Škarvada <jskarvad@redhat.com> - 4.20-6
- Fixed path in 20_memtest86+ not to generate error on grub2-mkconfig
  Resolves: rhbz#805542
- Temporal fix for 7th test failure
  Resolves: rhbz#805813

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.20-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Dec  7 2011 Jaroslav Škarvada <jskarvad@redhat.com> - 4.20-4
- Used ELF format with grub2

* Wed Dec  7 2011 Jaroslav Škarvada <jskarvad@redhat.com> - 4.20-3
- Renamed 20_memtest to 20_memtest86+
- Fixed ghost handling, 20_memtest86+ is properly removed now

* Mon Dec  5 2011 Jaroslav Škarvada <jskarvad@redhat.com> - 4.20-2
- Added support for grub2, thanks to Michal Ambroz <rebus@seznam.cz>

* Mon Mar 07 2011 Jaroslav Škarvada <jskarvad@redhat.com> - 4.20-1
- Update to new version (#682425)
- Removed fix-asciimap patch (not needed now)
- Removed make-gcc4-builds-work patch (not used)

* Mon Feb 21 2011 Jaroslav Škarvada <jskarvad@redhat.com> - 4.10-5
- Deprecated nash replaceed by findfs (#671503)

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.10-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 11 2011 Jaroslav Škarvada <jskarvad@redhat.com> - 4.10-3
- Reduce max-page-size on x86_64 to fit into loader limits (#620846)

* Tue May 25 2010 Anton Arapov <anton@redhat.com> - 4.10-2
- Fix memory region to load. (#578966)

* Wed May 05 2010 Anton Arapov <anton@redhat.com> - 4.10-1
- Update to new upstream release, v4.10

* Tue Mar 30 2010 Anton Arapov <anton@redhat.com> - 4.00-4
- Fix ascii map of spd.c (#577469)

* Fri Dec 25 2009 Robert Scheck <robert@fedoraproject.org> - 4.00-3
- Removed obsolete build requirement to compat-gcc-34 (#442285)

* Tue Oct 13 2009 Jarod Wilson <jarod@redhat.com> - 4.00-2
- Fix memtest-setup on systems without a separate /boot
  filesystem (#528651)

* Tue Sep 29 2009 Jarod Wilson <jarod@redhat.com> - 4.00-1
- Update to new upstream release, v4.00
- Drop gcc4.2+ patch, merged upstream

* Mon Aug 17 2009 Jarod Wilson <jarod@redhat.com> - 2.11-11
- Fix runtime operation when built with gcc4.2+ (#442285)

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.11-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Apr 24 2009 Warren Togami <wtogami@redhat.com> - 2.11-9
- Fix uninstall to remove stanza from grub.conf

* Fri Apr 24 2009 Warren Togami <wtogami@redhat.com> - 2.11-8
- Bug #494157 rename elf binary so it doesn't accidentally copy the elf binary
  during livecd-creator
- Put scripts into CVS

* Sun Apr 05 2009 Paulo Roma <roma@lcg.ufrj.br> - 2.11-7
- adapted the spec file for building the elf and 
  the bin versions #494157

* Thu Apr 02 2009 Paulo Roma <roma@lcg.ufrj.br> - 2.11-6
- grub.conf will not be updated by default. The user
  will have to add and/or remove memtest86+ entries.
- No messages printed.

* Tue Mar 31 2009 Paulo Roma <roma@lcg.ufrj.br> - 2.11-5
- Changed postun for preun.
- Calling memtest-setup in case of updating grub.conf

* Wed Mar 11 2009 Paulo Roma <roma@lcg.ufrj.br> - 2.11-4
- Updated to 2.11
- Patched for booting from grub.
- Using memtest (ELF) instead of memtest.bin
- Changed memtest-setup for writing the correct grub entry.
- Removed obsolete patch memtest86+-2.10-fixflags.patch
- Created option update grub.conf

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.11-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Nov 12 2008 Warren Togami <wtogami@redhat.com> - 2.10-1
- 2.10

* Thu Apr 03 2008 Warren Togami <wtogami@redhat.com> - 2.01-3
- Build with gcc34 for F9 (#437701)

* Tue Mar 04 2008 Peter Jones <pjones@redhat.com> - 2.01-2
- Don't install memtest86+ in bootloader configs on EFI platforms.

* Thu Feb 21 2008 Warren Togami <wtogami@redhat.com> - 2.01-1
- 2.01 major bugfix release

* Mon Feb 11 2008 Michal Schmidt <mschmidt@redhat.com> - 2.00-2
- forgot to cvs add the compilation patch.

* Mon Feb 11 2008 Michal Schmidt <mschmidt@redhat.com> - 2.00-1
- New upstream release: 2.00.
- Dropped boot time console configuration patches (already upstream).
- Fixed compilation on x86_64.

* Wed Oct 24 2007 Peter Jones <pjones@redhat.com> - 1.70-4
- Fix for mactel.

* Thu Oct 18 2007 Warren Togami <wtogami@redhat.com> - 1.70-3
- one more patch from mschmidt to allow configuration of parity and bits

* Wed Oct 17 2007 Warren Togami <wtogami@redhat.com> - 1.70-2
- mschmidt's boot time configuration of serial console (#319631)

* Thu Feb 08 2007 Florian La Roche <laroche@redhat.com> - 1.70-1
- update to 1.70

* Sat Feb 03 2007 Warren Togami <wtogami@redhat.com> - 1.65-6
- some spec cleanups (#226135)
- remove old Obsoletes

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.65-4.1
- rebuild

* Tue Jun 27 2006 Florian La Roche <laroche@redhat.com> - 1.65-4
- make sure coreutils is installed for the preun script

* Thu Jun 08 2006 Jesse Keating <jkeating@redhat.com> - 1.65-3
- rebuilt for new buildsystem

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.65-2.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Sat Oct 15 2005 Florian La Roche <laroche@redhat.com>
- make sure 32bit glibc-devel is installed (#170614)

* Sat Oct 01 2005 Warren Togami <wtogami@redhat.com> - 1.65-1
- 1.65

* Wed Jun 29 2005 Warren Togami <wtogami@redhat.com> - 1.60-1
- 1.60

* Mon Mar 28 2005 Warren Togami <wtogami@redhat.com> - 1.55.1-1
- 1.55.1 fixes K8

* Sun Mar 27 2005 Warren Togami <wtogami@redhat.com> - 1.55-1
- 1.55

* Wed Mar 16 2005 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sat Feb 19 2005 Warren Togami <wtogami@redhat.com> - 1.51-1
- 1.51

* Fri Jan 21 2005 Warren Togami <wtogami@redhat.com> - 1.50-1
- 1.50

* Sun Nov 28 2004 Warren Togami <wtogami@redhat.com> - 1.40-1
- 1.40
- remove arch patch, now upstream

* Tue Oct 26 2004 Warren Togami <wtogami@redhat.com> - 1.27-1
- 1.27

* Mon Oct 25 2004 Jeremy Katz <katzj@redhat.com> - 1.26-3
- allow building on all x86 arches
- pass appropriate compiler options to build on x86_64 as well (#136939)

* Thu Sep 02 2004 Warren Togami <wtogami@redhat.com> 1.26-1
- update to 1.26

* Sat Aug 28 2004 Warren Togami <wtogami@redhat.com> 1.25-1
- update to 1.25

* Mon Jun 28 2004 Warren Togami <wtogami@redhat.com>
- update to 1.20

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sun May 16 2004 Warren Togami <wtogami@redhat.com> 1.15-1
- update to 1.15

* Sun Feb 29 2004 Warren Togami <wtogami@redhat.com> 1.11-2
- switch to memtest86+ 1.11
- add boot loader setup script

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Oct 21 2003 Mike A. Harris <mharris@redhat.com> 3.0-3
- Pedantic spec file cleanups - s/Copyright/License/ and use _libdir instead of
  /usr/lib everywhere (even though it's currently x86 only)

* Tue Oct 21 2003 Jeremy Katz <katzj@redhat.com> 3.0-2
- fix perms (#107610)
- doesn't really require dev86 to build

* Mon Jul 21 2003 Michael Fulbright <msf@redhat.com>
- initial integration into distribution. Removed the scripts to install a
  entry in the boot loader for memtest for the moment, and relocated to under
  /usr/lib.

* Thu Apr 17 2003 Joe Szep <jszep@bu.edu>
- rebuilt for Doolittle final 

* Mon Feb  3 2003 Matthew Miller <mattdm@bu.edu>
- rebuild for doolittle
- patches to make build -- new gcc growing pains, I guess

* Tue Jul 30 2002 Matthew Miller <mattdm@bu.edu>
- added grubby stuff

* Tue Jul 30 2002 Dave Heistand <davidbh@bu.edu>
- updated source to v 3

* Thu Mar 7 2002 Dave Heistand <davidbh@bu.edu>
- updated source to 2.9, also changed setup -n
- to use %%{version}.

* Thu Nov  1 2001 Matthew Miller <mattdm@bu.edu>
- v 2.8a
- removed lilo-configuring scripts. need to figure out the best way to
  work with grub and RH 7.2 / BU Linux 2.5
- group -> System Environment/Base

* Mon Aug 20 2001 Matthew Miller <mattdm@bu.edu>
- v 2.7

* Wed Feb 14 2001 Matthew Miller <mattdm@bu.edu>
- v 2.5

* Fri Oct 06 2000 Matthew Miller <mattdm@bu.edu>
- v 2.4

* Thu Mar 23 2000 Matthew Miller <mattdm@bu.edu>
- changed so that lilo.conf isn't written if it already exists. This is
  important if you're including memtest86 in a distribution
- GPG key available from http://www.bu.edu/dsgsupport/linux/BULinux-GPG-KEY  
- changed name of lilo.conf backup file to something less likely to conflict
  with other backups

* Wed Mar 01 2000 Matthew Miller <mattdm@bu.edu>
- Updated to version 2.2
- Cosmetic changes to spec file
- updated Source: to reflect actual author's url

* Fri Dec 25 1998 Peter Soos <sp@osb.hu>

- Corrected the file attributes

* Mon Aug 17 1998 Peter Soos <sp@osb.hu>

- Moved to 1.4a

* Mon Jun 22 1998 Peter Soos <sp@osb.hu>

- Moved to 1.4

* Wed Dec 31 1997 Peter Soos <sp@osb.hu>

- Initial version
