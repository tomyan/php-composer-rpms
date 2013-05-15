# See WARNING notes in %%description

# Disable automatic dependency processing
# (prevents endless loop if php-composer is already installed on buildsys)
AutoReqProv: no

# For now, disable tests by default
# Tests are only run with rpmbuild --with tests
%global with_tests           %{?_with_tests:1}%{!?_with_tests:0}

# 1 = Tagged version
# 0 or undefined = Snapshot version
%global github_tagged        1

%global github_owner         composer
%global github_name          composer
%global github_version       1.0.0
%global github_version_alpha alpha7
%global github_commit        3e6afd8975b6ff6eb3045ba00e532d6c0e302fe6
%global github_date          20130504

%if 1 != 0%{?github_tagged}
%global github_release %{github_date}git%(c=%{github_commit}; echo ${c:0:7})
%endif

# This is the version that "composer.phar --version" will print. Need to
# manually define this here because compilation is from a tarball and not
# a git repo like the source compiler requires to calulate this value.
%if 0%{?github_tagged}
%global phar_version %{github_version}%{?github_version_alpha:-%{github_version_alpha}}
%else
%global phar_version %{github_commit}
%endif

%global php_min_ver        5.3.2

%global jsonlint_min_ver   1.0.0
%global jsonlint_max_ver   2.0.0

%global jsonschema_min_ver 1.1.0
# DEBUG
#%global jsonschema_max_ver 1.2.0
%global jsonschema_max_ver 2.0

%global symfony_min_ver    2.1.0
%global symfony_max_ver    3.0.0

%global composer           %{_datadir}/composer
%global composer_vendor    composer
%global composer_project   composer

Name:          php-composer
Version:       %{github_version}
Release:       0.4%{?github_version_alpha:.%{github_version_alpha}}%{?github_release:.%{github_release}}%{?dist}
Summary:       Dependency Manager for PHP

Group:         Development/Libraries
License:       MIT
URL:           http://getcomposer.org
Source0:       https://github.com/%{github_owner}/%{github_name}/archive/%{github_commit}/%{name}-%{github_version}-%{github_commit}.tar.gz
# Required only for bootstrapping/build
Source1:       http://getcomposer.org/download/1.0.0-alpha7/composer.phar
# RPM "magic"
Source2:       macros.composer
Source3:       composer.attr
Source4:       composer.prov
Source5:       composer.req
Source6:       composer-fixreq
Source7:       composer-install

# Allow for setting of PHAR version (RPM-only patch)
Patch0:        php-composer-phar-version.patch
# No COMPOSER_DEV_WARNING_TIME (RPM-only patch)
Patch1:        php-composer-no-dev-warning-time.patch

BuildArch:     noarch

# need this for test suite
BuildRequires:  php-phpunit-PHPUnit
BuildRequires:  php-jsonlint >= %{jsonlint_min_ver}
BuildRequires:  php-jsonlint <  %{jsonlint_max_ver}
BuildRequires:  php-JsonSchema >= %{jsonschema_min_ver}
BuildRequires:  php-JsonSchema <  %{jsonschema_max_ver}
BuildRequires:  php-pear(pear.symfony.com/Console) >= %{symfony_min_ver}
BuildRequires:  php-pear(pear.symfony.com/Console) <  %{symfony_max_ver}
BuildRequires:  php-pear(pear.symfony.com/Finder) >= %{symfony_min_ver}
BuildRequires:  php-pear(pear.symfony.com/Finder) <  %{symfony_max_ver}
BuildRequires:  php-pear(pear.symfony.com/Process) >= %{symfony_min_ver}
BuildRequires:  php-pear(pear.symfony.com/Process) <  %{symfony_max_ver}

Requires:      php-common >= %{php_min_ver}
Requires:      php-jsonlint >= %{jsonlint_min_ver}
Requires:      php-jsonlint <  %{jsonlint_max_ver}
Requires:      php-JsonSchema >= %{jsonschema_min_ver}
Requires:      php-JsonSchema <  %{jsonschema_max_ver}
Requires:      php-pear(pear.symfony.com/Console) >= %{symfony_min_ver}
Requires:      php-pear(pear.symfony.com/Console) <  %{symfony_max_ver}
Requires:      php-pear(pear.symfony.com/Finder) >= %{symfony_min_ver}
Requires:      php-pear(pear.symfony.com/Finder) <  %{symfony_max_ver}
Requires:      php-pear(pear.symfony.com/Process) >= %{symfony_min_ver}
Requires:      php-pear(pear.symfony.com/Process) <  %{symfony_max_ver}
# phpci
Requires:      php-curl
Requires:      php-date
Requires:      php-hash
Requires:      php-iconv
Requires:      php-json
Requires:      php-libxml
Requires:      php-mbstring
Requires:      php-openssl
Requires:      php-pcre
Requires:      php-reflection
Requires:      php-simplexml
Requires:      php-spl
Requires:      php-tokenizer
Requires:      php-xsl
Requires:      php-zip
%if 0%{?fedora}
Requires:      php-filter
Requires:      php-phar
%endif

# Common package naming (php-composervendor-composerproject)
Provides:      php-composer-composer = %{version}-%{release}
# Virtual provide
Provides:      php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
Composer is a tool for dependency management in PHP. It allows you to declare
the dependent libraries your project needs and it will install them in your
project for you.

WARNING: This is just a development RPM.  Please submit issues at
         https://github.com/siwinski/php-composer-rpms/issues and prefix
         your issue title with "[%name] ".


%prep
%setup -q -c

cp %{SOURCE2} .
cp %{SOURCE3} .
cp %{SOURCE4} .
cp %{SOURCE5} .
cp %{SOURCE6} .
cp %{SOURCE7} .

cd %{github_name}-%{github_commit}

# Set PHAR version
%patch0
sed 's#__PHAR_VERSION__#%{phar_version}#' -i src/Composer/Compiler.php

# No COMPOSER_DEV_WARNING_TIME
%patch1

# Use system libraries
sed -e "s#__DIR__.'/../../vendor/symfony/'#'%pear_phpdir/Symfony/Component/'#" \
    -e "s#__DIR__.'/../../vendor/seld/jsonlint/src/'#'%{_datadir}/php/Seld/JsonLint/'#" \
    -e "s#__DIR__.'/../../vendor/justinrainbow/json-schema/src/'#'%{_datadir}/php/JsonSchema/'#" \
    -i src/Composer/Compiler.php

# No self update
rm -f src/Composer/Command/SelfUpdateCommand.php
sed '/SelfUpdateCommand/d' -i src/Composer/Console/Application.php

# rpmlint warnings
find ./ -name "*.php" -executable | xargs chmod -x

# important option - allows loading of classes also from global php include path
php %{SOURCE1} config use-include-path true

php %{SOURCE1} dumpautoload


%build
%{github_name}-%{github_commit}/bin/compile


%install
mkdir -p -m 0755 %{buildroot}%{composer}/%{composer_vendor}/%{composer_project} %{buildroot}%{_bindir}
cp -rp %{github_name}-%{github_commit}/{bin,res,src,tests,vendor} %{buildroot}%{composer}/%{composer_vendor}/%{composer_project}/
cp -a %{github_name}-%{github_commit}/{composer.*,phpunit.xml.dist} %{buildroot}%{composer}/%{composer_vendor}/%{composer_project}/

ln -s %{composer}/%{composer_vendor}/%{composer_project}/bin/composer %{buildroot}%{_bindir}/composer

# symlink generic autoloader to include path
ln -s %{composer}/%{composer_vendor}/%{composer_project}/vendor %{buildroot}%{composer}/vendor

# RPM "magic"
mkdir -p -m 0755 %{buildroot}%{_sysconfdir}/rpm
install -p -m 0644 macros.composer %{buildroot}%{_sysconfdir}/rpm/
mkdir -p -m 0755 %{buildroot}%{_rpmconfigdir}/fileattrs
install -p -m 0644 composer.attr %{buildroot}%{_rpmconfigdir}/fileattrs/
install -p -m 0755 composer.prov %{buildroot}%{_rpmconfigdir}/
install -p -m 0755 composer.req %{buildroot}%{_rpmconfigdir}/
install -p -m 0755 composer-fixreq %{buildroot}%{_rpmconfigdir}/
install -p -m 0755 composer-install %{buildroot}%{_rpmconfigdir}/


%check
%if %{with_tests}
    cd %{github_name}-%{github_commit}
    phpunit -c tests/complete.phpunit.xml -d date.timezone=UTC
%else
: Tests skipped, missing '--with tests' option
%endif


%files
%doc %{github_name}-%{github_commit}/LICENSE
%doc %{github_name}-%{github_commit}/*.md
%doc %{github_name}-%{github_commit}/PORTING_INFO
%doc %{github_name}-%{github_commit}/doc
%{composer}/vendor
%dir %{composer}
%dir %{composer}/%{composer_vendor}
     %{composer}/%{composer_vendor}/%{composer_project}
%{_bindir}/composer
# RPM "magic"
%{_sysconfdir}/rpm/macros.composer
%{_rpmconfigdir}/fileattrs/composer.attr
%{_rpmconfigdir}/composer.prov
%{_rpmconfigdir}/composer.req
%{_rpmconfigdir}/composer-fixreq
%{_rpmconfigdir}/composer-install


%changelog
* Wed May 15 2013 Shawn Iwinski <shawn.iwinski@gmail.com> 1.0.0-0.4.alpha7
- Updated to version 1.0.0-alpha7
- Use ustream PHAR as source instead of downloading
- Path substitution instead of patch
- Updated some macro logic
- Allow for setting of PHAR version
- No COMPOSER_DEV_WARNING_TIME
- No self update

* Fri Apr 05 2013 Shawn Iwinski <shawn.iwinski@gmail.com> 1.0.0-0.3.alpha6.20130328git78c250d
- Added composer-install
- Disabled tests by default

* Sat Mar 30 2013 Shawn Iwinski <shawn.iwinski@gmail.com> 1.0.0-0.2.20130328git
- Added composer-fixreq

* Thu Mar 28 2013 Gregor Tätzner <brummbq@fedoraproject.org> - 1.0.0-0.1.20130328git
- git snapshot 78c250da19b823617a14513450576977da36eb3f
- enable tests

* Mon Feb 18 2013 Shawn Iwinski <shawn.iwinski@gmail.com> 1.0.0-0.1.alpha6
- Initial package
