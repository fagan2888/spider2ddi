#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 11:40:28 2016

@author: vilhuber
"""

# csv2xml.py
# FB - 201010107
# First row of the csv file must be header!

# example CSV file: myData.csv
# id,code name,value
# 36,abc,7.6
# 40,def,3.6
# 9,ghi,6.3
# 76,def,99

import csv
import re

csvFile = '2014 SIPP Internal Codebook 10.6.16.csv'
#csvFile = '2014 SIPP Internal Codebook 10.6.16 UPDATED.csv'
xmlFile = '2014_SIPP_Internal.xml'
headerFile = 'SIPP_header.xml'

csvData = csv.reader(open(csvFile))
headerData = open(headerFile, 'r')
xmlData = open(xmlFile, 'w')

# copy header
for line in headerData:
    xmlData.write(line)

#xmlData.write('<?xml version="1.0" encoding="UTF-8"?>' + "\n")
#xmlData.write('<codeBook xmlns:act="http://ced2ar.org/ns/activities#" xmlns:ced2ar="http://ced2ar.org/ns/core#" xmlns:RePEc="https://ideas.repec.org/#" xmlns:exn="http://ced2ar.org/ns/external#" xmlns:repeca="https://ideas.repec.org/e/#" xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:tr="http://example.com/ns/tr#" xmlns:ex="http://example.com/ns/ex#" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:prov="http://www.w3.org/ns/prov#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:saxon="http://xml.apache.org/xslt" xmlns:ns0="http://purl.org/dc/elements/1.1/" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:dc="http://purl.org/dc/terms/" xmlns="ddi:codebook:2_5" xsi:schemaLocation="ddi:codebook:2_5 http://www.ncrn.cornell.edu/docs/ddi/2.5.NCRN.P/schemas/codebook.xsd">' + "\n")


# there must be only one top-level tag
xmlData.write('<dataDscr>' + "\n")

# map the inputs to the DDI paths
# mapping (element/attrib, type, path1, path2, path3 )
options = {'Name' : ('name','attrib') ,
           'Length' : ('width', 'attrib', 'location') ,
           'Description' : ('labl', 'element') ,
           'Universe Description' : ('anlysUnit', 'element') ,
           'Min' : ('min', 'retain', 'range', 'valrng') ,
           'Max' : ('max', 'attrib', 'range', 'valrng') ,
           'Universe' : ('universe', 'element') ,
           'Answer List' : ('catproc', 'element') ,
           'Values' : ( 'catValu', 'element', 'catgry') ,
           'Allocation Name' : ('notes', 'element' ) ,
}

#           'Answer List' : ('txt', 'element', 'catgry') ,
#            'Allocation Name' : ('var', 'attrib', 'derivation' ) ,

cdata = {  'Universe' : ('universe') ,
}

postprocess ={   'Answer List' : ('txt') ,
}

def cleanrow (mydata):
            # clean the data
            myrow = re.sub(r'&',r'and',mydata)
            myrow = re.sub(r'<>',r'!=',myrow)
#            myrow = re.sub(r'<=',r' LE ',myrow)
#            myrow = re.sub(r'<',r' LT ',myrow)
#            myrow = re.sub(r'>',r' GT ',myrow)
            return myrow

def catproc (mydata):
    catrows = mydata.replace('\n', '\r').split('\r')
    myrow = ''
    for catrow in catrows:
        # process the embedded variable lists
        myrow += re.sub('(\d*)\. (.*)',r'   <catgry><catValu>\1<catValu><labl>\2</labl></catgry>\n', catrow)
    return myrow


# python dictionaries don't have an oder
# ordre of DDI elements from http://www.ddialliance.org/sites/default/files/StylesheetMapping-variable-fields.txt
order = {  0: 'Name' ,
           1: 'Length' ,
           2: 'Description' ,
           7: 'Universe Description' ,
           9: 'Min' ,
           9: 'Max' ,
           12: 'Universe' ,
           15: 'Answer List' ,
           18: 'Values' ,
           22: 'Allocation Name' ,
}
# describe the mixed dictionary above - 0-based!
levels = { 'attrib': 3 ,
           'element' : 2 }
rowNum = 0
attribute = 'attrib'
element = 'element'

for row in csvData:
    if rowNum == 0:
        tags = row
    else:
        # start the entry
        xmlData.write('  <var ' )
        for select in options:
            for i in range(len(tags)):
                # only the var attributes have length 2
                if attribute in options[select] and \
                    len(options[select]) == 2:
                    #print("Attribute found",options[select])
                    if tags[i] == select:
                        xmlData.write(' ' + options[select][0] + '="' \
                            + cleanrow(row[i]) + '"')
        # end the var statement
        xmlData.write('>' + "\n")
        # we will write out the label one too
#        xmlData.write('<labl>' + row[0] + '</labl>\n')
        for num in sorted(order):
            #print("num = " , num)
            #print("order[num] = " , order[num])
            select = order[num]
            #print("select = " , select)
            for i in range(1,len(tags)):
                    if tags[i] == select:
                        #print("select=",select," i=",i, " rowNum=", rowNum)
                        # if it is deeper in the hierarchy, we need to write out the elements first
                        #print("Entering loop")
                        #print("len(options[select])",len(options[select]))
                        #print("options[select]",options[select])
                        if row[i] != "":
                            #print("row[i]=",row[i])
                            higher_range = 0
                            if (len(options[select]) > levels[element] and  element in options[select] ) :
                                for j in range(levels[element],len(options[select])):
                                    #print("higher ",options[select][j])
                                    xmlData.write('    <' + options[select][j] +  '>' + "\n" )
                            if ( len(options[select]) > levels[attribute] and attribute in options[select] ):
                                #print("Entering higher order ",len(options[select]))
                                for j in range(levels[attribute],len(options[select])):
                                    #print("higher ",options[select][j])
                                    xmlData.write('    <' + options[select][j] +  '>' + "\n" )


                            if attribute in options[select]:
                            #    print(rowNum, ": entering attribute loop for",options[select][0])
                                xmlData.write('    <' + options[select][2] + ' ' \
                                    + options[select][0] + '="' \
                                    + cleanrow(row[i]) + '" />\n')


                            #if element in options[select] and select != "Answer List":
                            if element in options[select] :
                                # it is an element
                                print(rowNum, ": entering element loop for", options[select][0])
                                if select != "Answer List":
                                    xmlData.write('    <' + options[select][0] + '>' )
                                if select in cdata:
                                    xmlData.write('<![CDATA[')
                                myrow = cleanrow(row[i])
                                if select in postprocess:
                                    print(rowNum, ": entering catproc processing", options[select][0])
                                    print(rowNum, ": row[i]", row[i])
                                    myrow = catproc( row[i] )
                                xmlData.write( myrow )
                                if select in cdata:
                                    xmlData.write(']]>')
                                if select != "Answer List":
                                    xmlData.write( '</' + options[select][0] + '>' + "\n" )

#                            if element in options[select] and select == "Answer List":
                                # it is an element, it is a list, it is....
#                                print(rowNum, ": entering element loop for", options[select][0])
#                                mystuff = re.sub(r'(^[1-9]*)\. (*)',r'<catValu>\1</catValu><labl>\2</labl>',row[i])
#                                xmlData.write(mystuff + "\n" )
#                                print(rowNum, ": entering element loop for", options[select][0])
#                                xmlData.write('    <' + options[select][0] + '>![CDATA[' \
#                                    + row[i] + ']]</' + options[select][0] + '>' + "\n" )

                            # close the higher orders
                            if (len(options[select]) > levels[element] and  element in options[select] ) :
                                for j in range(levels[element],len(options[select])):
                                    #print("higher ",options[select][j])
                                    xmlData.write('    </' + options[select][j] + '>' + "\n" )
                            if ( len(options[select]) > levels[attribute] and attribute in options[select] ):
                                #print("Entering higher order ",len(options[select]))
                                for j in range(levels[attribute],len(options[select])):
                                    #print("higher ",options[select][j])
                                    xmlData.write('    </' + options[select][j] + '>' + "\n" )

        # end the var statement
        # first we find the attributes of var
        # for i in range(len(tags)):
        #     for select in options:
        #         print("select", select)
        #         print("tags[i]", tags[i])
        #         if tags[i] == select:
        #             print("options[select]",options[select])
#                    xmlData.write('    ' + '<' + options[i] + '>' \
#                          + row[i] + '</' + options[i][2] + '>' + "\n")
        xmlData.write('  </var>' + "\n")

    rowNum +=1

xmlData.write('</dataDscr>' + "\n")
xmlData.write('</codeBook>' + "\n")
xmlData.close()
