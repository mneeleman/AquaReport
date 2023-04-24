from AquaComp import *


def test_loadaquareport(ar_file1='./TestAR/E2E9.1.00060.S_2023_04_11.AquaReport.xml'):
    return load_aquareport(ar_file1)


def test_compareaquareport(ar_file1='../AquaReports/E2E9.1.00060.S_2023_04_11.AquaReport.xml',
                           ar_file2='../AquaReports/E2E9.1.00060.S_2023_04_12.AquaReport.xml'):
    return compare_aquareports(ar_file1, ar_file2)
