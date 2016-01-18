#!/usr/bin/env python
import sys
import datetime
import os
from re import *
import time
import argparse

# Symbolic-related functions
from sympy import *
from sympy.parsing.sympy_parser import *
init_printing(use_latex=True)

# Import local utility functions
from einstein_expansion import *
from algorithm import *
from utils import *

LATEX_FILE = "equations.tex"

def expand_equations(equations_file):
   """ Perform an expansion of the equations, provided by the user, and written in Einstein notation.
   
   :arg str equations_file: The path to the equations file.
   """
   
   # Remove leading and trailing white spaces and empty lines
   with open(equations_file) as f:
      read_file = [line for line in f.read().splitlines() if line]
   comm_lineno = [] # Line numbers of each (Python) comment line, which we want to ignore

   # Get all the comments in the file
   for ind,line in enumerate(read_file):
     if line[0] == '#':
       comm_lineno.append(ind)

   inp = inputs() # Define the inputs
   
   # Read inputs from the file
   inp.eq = read_file[comm_lineno[0]+1:comm_lineno[1]]
   inp.substi = read_file[comm_lineno[1]+1:comm_lineno[2]]
   inp.ndim = int(read_file[comm_lineno[2]+1])
   inp.const = read_file[comm_lineno[3]+1:comm_lineno[4]]
   inp.coord = read_file[comm_lineno[4]+1:comm_lineno[5]]
   inp.metric = read_file[comm_lineno[5]+1:comm_lineno[6]]
   inp.formula = read_file[comm_lineno[6]+1:comm_lineno[7]]
   # Find the tensor indices in the equations

   # Expand the equations
   start = time.time()
   eqs = []
   for eq in inp.eq:
     eqs.append(equations(eq, inp))
   forms = []
   for form in inp.formula:
     forms.append(equations(form, inp))
   #for eq in eqs:
     #pprint(eq.expandedeq)
   end = time.time()
   print ('The time taken for tensor expansion of equations in %d Dimensions  is %s'%(inp.ndim,end - start))
   
   # Prepare equations for algorithm
   read_file = [line for line in open("algorithm", "r").read().splitlines() if line]
   alg = read_alg(read_file)
   start = time.time()
   fineq = prepareeq(eqs,forms,alg)
   end = time.time()
   print ('The time taken for tensor expansion of equations in %d Dimensions  is %s'%(inp.ndim,end - start))

   # Output equations in LaTeX format.
   with open(LATEX_FILE,'w') as latex_file:
      temp = []
      for eq in eqs:
        temp = temp + [eq.parsed]
      inp = ['Algorithm', 'Satya P Jammy','University of Southampton']
      header , end = latex_article_header(inp)
      latex_file.write(header)
      temp = []
      for eq in eqs:
        temp = temp + [eq.expandedeq]
      temp = flatten(temp)
      write_latex(latex_file, temp)
      latex_file.write(end)
   
   return

if(__name__ == "__main__"):
   # Parse the command line arguments provided by the user
   parser = argparse.ArgumentParser(prog="codegen", description="")
   parser.add_argument("equations_file", help="The path to the file containing the equations.", action="store", type=str)
   args = parser.parse_args()
   
   expand_equations(args.equations_file)
   

