# Copyright 2017 Politecnico di Torino
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Simple tests for the CyberTop class.

@author: Daniele Canavese
"""

import sys
sys.path.append("..")

# from cybertop.cybertop import CyberTop
from cybertop.util import getHSPLNamespace
import unittest
from cybertop.cybertop import CyberTop
import os

def getTestFilePath(filename):
    """
    Retrieves a file in the test directory.
    @param filename: The file name to use.
    @return: The file path.
    """
    return os.path.join(os.path.dirname(__file__), filename)

class BasicTest(unittest.TestCase):
    """
    Basic test class.
    """

    def _doHSPLTest(self, attackFile, landscapeFile, expectedCount, expectedProtocols, expectedActions, expectedSubjects = None, expectedObjectPorts = None):
        """
        Tests the HSPL generation.
        @param attackFile: The attack file to read.
        @param landscapeFile: The CSF file to read.
        @param expectedCount: The number of expected recommendation.
        @param expectedProtocols: The expected protocol list.
        @param expectedActions: The expected actions list.
        @param expectedSubjects: The expected subject list or None if this test must be skipped.
        @param expectedObjectPorts: The expected object port list or None if this test must be skipped.
        """
        cyberTop = CyberTop(getTestFilePath("cybertop.cfg"), getTestFilePath("logging.ini"))
    
        r = cyberTop.getMSPLsFromFile(getTestFilePath(attackFile), getTestFilePath(landscapeFile))
        self.assertIsNotNone(r)
        [recommendation, _] = r
        self.assertEqual(expectedCount, len(recommendation))
                
        for hsplSet in recommendation:
            good = True
            protocols = hsplSet.findall("{%s}hspl/{%s}traffic-constraints/{%s}type" % (getHSPLNamespace(), getHSPLNamespace(), getHSPLNamespace()))
            if len(protocols) != len(expectedProtocols):
                good = False
                continue
            p1 = []
            for i in protocols:
                p1.append(i.text)
            p1 = sorted(p1)
            p2 = sorted(expectedProtocols)
            for i in range(len(protocols)):
                if p1[i] != p2[i]:
                    good = False
            actions = hsplSet.findall("{%s}hspl/{%s}action" % (getHSPLNamespace(), getHSPLNamespace()))
            objects = hsplSet.findall("{%s}hspl/{%s}object" % (getHSPLNamespace(), getHSPLNamespace()))
            subjects = hsplSet.findall("{%s}hspl/{%s}subject" % (getHSPLNamespace(), getHSPLNamespace()))
            self.assertEqual(len(actions), len(expectedActions))
            for i in range(len(actions)):
                if actions[i].text != expectedActions[i]:
                    good = False
            if expectedSubjects is not None:
                if len(subjects) != len(expectedSubjects):
                    good = False
                for i in range(0, len(subjects)):
                    if subjects[i].text != expectedSubjects[i]:
                        good = False
            if expectedObjectPorts is not None:
                if len(objects) != len(expectedObjectPorts):
                    good = False
                for i in range(0, len(objects)):
                    parts = objects[i].text.split(":")
                    if len(parts) != 2:
                        good = False
                    if parts[1] != expectedObjectPorts[i]:
                        good = False
            
            if good:
                return
        
        self.fail("No HSPL set respect the expectations!")

    def _doObjectTest(self, attackFile, landscapeFile, maximumHSPLs, expectedObjects):
        """
        Tests the HSPL generation.
        @param attackFile: The attack file to read.
        @param maximumHSPLs: The maximum number of HSPLs.
        @param landscapeFile: The CSF file to read.
        @param expectedObjects: The list of expected objects.
        """
        cyberTop = CyberTop(getTestFilePath("cybertop.cfg"), getTestFilePath("logging.ini"))
    
        r = cyberTop.getMSPLsFromFile(getTestFilePath(attackFile), getTestFilePath(landscapeFile))
        self.assertIsNotNone(r)
        [recommendation, _] = r
        for hsplSet in recommendation:
            objects = hsplSet.findall("{%s}hspl/{%s}object" % (getHSPLNamespace(), getHSPLNamespace()))
            self.assertLessEqual(len(objects), maximumHSPLs)
            for i in range(len(objects)):
                self.assertIn(objects[i].text, expectedObjects)

class TestDoS(BasicTest):
    """
    Tests the DoS attack responses.
    """
        
    def test_veryHighTCP(self):
        """
        Tests the TCP flood, very high severity.
        """
        self._doHSPLTest("Very high-DoS-1.csv", "landscape1.xml", 2, ["TCP"] * 2, ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very high-DoS-1.csv", "landscape1.xml", 2, ["TCP"] * 2, ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very high-DoS-1.csv", "landscape2.xml", 1, ["TCP"] * 2, ["drop"] * 2, None, ["*"] * 2)
        
    def test_highTCP(self):
        """
        Tests the TCP flood, high severity.
        """
        self._doHSPLTest("High-DoS-1.csv", "landscape1.xml", 2, ["TCP"] * 2, ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("High-DoS-1.csv", "landscape1.xml", 2, ["TCP"] * 2, ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("High-DoS-1.csv", "landscape2.xml", 1, ["TCP"] * 2, ["drop"] * 2, None, ["*"] * 2)
    
    def test_lowTCP(self):
        """
        Tests the TCP flood, low severity.
        """
        self._doHSPLTest("Very low-DoS-1.csv", "landscape1.xml", 2, ["TCP"] * 2, ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very low-DoS-1.csv", "landscape1.xml", 2, ["TCP"] * 2, ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very low-DoS-1.csv", "landscape2.xml", 1, ["TCP"] * 2, ["drop"] * 2, None, ["*"] * 2)

    def test_veryLowTCP(self):
        """
        Tests the TCP flood, low severity.
        """
        self._doHSPLTest("Very low-DoS-1.csv", "landscape1.xml", 2, ["TCP"] * 2, ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very low-DoS-1.csv", "landscape1.xml", 2, ["TCP"] * 2, ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very low-DoS-1.csv", "landscape2.xml", 1, ["TCP"] * 2, ["drop"] * 2, None, ["*"] * 2)

    def test_veryHighUDP(self):
        """
        Tests the UDP flood, very high severity.
        """
        self._doHSPLTest("Very high-DoS-2.csv", "landscape1.xml", 2, ["UDP"] * 2, ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very high-DoS-2.csv", "landscape1.xml", 2, ["UDP"] * 2, ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very high-DoS-2.csv", "landscape2.xml", 1, ["UDP"] * 2, ["drop"] * 2, None, ["*"] * 2)
        
    def test_highUDP(self):
        """
        Tests the UDP flood, high severity.
        """
        self._doHSPLTest("High-DoS-2.csv", "landscape1.xml", 2, ["UDP"] * 2, ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("High-DoS-2.csv", "landscape1.xml", 2, ["UDP"] * 2, ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("High-DoS-2.csv", "landscape2.xml", 1, ["UDP"] * 2, ["drop"] * 2, None, ["*"] * 2)

    def test_lowUDP(self):
        """
        Tests the TCP flood, low severity.
        """
        self._doHSPLTest("Very low-DoS-2.csv", "landscape1.xml", 2, ["UDP"] * 2, ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very low-DoS-2.csv", "landscape1.xml", 2, ["UDP"] * 2, ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very low-DoS-2.csv", "landscape2.xml", 1, ["UDP"] * 2, ["drop"] * 2, None, ["*"] * 2)

    def test_veryLowUDP(self):
        """
        Tests the TCP flood, low severity.
        """
        self._doHSPLTest("Very low-DoS-2.csv", "landscape1.xml", 2, ["UDP"] * 2, ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very low-DoS-2.csv", "landscape1.xml", 2, ["UDP"] * 2, ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very low-DoS-2.csv", "landscape2.xml", 1, ["UDP"] * 2, ["drop"] * 2, None, ["*"] * 2)

    def test_VeryHighTCPAndUDP(self):
        """
        Tests the UDP flood, very high severity.
        """
        self._doHSPLTest("Very high-DoS-3.csv", "landscape1.xml", 2, ["TCP", "UDP"], ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very high-DoS-3.csv", "landscape1.xml", 2, ["TCP", "UDP"], ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very high-DoS-3.csv", "landscape2.xml", 1, ["TCP", "UDP"], ["drop"] * 2, None, ["*"] * 2)

    def test_highTCPAndUDP(self):
        """
        Tests the UDP flood, high severity.
        """
        self._doHSPLTest("High-DoS-3.csv", "landscape1.xml", 2, ["TCP", "UDP"], ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("High-DoS-3.csv", "landscape1.xml", 2, ["TCP", "UDP"], ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("High-DoS-3.csv", "landscape2.xml", 1, ["TCP", "UDP"], ["drop"] * 2, None, ["*"] * 2)

    def test_lowTCPAndUDP(self):
        """
        Tests the UDP flood, high severity.
        """
        self._doHSPLTest("Low-DoS-3.csv", "landscape1.xml", 2, ["TCP", "UDP"], ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Low-DoS-3.csv", "landscape1.xml", 2, ["TCP", "UDP"], ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Low-DoS-3.csv", "landscape2.xml", 1, ["TCP", "UDP"], ["drop"] * 2, None, ["*"] * 2)

    def test_veryLowTCPAndUDP(self):
        """
        Tests the UDP flood, high severity.
        """
        self._doHSPLTest("Very low-DoS-3.csv", "landscape1.xml", 2, ["TCP", "UDP"], ["limit"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very low-DoS-3.csv", "landscape1.xml", 2, ["TCP", "UDP"], ["drop"] * 2, None, ["*"] * 2)
        self._doHSPLTest("Very low-DoS-3.csv", "landscape2.xml", 1, ["TCP", "UDP"], ["drop"] * 2, None, ["*"] * 2)

    def test_big(self):
        """
        Tests a big DoS attack with 1000 clients.
        """
        self._doHSPLTest("Very high-DoS-4.csv", "landscape1.xml", 2, ["TCP"] * 8, ["drop"] * 8, None, ["*"] * 8)
        self._doHSPLTest("Very high-DoS-4.csv", "landscape1.xml", 2, ["TCP"] * 8, ["limit"] * 8, None, ["*"] * 8)
        self._doHSPLTest("Very high-DoS-4.csv", "landscape2.xml", 1, ["TCP"] * 8, ["drop"] * 8, None, ["*"] * 8)

class TestDNSTunneling(BasicTest):
    """
    Tests the DNS tunneling attack responses.
    """
        
    def test_veryHighDNS(self):
        """
        Tests the DNS tunneling, very high severity.
        """
        self._doHSPLTest("Very high-DNS tunneling-1.csv", "landscape1.xml", 1, ["TCP+UDP"], ["drop"], None, ["*"])
        self._doHSPLTest("Very high-DNS tunneling-1.csv", "landscape2.xml", 1, ["TCP+UDP"], ["drop"], None, ["*"])
        
    def test_highDNS(self):
        """
        Tests the DNS tunneling, very high severity.
        """
        self._doHSPLTest("High-DNS tunneling-1.csv", "landscape1.xml", 1, ["TCP+UDP"], ["drop"], None, ["*"])
        self._doHSPLTest("High-DNS tunneling-1.csv", "landscape2.xml", 1, ["TCP+UDP"], ["drop"], None, ["*"])
        
    def test_lowDNS(self):
        """
        Tests the DNS tunneling, very high severity.
        """
        self._doHSPLTest("Low-DNS tunneling-1.csv", "landscape1.xml", 1, ["TCP+UDP"], ["drop"], None, ["*"])
        self._doHSPLTest("Low-DNS tunneling-1.csv", "landscape2.xml", 1, ["TCP+UDP"], ["drop"], None, ["*"])
        
    def test_veryLowDNS(self):
        """
        Tests the DNS tunneling, very high severity.
        """
        self._doHSPLTest("Very low-DNS tunneling-1.csv", "landscape1.xml", 1, ["TCP+UDP"], ["drop"], None, ["*"])
        self._doHSPLTest("Very low-DNS tunneling-1.csv", "landscape2.xml", 1, ["TCP+UDP"], ["drop"], None, ["*"])

    def test_big(self):
        """
        Tests a big DNS tunneling attack.
        """
        self._doHSPLTest("High-DNS tunneling-2.csv", "landscape1.xml", 1, ["TCP+UDP"], ["drop"], ["0.0.0.0/0:53"])
        self._doHSPLTest("High-DNS tunneling-2.csv", "landscape2.xml", 1, ["TCP+UDP"], ["drop"], ["0.0.0.0/0:53"])

    def test_filters(self):
        """
        Tests the DNS tunneling filters.
        """
        self._doHSPLTest("High-DNS tunneling-3.csv", "landscape1.xml", 1, ["TCP+UDP"] * 3, ["drop"] * 3, ["0.0.0.0/0:53"] * 3)
        self._doHSPLTest("High-DNS tunneling-3.csv", "landscape2.xml", 1, ["TCP+UDP"] * 3, ["drop"] * 3, ["0.0.0.0/0:53"] * 3)

class TestCryptomining(BasicTest):
    """
    Tests the cryptomining attack responses.
    """
        
    def test_lowCryptomining(self):
        """
        Tests the cryptomining, low severity.
        """
        self._doHSPLTest("Low-Cryptocurrency Mining-1.csv", "landscape1.xml", 1, ["TCP"] * 2, ["drop"] * 2, ["35.177.197.177:3333", "10.0.2.15:34991"], ["34991", "3333"])
        self._doHSPLTest("Low-Cryptocurrency Mining-1.csv", "landscape2.xml", 1, ["TCP"] * 2, ["drop"] * 2, ["35.177.197.177:3333", "10.0.2.15:34991"], ["34991", "3333"])

class TestWorm(BasicTest):
    """
    Tests the Worm attack responses.
    """
        
    def test_veryHighWorm(self):
        """
        Tests the worm, very high severity.
        """
        self._doHSPLTest("Very High-wannacry-1.csv", "landscape1.xml", 2, ["TCP"] * 6 + ["UDP"] * 12, ["drop"] * 18, ["*:*"] * 18, ["*"] * 18)
        self._doHSPLTest("Very High-wannacry-1.csv", "landscape1.xml", 2, ["TCP"] * 6 + ["UDP"] * 12, ["limit"] * 18, ["*:*"] * 18, ["*"] * 18)
        self._doHSPLTest("Very High-wannacry-1.csv", "landscape2.xml", 1, ["TCP"] * 6 + ["UDP"] * 12, ["drop"] * 18, ["*:*"] * 18, ["*"] * 18)
        
    def test_highWorm(self):
        """
        Tests the worm, high severity.
        """
        self._doHSPLTest("High-Worm-1.csv", "landscape1.xml", 2, ["TCP"] * 2, ["drop"] * 2, ["*:*"] * 2, ["*"] * 2)
        self._doHSPLTest("High-Worm-1.csv", "landscape1.xml", 2, ["TCP"] * 2, ["limit"] * 2, ["*:*"] * 2, ["*"] * 2)
        self._doHSPLTest("High-Worm-1.csv", "landscape2.xml", 1, ["TCP"] * 2, ["drop"] * 2, ["*:*"] * 2, ["*"] * 2)

class TestHSPLMerging(BasicTest):
    """
    Tests the HSPL merging.
    """

    def test_mergeAnyPorts(self):
        """
        Tests that any ports merging.
        """
        self._doObjectTest("Very low-DoS-4.csv", "landscape1.xml", 10, ["91.211.1.100:*"])

    def test_mergeSubnets(self):
        """
        Tests the subnets merging.
        """
        self._doObjectTest("Very low-DoS-5.csv", "landscape1.xml", 10, [
            "91.211.1.0/31:*",
            "91.211.1.2/31:*",
            "91.211.1.4/31:*",
            "91.211.1.6/31:*",
            "91.211.1.8/31:*",
            "91.211.1.10/31:*"])
    def test_mergeAnyPortsWithInclusions(self):
        """
        Tests that any ports merging with some inclusions.
        """
        self._doObjectTest("Very low-DoS-6.csv", "landscape1.xml", 10, ["91.211.1.0:*"])

    def test_mergeSubnetsWithInclusions(self):
        """
        Tests the subnets merging with some inclusions.
        """
        self._doObjectTest("Very low-DoS-7.csv", "landscape1.xml", 10, [
            "91.211.1.0/31:*",
            "91.211.1.2/31:*",
            "91.211.1.4/31:*",
            "91.211.1.6/31:*",
            "91.211.1.8/31:*",
            "91.211.1.10/31:*"])

    def test_mergeAll(self):
        """
        Tests the any ports and subnets merging with some inclusions.
        """
        self._doObjectTest("Very low-DoS-8.csv", "landscape1.xml", 10, [
            "91.211.1.0/31:*",
            "91.211.1.2/31:*",
            "91.211.1.4/31:*",
            "91.211.1.6/31:*",
            "91.211.1.8/31:*",
            "91.211.1.10/31:*"])

    def test_mergeBig1(self):
        """
        Big test #1!
        """
        self._doObjectTest("Very low-DoS-9.csv", "landscape1.xml", 10, [
            "1.100.7.0/25:*",
            "1.100.7.128/25:*",
            "1.152.233.0/25:*",
            "1.152.233.128/25:*",
            "10.14.254.0/25:*",
            "10.14.254.128/25:*",
            "10.101.30.61:*",
            "100.114.244.0/25:*",
            "100.114.244.128/25:*"])

    def test_mergeBig2(self):
        """
        Big test #2!
        """
        self._doObjectTest("Very low-DoS-10.csv", "landscape1.xml", 10, ["1.2.3.4:*"])

    def test_mergeBig3(self):
        """
        Big test #3!
        """
        self._doObjectTest("Very low-DoS-11.csv", "landscape1.xml", 10, ["1.2.3.4:*", "1.2.3.5:*"])

    def test_mergeBig4(self):
        """
        Big test #4!
        """
        self._doObjectTest("Very low-DoS-12.csv", "landscape1.xml", 10, [
            "1.2.3.0/27:*",
            "1.2.3.32/27:*",
            "1.2.3.64/27:*",
            "1.2.3.96/27:*",
            "1.2.3.128/27:*",
            "1.2.3.160/27:*",
            "1.2.3.192/27:*",
            "1.2.3.224/27:*"])

    def test_mergeBig5(self):
        """
        Big test #5!
        """
        self._doObjectTest("Very low-DoS-13.csv", "landscape1.xml", 16, [
            "1.0.0.0/24:*",
            "1.0.50.0/24:*",
            "1.0.100.0/24:*",
            "1.0.150.0/24:*",
            "1.1.0.0/24:*",
            "1.1.50.0/24:*",
            "1.1.100.0/24:*",
            "1.1.150.0/24:*",
            "1.2.0.0/24:*",
            "1.2.50.0/24:*",
            "1.2.100.0/24:*",
            "1.2.150.0/24:*",
            "1.3.0.0/24:*",
            "1.3.50.0/24:*",
            "1.3.100.0/24:*",
            "1.3.150.0/24:*"])

class TestCSVParser(BasicTest):

    def test_parseHeaders(self):
        """
        Tests a CSV file with and without a header.
        """
        self._doHSPLTest("High-DoS-4.csv", "landscape1.xml", 2, ["TCP"] * 5, ["drop"] * 5)
        self._doHSPLTest("High-DoS-4.csv", "landscape1.xml", 2, ["TCP"] * 5, ["limit"] * 5)

    def test_parseSeparators(self):
        """
        Tests a CSV file with different separators.
        """
        self._doHSPLTest("High-DoS-6.csv", "landscape1.xml", 2, ["TCP"] * 5, ["drop"] * 5)
        self._doHSPLTest("High-DoS-6.csv", "landscape1.xml", 2, ["TCP"] * 5, ["limit"] * 5)

    def test_parseEmptyLines(self):
        """
        Tests a CSV file with some empty lines.
        """
        self._doHSPLTest("High-DoS-8.csv", "landscape1.xml", 2, ["TCP"] * 5, ["drop"] * 5)
        self._doHSPLTest("High-DoS-8.csv", "landscape1.xml", 2, ["TCP"] * 5, ["limit"] * 5)

    def test_parseComments(self):
        """
        Tests a CSV file with some comments.
        """
        self._doHSPLTest("High-DoS-9.csv", "landscape1.xml", 2, ["TCP"] * 5, ["drop"] * 5)
        self._doHSPLTest("High-DoS-9.csv", "landscape1.xml", 2, ["TCP"] * 5, ["limit"] * 5)

if __name__ == "__main__":
    unittest.main()
