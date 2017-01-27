#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 11:40:28 2016

@author: vilhuber
"""

import csv
import re

#csvFile = '2014 SIPP Internal Codebook 10.6.16.csv'
csvFile = '2014 SIPP Internal Codebook 10.6.16 UPDATED.csv'
csvData = csv.reader(open(csvFile))
xmlFile = "test.xml"
xmlData = open(xmlFile, 'w')

vars = dict()

for row in csvData:
    print("Variable: ",row[1])
    # test if block exists
    if not row[0] in vars:
        vars[row[0]] = set()
    vars[row[0]].add(row[1])

for block, items in vars.items():
    xmlData.write('  <varGrp ID="' + block + '" var="')
    for var in items:
        xmlData.write(var + " ")
    xmlData.write('">')
