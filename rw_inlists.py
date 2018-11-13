#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
code to read and write MESA inlist files
"""

import copy

#class for storing mesa inlists
class mesa_inlist:
    def __init__(self, lines=[],inlist_dict=dict(),fname=''):
        self.lines=lines
        self.dict=inlist_dict
        self.fname=fname
    
    def read(self, f_in=None):
        f_in = f_in or self.fname
        if f_in=='':
            print("No input file name given")
            return
            
        self.fname=f_in
        ll, outdict = read_inlist(f_in)
        self.lines = ll
        self.dict = outdict
    
    def write(self, f_out=None):
        f_out = f_out or self.fname
        if f_out=='':
            print("No output file name given")
            return
        self.fname =f_out
        write_inlist(self.lines, self.dict, f_out)
        

#function to read MESA inlist file
#inputs:
#   f_in_name: inlist file name
#outputs:
#   linelist: list of lists of str, lines of file broken into relevant parts
#   inlist_dict: dictionary of inlist keywords and values
def read_inlist(f_in_name):
    f_in = open(f_in_name,"r")

    linelist=[] #tuple for storing different parts of a line
    inlist_dict=dict()
    for line in f_in:
        l=line.strip() #remove '\n'
        content=''
        comment=''
    
        if l.startswith('&'):
            content,comment = l.split('&',1)
            comment= "&" + comment
        elif l.startswith('/'):
            content,comment = l.split('/',1)
            comment="/" + comment
        elif '!' in l: #do this last because can have lines like "&pgstar !plotting" and want all to be comment
            content,comment = l.split('!',1)
            comment="!" + comment
        else:
            content=l
        #end if
        keyw=""
        val=""
        if len(content)>0 and "=" in content:
            keyw,val= content.split('=',1)
            keyw=keyw.strip()
            val=val.strip()
    
        if len(keyw)>0 and len(val)>0:
            inlist_dict.update({keyw:val})
        
        linelist.append([keyw,val,comment])
    #end for
    f_in.close()
    return linelist, inlist_dict
#end fcn

#function to write MESA inlist to file
#updates content of out of date linelist
#inputs:
#   linelist: list of lists of str, lines of file broken into relevant parts
#   inlist_dict: dictionary of inlist keywords and values
#   f_out_name: name of output file
def write_inlist(linelist, inlist_dict, f_out_name):
    f_out = open(f_out_name,'w')
    llist=copy.deepcopy(linelist)

    #update tuple with current dict values
    for key in inlist_dict:
        for j in range(0,len(llist)):
            if llist[j][0]==key:
                llist[j][1]=inlist_dict[key]

    for i in range(0,len(llist)):
        if len(llist[i][0])>0:
            outstr= llist[i][0] +" = "+ llist[i][1]+" " +llist[i][2] +"\n"
        else:
            outstr= llist[i][0] + llist[i][1] + llist[i][2]+"\n"
        
        if len(llist[i][0])==0 and len(llist[i][1])!=0:
            print("This should never happen!")
    
        f_out.write(outstr)
    
    f_out.close()
    return;
