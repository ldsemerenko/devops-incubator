%ifos darwin
%define __portsed sed -i "" -e
%else
%define __portsed sed -i
%endif

%if %{?TOMCAT_REL:1}
%define tomcat_rel        %{TOMCAT_REL}
%else
%define tomcat_rel        7.0.27
%endif

%if %{?NEXUS_REL:1}
%define nexus_rel    %{NEXUS_REL}
%else
%define nexus_rel    2.0.4
%endif

Name: mynexus
Version: %{nexus_rel}
Release: 1
Summary: Sonatype Nexus OSS %{nexus_rel} powered by Apache Tomcat %{tomcat_rel}
Group: Applications/Communications
URL: http://www.mycorp.org/
Vendor: MyCorp
Packager: MyCorp
License: AGPLv1
BuildArch:  noarch

%define app             mynexus
%define appusername     mynexus
%define appuserid       1236
%define appgroupid      1236

%define appdir          /opt/%{app}
%define appdatadir      %{_var}/lib/%{app}
%define applogdir       %{_var}/log/%{app}
%define appexec         %{appdir}/bin/catalina.sh
%define appconfdir      %{appdir}/conf
%define appconflocaldir %{appdir}/conf/Catalina/localhost
%define appwebappdir    %{appdir}/webapps
%define apptempdir      /tmp/%{app}
%define appworkdir      %{_var}/%{app}

%define _systemdir      /lib/systemd/system
%define _initrddir      %{_sysconfdir}/init.d

BuildRoot: %{_tmppath}/build-%{name}-%{version}-%{release}

%if 0%{?suse_version} > 1140
BuildRequires: systemd
%{?systemd_requires}
%else
%define systemd_requires %{nil}
%endif

%if 0%{?suse_version}
Requires:           java = 1.6.0
%endif

%if 0%{?fedora} || 0%{?rhel} || 0%{?centos}
Requires:           java = 1:1.6.0
%endif

Requires(pre):      %{_sbindir}/groupadd
Requires(pre):      %{_sbindir}/useradd

Source0: apache-tomcat-%{tomcat_rel}.tar.gz
Source1: nexus-%{nexus_rel}.war
Source2: initd.skel
Source3: sysconfig.skel
Source4: jmxremote.access.skel
Source5: jmxremote.password.skel
Source6: setenv.sh.skel
Source7: logrotate.skel
Source8: server.xml.skel
Source9: limits.conf.skel
Source10: systemd.skel
Source11: catalina-jmx-remote-%{tomcat_rel}.jar

%description
Sonatype Nexus OSS %{nexus_rel} powered by Apache Tomcat %{tomcat_rel}

%prep
%setup -q -c

%build

%install
# Prep the install location.
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_initrddir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/security/limits.d
mkdir -p $RPM_BUILD_ROOT%{_systemdir}

mkdir -p $RPM_BUILD_ROOT%{appdir}
mkdir -p $RPM_BUILD_ROOT%{appdatadir}
mkdir -p $RPM_BUILD_ROOT%{applogdir}
mkdir -p $RPM_BUILD_ROOT%{apptempdir}
mkdir -p $RPM_BUILD_ROOT%{appworkdir}
mkdir -p $RPM_BUILD_ROOT%{appwebappdir}

# Copy tomcat
mv apache-tomcat-%{tomcat_rel}/* $RPM_BUILD_ROOT%{appdir}

# Create conf/Catalina/localhost
mkdir -p $RPM_BUILD_ROOT%{appconflocaldir}

# remove default webapps
rm -rf $RPM_BUILD_ROOT%{appdir}/webapps/*

# patches to have logs under /var/log/app
%{__portsed} 's|\${catalina.base}/logs|%{applogdir}|g' $RPM_BUILD_ROOT%{appdir}/conf/logging.properties

# nexus webapp is ROOT.war (will respond to /)
cp %{SOURCE1}  $RPM_BUILD_ROOT%{appwebappdir}/ROOT.war

# init.d
cp  %{SOURCE2} $RPM_BUILD_ROOT%{_initrddir}/%{app}
%{__portsed} 's|@@NEXUS_APP@@|%{app}|g' $RPM_BUILD_ROOT%{_initrddir}/%{app}
%{__portsed} 's|@@NEXUS_USER@@|%{appusername}|g' $RPM_BUILD_ROOT%{_initrddir}/%{app}
%{__portsed} 's|@@NEXUS_VERSION@@|version %{version} release %{release}|g' $RPM_BUILD_ROOT%{_initrddir}/%{app}
%{__portsed} 's|@@NEXUS_EXEC@@|%{appexec}|g' $RPM_BUILD_ROOT%{_initrddir}/%{app}

# sysconfig
cp  %{SOURCE3}  $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{app}
%{__portsed} 's|@@NEXUS_APP@@|%{app}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{app}
%{__portsed} 's|@@NEXUS_APPDIR@@|%{appdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{app}
%{__portsed} 's|@@NEXUS_DATADIR@@|%{appdatadir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{app}
%{__portsed} 's|@@NEXUS_LOGDIR@@|%{applogdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{app}
%{__portsed} 's|@@NEXUS_USER@@|%{appusername}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{app}
%{__portsed} 's|@@NEXUS_CONFDIR@@|%{appconfdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{app}

# JMX (including JMX Remote)
cp %{SOURCE11} $RPM_BUILD_ROOT%{appdir}/lib
cp %{SOURCE4}  $RPM_BUILD_ROOT%{appconfdir}/jmxremote.access.skel
cp %{SOURCE5}  $RPM_BUILD_ROOT%{appconfdir}/jmxremote.password.skel

# Our custom setenv.sh to get back env variables
cp  %{SOURCE6} $RPM_BUILD_ROOT%{appdir}/bin/setenv.sh
%{__portsed} 's|@@NEXUS_APP@@|%{app}|g' $RPM_BUILD_ROOT%{appdir}/bin/setenv.sh

# Install logrotate
cp %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{app}
%{__portsed} 's|@@NEXUS_LOGDIR@@|%{applogdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{app}

# Install server.xml.skel
cp %{SOURCE8} $RPM_BUILD_ROOT%{appconfdir}/server.xml.skel

# Setup user limits
cp %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/security/limits.d/%{app}.conf
%{__portsed} 's|@@NEXUS_USER@@|%{appusername}|g' $RPM_BUILD_ROOT%{_sysconfdir}/security/limits.d/%{app}.conf

# Setup Systemd
cp %{SOURCE10} $RPM_BUILD_ROOT%{_systemdir}/%{app}.service
%{__portsed} 's|@@NEXUS_APP@@|%{app}|g' $RPM_BUILD_ROOT%{_systemdir}/%{app}.service
%{__portsed} 's|@@NEXUS_EXEC@@|%{appexec}|g' $RPM_BUILD_ROOT%{_systemdir}/%{app}.service

# remove uneeded file in RPM
rm -f $RPM_BUILD_ROOT%{appdir}/*.sh
rm -f $RPM_BUILD_ROOT%{appdir}/*.bat
rm -f $RPM_BUILD_ROOT%{appdir}/bin/*.bat
rm -rf $RPM_BUILD_ROOT%{appdir}/logs
rm -rf $RPM_BUILD_ROOT%{appdir}/temp
rm -rf $RPM_BUILD_ROOT%{appdir}/work

# ensure shell scripts are executable
chmod 755 $RPM_BUILD_ROOT%{appdir}/bin/*.sh

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%if 0%{?suse_version} > 1140
%service_add_pre %{app}.service
%endif
# First install time, add user and group
if [ "$1" == "1" ]; then
  %{_sbindir}/groupadd -r -g %{appgroupid} %{appusername} 2>/dev/null || :
  %{_sbindir}/useradd -s /sbin/nologin -c "%{app} user" -g %{appusername} -r -d %{appdatadir} -u %{appuserid} %{appusername} 2>/dev/null || :
else
# Update time, stop service if running
  if [ "$1" == "2" ]; then
    if [ -f %{_var}/run/%{app}.pid ]; then
      %{_initrddir}/%{app} stop
      touch %{applogdir}/rpm-update-stop
    fi
    # clean up deployed webapp
    rm -rf %{appwebappdir}/ROOT
  fi
fi

%post
%if 0%{?suse_version} > 1140
%service_add_post %{app}.service
%endif
# First install time, register service, generate random passwords and start application
if [ "$1" == "1" ]; then
  # register app as service
  systemctl enable %{app}.service >/dev/null 2>&1

  # Generated random password for RO and RW accounts
  RANDOMVAL=`echo $RANDOM | md5sum | sed "s| -||g" | tr -d " "`
  sed -i "s|@@NEXUS_RO_PWD@@|$RANDOMVAL|g" %{_sysconfdir}/sysconfig/%{app}
  RANDOMVAL=`echo $RANDOM | md5sum | sed "s| -||g" | tr -d " "`
  sed -i "s|@@NEXUS_RW_PWD@@|$RANDOMVAL|g" %{_sysconfdir}/sysconfig/%{app}

  pushd %{appdir} >/dev/null
  ln -s %{applogdir}  logs
  ln -s %{apptempdir} temp
  ln -s %{appworkdir} work
  popd >/dev/null

  # start application at first install (uncomment next line this behaviour not expected)
  # %{_initrddir}/%{name} start
else
  # Update time, restart application if it was running
  if [ "$1" == "2" ]; then
    if [ -f %{applogdir}/rpm-update-stop ]; then
      # restart application after update (comment next line this behaviour not expected)
      %{_initrddir}/%{name} start
      rm -f %{applogdir}/rpm-update-stop
    fi
  fi
fi

%preun
%if 0%{?suse_version} > 1140
%service_del_preun %{app}.service
%endif
if [ "$1" == "0" ]; then
  # Uninstall time, stop service and cleanup

  # stop service
  %{_initrddir}/%{app} stop

  # unregister app from services
  systemctl disable %{app}.service >/dev/null 2>&1

  # finalize housekeeping
  rm -rf %{appdir}
  rm -rf %{applogdir}
  rm -rf %{apptempdir}
  rm -rf %{appworkdir}
fi

%postun
%if 0%{?suse_version} > 1140
%service_del_postun %{app}.service
%endif

%files
%defattr(-,root,root)
%attr(0755,%{appusername},%{appusername}) %dir %{applogdir}
%attr(0755, root,root) %{_initrddir}/%{app}
%attr(0644,root,root) %{_systemdir}/%{app}.service
%config(noreplace) %{_sysconfdir}/sysconfig/%{app}
%config %{_sysconfdir}/logrotate.d/%{app}
%config %{_sysconfdir}/security/limits.d/%{app}.conf
%{appdir}/bin
%{appdir}/conf
%{appdir}/lib
%attr(-,%{appusername}, %{appusername}) %{appdir}/webapps
%attr(0755,%{appusername},%{appusername}) %dir %{appconflocaldir}
%attr(0755,%{appusername},%{appusername}) %dir %{appdatadir}
%attr(0755,%{appusername},%{appusername}) %dir %{apptempdir}
%attr(0755,%{appusername},%{appusername}) %dir %{appworkdir}
%doc %{appdir}/NOTICE
%doc %{appdir}/RUNNING.txt
%doc %{appdir}/LICENSE
%doc %{appdir}/RELEASE-NOTES

%changelog
* Thu May 24 2012 henri.gomez@gmail.com 2.0.4-1
- Nexus 2.0.4 released, RPM updated

* Wed Apr 25 2012 henri.gomez@gmail.com 2.0.3-1
- Set default release to 1 instead of 0

* Wed Mar 7 2012 henri.gomez@gmail.com 2.0.2-0
- Distribution dependant Requires for Java
- Nexus 2.0.2 released

* Fri Jan 6 2012 henri.gomez@gmail.com 2.0.1-0
- Create conf/Catalina/localhost with user rights

* Sat Dec 3 2011 henri.gomez@gmail.com 1.99-0
- Initial RPM