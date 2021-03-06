#!/usr/bin/python
"""
Python tests for SCSI-3 Persistent Group Reservations

Description:
 This module tests Exclusive Access Reservations.
"""


__author__ = "Lee Duncan <leeman.duncan@gmail.com>"


import sys
import os
import time
import unittest

from support.initiator import initA, initB, initC
from support.reservation import ProutTypes
from support.setup import set_up_module

my_rtype = ProutTypes["ExclusiveAccess"]

################################################################

def setUpModule():
    """Whole-module setup"""
    set_up_module(initA, initB, initC)

################################################################

def my_resvn_setup():
    """make sure we are all setup to test reservations"""
    initA.clear()
    initA.runTur()
    initB.clear()
    initB.runTur()
    initA.register()
    initB.register()
    initC.runTur()

################################################################

class test01CanReserveTestCase(unittest.TestCase):
    """Test that PGR RESERVE Exclusive Access can be set"""

    def setUp(self):
        my_resvn_setup()

    def testCanReserve(self):
        res = initA.reserve(my_rtype)
        self.assertEqual(res, 0)

################################################################

class test02CanReadReservationTestCase(unittest.TestCase):
    """Test that PGR RESERVE Exclusive Access can be read"""

    def setUp(self):
        my_resvn_setup()
        initA.reserve(my_rtype)

    def testCanReadReservationFromReserver(self):
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
 
    def testCanReadReservationFromNonReserver(self):
        resvnB = initB.getReservation()
        self.assertEqual(resvnB.key, initA.key)
        self.assertEqual(resvnB.getRtypeNum(), my_rtype)

    def testCanReadReservationFromNonRegistrant(self):
        resvnC = initC.getReservation()
        self.assertEqual(resvnC.key, initA.key)
        self.assertEqual(resvnC.getRtypeNum(), my_rtype)

################################################################

class test03CanReleaseReservationTestCase(unittest.TestCase):
    """Test that PGR RESERVE Exclusive Access can be released"""

    def setUp(self):
        my_resvn_setup()
        initA.reserve(my_rtype)
        time.sleep(2)                   # give I/O time to sync up

    def testCanReleaseReservation(self):
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
        res = initA.release(my_rtype)
        self.assertEqual(res, 0)
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, None)
        self.assertEqual(resvnA.rtype, None)
    
    def testCannotReleaseReservation(self):
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
        res = initB.release(my_rtype)
        self.assertEqual(res, 0)
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)

################################################################

class test04UnregisterHandlingTestCase(unittest.TestCase):
    """Test how PGR RESERVE Exclusive Access reservation is handled
    during unregistration"""

    def setUp(self):
        my_resvn_setup()
        initA.reserve(my_rtype)

    def testUnregisterReleasesReservation(self):
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
        res = initA.unregister()
        self.assertEqual(res, 0)
        time.sleep(1)                   # for stgt
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, None)
        self.assertEqual(resvnA.rtype, None)

    def testUnregisterDoesNotReleaseReservation(self):
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
        res = initB.unregister()
        self.assertEqual(res, 0)
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)

################################################################

class test05ReservationAccessTestCase(unittest.TestCase):
    """Test how PGR RESERVE Exclusive Access reservation acccess is
    handled"""

    def setUp(self):
        my_resvn_setup()
        initA.reserve(my_rtype)
        time.sleep(2)                   # give I/O time to sync up

    def testReservationHolderHasReadAccess(self):
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
        # initA read from disk to /dev/null
        ret = initA.readFromTarget()
        self.assertEqual(ret.result, 0)
        
    def testReservationHolderHasWriteAccess(self):
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
        # initA can write from /dev/zero to 2nd 512-byte block on disc
        ret = initA.writeToTarget()
        self.assertEqual(ret.result, 0)
    
    def testNonReservationHolderDoesNotHaveReadAccess(self):
        # initA get reservation
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
        # initB can't read from disk to /dev/null
        ret = initB.readFromTarget()
        self.assertEqual(ret.result, 1)

    def testNonReservationHolderDoesNotHaveWriteAccess(self):
        # initA get reservation
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
        # initB can't write from /dev/zero to 2nd 512-byte block on disc
        ret = initB.writeToTarget()
        self.assertEqual(ret.result, 1)

    def testNonRegistrantDoesNotHaveReadAccess(self):
        # initA get reservation
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
        # initC can't read from disk to /dev/null
        ret = initC.readFromTarget()
        self.assertEqual(ret.result, 1)

    def testNonRegistrantDoesNotHaveWriteAccess(self):
        # initA get reservation
        resvnA = initA.getReservation()
        self.assertEqual(resvnA.key, initA.key)
        self.assertEqual(resvnA.getRtypeNum(), my_rtype)
        # initC can't write from /dev/zero to 2nd 512-byte block on disc
        ret = initC.writeToTarget()
        self.assertEqual(ret.result, 1)
