#!/usr/bin/python
"""
Initiator Class for testing PGR
"""

from dprint import dprint
from cmd import runCmdWithOutput
from reservation import Reservation


class Initiator:
    """A General PGR initiator"""
    def __init__(self, dev, key, opts):
        self.dev = dev
        self.key = key
        self.opts = opts

    def runSgCmdWithOutput(self, cmd):
        """Run the SG command on specified host"""
        my_cmd = ["sg_persist", "-n"] + cmd + [self.dev]
        return runCmdWithOutput(my_cmd, self.opts)

    def getRegistrants(self):
        """Get list of registrants using specified initiator"""
        registrants = []
        res = self.runSgCmdWithOutput(["-k"])
        if "no registered reservation keys" not in res.lines[0].lower():
            for l in res.lines[1:]:
                dprint(self.opts, "key=", l.strip())
                registrants.append(l.strip())
        dprint(self.opts, "returning registrants list=", registrants)
        return registrants

    def register(self):
        """Register the remote I_T Nexus"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--register",
             "--param-sark=" + self.key])
        return res.result

    def registerAndIgnore(self, new_key):
        """Register the remote I_T Nexus"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--register",
             "--param-rk=" + self.key,
             "--param-sark=" + new_key])
        return res.result

    def unregister(self):
        """UnRegister the remote I_T Nexus"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--register",
             "--param-rk=" + self.key])
        return res.result

    def reserve(self, prout_type):
        """Reserve for the host using the supplied type"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--reserve",
             "--param-rk=" + self.key,
             "--prout-type=" + prout_type])
        return res.result

    def getReservation(self):
        """Get current reservation"""
        res = self.runSgCmdWithOutput(["-r"])
        dprint(self.opts,
               "Parsing %d lines of reservations:" % len(res.lines))
        for o in res.lines:
            dprint(self.opts, "line=", o)
        rr = Reservation(self.opts)
        if "Reservation follows" in res.lines[0]:
            rr.key = res.lines[1].split("=")[1]
            pcs = res.lines[2].split(",")
            rr.rtype = pcs[1].split(":")[1].strip()
            dprint(self.opts,
                   "Reservation: found key=", rr.key, "type=", rr.rtype)
        else:
            dprint(self.opts, "No Reservation found")
        return rr

    def release(self, prout_type):
        """Reserve for the host using the supplied type"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--release",
             "--param-rk=" + self.key,
             "--prout-type=" + prout_type])
        return res.result

    def clear(self):
        """Clear Registrations and Reservation on a target"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--clear",
             "--param-rk=" + self.key])
        return res.result

    def getDiskInquirySn(self):
        """Get the Disk Serial Number"""
        res = runCmdWithOutput(["sg_inq", self.dev], self.opts)
        ret = None
        if res.result == 0:
            if "Unit serial number" in res.lines[-1]:
                line = res.lines[-1]
                ret = line.split()[-1]
        dprint(self.opts, "getDiskInquirySn(%s) -> %s" % (self.dev, ret))
        return ret

    def runTur(self):
        """Clear any UA by sending TUR"""
        res = runCmdWithOutput(["sg_turs", self.dev], self.opts)
        return res.result
