#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 16:14:04 2018

Test using script command line arguments 
@author: nxt5109
"""
import sys
args=sys.argv #all strings

print("Name of file:", args[0])
print("First arg:", args[1])
print("Second arg:",args[2])
#print("Type of first:", type(args[1]))

num1=int(args[1])
num2=int(args[2])

print("arg1 x arg2 =",num1*num2)