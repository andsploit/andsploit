import os
import cPickle


class IntentFuzzerReport(object):
    def __init__(self, package_name):
        self.package_name = package_name
        self.service_leaks = {}
        self.receiver_leaks = {}

    def add_service_leak(self, service_name, perm_leak):
        if service_name in self.service_leaks:
            self.service_leaks[service_name].append(perm_leak)
        else:
            self.service_leaks[service_name] = [perm_leak]

    def add_receiver_leak(self, receiver_name, perm_leak):
        if receiver_name in self.receiver_leaks:
            self.receiver_leaks[receiver_name].append(perm_leak)
        else:
            self.receiver_leaks[receiver_name] = [perm_leak]

    def gen_report(self, path):
        file_path = os.path.join(path, self.package_name) + ".report"
        f = open(file_path, 'w')
        f.write(repr(self))
        f.close()

    def save(self, path):
        file_path = os.path.join(path, self.package_name) + ".pickle"
        f = open(file_path, 'w')
        data = (self.package_name,
                self.service_leaks,
                self.receiver_leaks)
        cPickle.dump(data, f)
        f.close()

        file_path = os.path.join(path, self.package_name) + ".report"
        f = open(file_path, 'w')
        data = repr(self)
        f.write(data)
        f.close()

    def load(self, path):
        file_path = os.path.join(path, self.package_name) + ".pickle"
        f = open(file_path, 'r')
        data = cPickle.load(f)
        self.package_name = data[0]
        self.service_leaks = data[1]
        self.receiver_leaks = data[2]
        f.close()

    def __repr__(self):
        r = "%s\n" % self.package_name
        for service_name, leaks in self.service_leaks.items():
            r += "\t%s\n" % service_name
            for leak in leaks:
                r += repr(leak)
        for receiver_name, leaks in self.receiver_leaks.items():
            r += "\t%s\n" % receiver_name
            for leak in leaks:
                r += repr(leak)
        return r + "\n"


class PermLeak(object):
    def __init__(self, action="", data="", extras=[], perms=[]):
        self.action = action
        self.data = data
        self.extras = extras
        self.perms = perms

    def __repr__(self):
        extras_reprs = []
        for extra in self.extras:
            extras_reprs.append("(%s)%s: %s" % (extra[0], extra[1], extra[2]))
        extras_repr = "[" + ", ".join(extras_reprs) + "]"
        intent_repr = "\t\taction: %s, data: %s, extras: %s\n" % (self.action, self.data, extras_repr)
        perms_repr = "\n".join(["\t\t*" + p for p in self.perms])
        return intent_repr + perms_repr + "\n"


