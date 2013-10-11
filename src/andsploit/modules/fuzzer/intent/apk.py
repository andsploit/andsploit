from xml.etree import ElementTree

from andsploit import android
from andsploit.modules import common, Module
from mwr.common.report import IntentFuzzerReport, PermLeak
import time
import logging
import os
import subprocess


class APK(Module, common.Assets, common.ClassLoader, common.Filters, common.PackageManager):

    name = "Intent fuzzing third-party apps."
    description = "Do some preparations for smart fuzzing."
    examples = """Fuzzing a specific package:

    mercury> run app.intents.fuzz -a com.android.settings
    Package: com.android.settings
      Services or Receivers:
      .......
      ......."""
    author = ["Michael (@NISL)", "ZhouLujue (zhoulujue@gmail.com)"]
    date = "2013-5-16"
    license = "MWR Code License"
    path = ["fuzzer", "intent"]
    report_path = "./report"
    EXTRAS_MAP = {"boolean": "t",
                  "byte": "108",
                  "char": "98",
                  "float": "3.14",
                  "double": "3.1415",
                  "short": "12",
                  "integer": "34",
                  "long": "56",
                  "string": "blue-lotus"}

    def add_arguments(self, parser):
        parser.add_argument("-a", "--package", default=None, help="specify the package to inspect")
        parser.add_argument("-f", "--filter", default=None, help="specify filter conditions")
        parser.add_argument("-s", "--samples", default=None, help="fuzz all apps in samples directory")

    def execute(self, arguments):
        shell = self.new("com.mwr.droidhg.shell.Shell")
        # wait for the kernel to get super user permission
        shell.write("su\n")
        time.sleep(1)
                    
        # reading logcat logs about permission check and intent extra check
        shell.write("logcat ContextImplcheckPermission:E IntentExtra:E *:S")
        # wait for the logcat to print out all the result.
        time.sleep(1)
        # before fuzzing, we need to clear all the contexImplPermissioncheck output.
        shell.read()

        if not arguments.package:
            app_list = self.__get_app_list("./samples")
            for package_name in app_list:
                if self.__report__exists("./report", package_name):
                    print "package %s has been analyzed." % package_name
                    continue

                try:
                    output = subprocess.check_output(["grep", package_name, "log/apk_install_error.log"])
                    if output.find(package_name) >= 0:
                        print "package %s cannot be installed." % package_name
                        continue
                except subprocess.CalledProcessError:
                    pass

                if not self.__install_app("./samples", package_name):
                    logging.basicConfig(filename='log/apk_install_error.log')
                    logging.error(package_name)
                    continue
                print "fuzzing package %s......" % package_name
                packageManager = self.packageManager()
                package = packageManager.getPackageInfo(package_name,
                                                        common.PackageManager.GET_RECEIVERS |
                                                        common.PackageManager.GET_SERVICES |
                                                        common.PackageManager.GET_PERMISSIONS |
                                                        common.PackageManager.GET_GIDS)
                self.__fuzz_package(shell, arguments, package)
                self.__uninstall_app("./samples", package_name)
        else:
            package = self.packageManager().getPackageInfo(arguments.package,
                                                           common.PackageManager.GET_RECEIVERS |
                                                           common.PackageManager.GET_SERVICES |
                                                           common.PackageManager.GET_PERMISSIONS |
                                                           common.PackageManager.GET_GIDS)
            self.__fuzz_package(shell, arguments, package)

    def __fuzz_package(self, shell, arguments, package):
        report = IntentFuzzerReport(str(package.packageName))
        services = self.match_filter(package.services, 'name', arguments.filter)
        receivers = self.match_filter(package.receivers, 'name', arguments.filter)

        exported_services = self.match_filter(services, 'exported', True)
        exported_receivers = self.match_filter(receivers, 'exported', True)

        self.stdout.write("Package: %s\n" % package.packageName)
        self.stdout.write("UID: %s\n" % package.applicationInfo.uid)

        if len(exported_services) > 0:
            self.stdout.write("  Exported services:\n")
            for service in exported_services:
                self.__fuzz_component("service", shell, package, service, report)
            self.stdout.write("\n")
        else:
            self.stdout.write("  No matching services.\n\n")

        if len(exported_receivers) > 0:
            self.stdout.write("  Exported Receivers:\n")
            for receiver in exported_receivers:
                self.__fuzz_component("receiver", shell, package, receiver, report)
            self.stdout.write("\n")
        else:
            self.stdout.write("  No matching receivers.\n\n")
        # print repr(report)
        report.save(self.report_path)

    def __fuzz_component(self, ctype, shell, package, component, report):
            self.stdout.write("  %s: %s\n" % (ctype, component.name))
            self.stdout.write("  permission: %s\n" % component.permission)
            self.stdout.write("  Start fuzzing %s ...\n" % component.name)

            uid = package.applicationInfo.uid
            filters = self.__find_filters(ctype, component)
            if len(filters) <= 0:
                filters = [None]
            count = 0
            for filter_ in filters:
                repr_ = self.__get_data_repr(filter_)
                if repr_ != "":
                    logging.basicConfig(filename='log/filter_data.log')
                    logging.warn(component.packageName + "\n" + repr_)
                count += 1
                self.stdout.write("    IntentFilter %s\n" % count)
                actions = self.__find_actions(filter_)
                if len(actions) <= 0:
                    actions = [None]
                for action in actions:
                    stop = False
                    extra_keys = set([])
                    while not stop:
                        self.stdout.write("      Action: " + str(action) + "\n")
                        extras = []
                        for type_, key in extra_keys:
                            if type_ in self.__class__.EXTRAS_MAP.keys():
                                extras.append([type_, key, self.__class__.EXTRAS_MAP[type_]])
                                self.stdout.write("      Extra: (%s)%s: %s\n" %
                                                  (type_, key, self.__class__.EXTRAS_MAP[type_]))

                        pyIntent = android.Intent(action=action,
                                                  component=[package.packageName, component.name],
                                                  extras=extras)
                        realIntent = pyIntent.buildIn(self)
                        self.stdout.write("      Sending intent......\n")

                        shell.read()

                        try:
                            if ctype == "service":
                                self.getContext().startService(realIntent)
                            elif ctype == "receiver":
                                self.getContext().sendBroadcast(realIntent)
                            # wait until system_server process prints all the permissions check
                            time.sleep(3)
                        except:
                            self.stdout.write("      Exception occured while sending Intent\n")
                            break

                        logs = shell.read()
                        [resultPermissions, new_extras] = self.__check_permission_leak(logs, component, uid)

                        # Remove permissions checked in manifest.xml
                        component_perm = str(component.permission)
                        if component_perm and component_perm != "null":
                            if component_perm in resultPermissions:
                                resultPermissions.pop(resultPermissions.index(component_perm))
                        # If the process use some permission related API and it doesn't has any permission request!!
                        if len(resultPermissions) > 0:
                            self.stdout.write("        *Permission Leak Found!!!!!!!!!!\n")
                            pl = PermLeak(action, "", extras, resultPermissions)
                            if ctype == "service":
                                report.add_service_leak(str(component.name), pl)
                            elif ctype == "receiver":
                                report.add_receiver_leak(str(component.name), pl)
                            for pm in resultPermissions:
                                self.stdout.write("         %s\n" % pm)
                        else:
                            self.stdout.write("        No Potential leak.\n")

                        if new_extras.issubset(extra_keys):
                            stop = True
                        else:
                            extra_keys = extra_keys.union(new_extras)
                        self.stdout.write("\n")
            return

    def __check_permission_leak(self, logs, component, uid):
        lines = logs.split("\n")
        resultPermissions = []
        extras = []
        for line in lines:
            if line.find(str(uid)) == -1:
                continue
            if line.find("ContextImplcheckPermission") == 2:
                if self.__parse_uid_from_log_line(line) == uid:
                    pi = line.rfind("Permission: ") + 12
                    perm = line[pi:].split(",", 1)[0]
                    resultPermissions.append(perm)
                    continue
            if line.find("IntentExtra") == 2:
                if self.__parse_uid_from_log_line(line) == uid:
                    ki = line.rfind("key: ") + 5
                    key = line[ki:].split(",", 1)[0]
                    ti = line.rfind("type: ") + 6
                    type_ = line[ti:].split(",", 1)[0]
                    extras.append((type_, key))
                    continue
        resultPermissions = list(set(resultPermissions))
        return [resultPermissions, set(extras)]

    def __get_app_list(self, path):
        app_list = []
        for (dirpath, dirname, filename) in os.walk(path):
            app_list.extend(filename)
        app_list = [app[:-4] for app in app_list]
        return app_list

    def __install_app(self, app_path, package_name):
        filepath = os.path.join(app_path, package_name) + ".apk"
        print "Installing %s......" % (package_name)
        output = subprocess.check_output(["adb", "install", filepath])
        print output
        if output.find("Failure") >= 0:
            return False
        else:
            return True

    def __uninstall_app(self, app_path, package_name):
        print "Uninstalling %s......" % (package_name)
        output = subprocess.check_output(["adb", "uninstall", package_name])
        print output
        if output.find("Failure") >= 0:
            return False
        else:
            return True

    def __report__exists(self, report_path, package_name):
        filepath = os.path.join(report_path, package_name) + ".pickle"
        if not os.path.isfile(filepath):
            return False
        filepath = os.path.join(report_path, package_name) + ".report"
        if not os.path.isfile(filepath):
            return False
        return True

    def __parse_uid_from_log_line(self, line):
        start = line.rfind("UID: ") + 5
        end = line.rfind("#")
        return int(line[start:end])

    def __find_filters(self, ctype, component):
        try:
            xml = ElementTree.fromstring(self.getAndroidManifest(component.packageName),)
        except UnicodeEncodeError:
            logging.basicConfig(filename='log/xml_parse_error.log')
            logging.error(component.packageName)
            return []
        if xml is None:
            return []
        component_short_name = str(component.name)[len(component.packageName) + 1:]
        xpath_filter = "./application/%s[@name='%s']/intent-filter" % (ctype, component_short_name)
        filters = xml.findall(xpath_filter)
        return filters

    def __find_actions(self, filter_):
        if filter_ is None:
            return []
        actions_xml = filter_.findall("./action")
        actions = [a.attrib['name'] for a in actions_xml]
        return actions

    def __get_data_repr(self, filter_):
        if filter_ is None:
            return ""
        data_xml = filter_.findall("./data")
        repr_ = ""
        for d in data_xml:
            repr_ += ElementTree.tostring(d)
        return repr_

    def __find_data(self, filter_):
        if filter_ is None:
            return []
        data_xml = filter_.findall("./data")
        data_list = []
        for d in data_xml:
            attrib_dict = d.attrib
            if "mimeType" in attrib_dict:
                type_ = attrib_dict["mimeType"]
            else:
                type_ = ""
            if "schema" in attrib_dict:
                schema = attrib_dict["schema"]
            else:
                schema = ""
            if "host" in attrib_dict:
                host = attrib_dict["host"]
            else:
                host = ""
            if "port" in attrib_dict:
                port = attrib_dict["port"]
            else:
                port = ""
            if "path" in attrib_dict:
                path = attrib_dict["path"]
            else:
                path = ""
            data_list.append((type_, schema, host, port, path))
        return data_list

