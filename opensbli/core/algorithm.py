
loopcounter = 0

from .block import SimulationBlock as SB
from .kernel import Kernel
from .latex import *
from .opensbliequations import *

class Loop(object):
    pass

class MainPrg(Loop):
    def __init__(self):
        self.components = []
        return
    def __str__(self):
        return "%s"%(self.__class__.__name__)
    def add_components(self, components):
        """ """
        if isinstance(components, list):
            self.components += components
        else:
            self.components += [components]
        return
    def write_latex(self, latex):
        latex.write_string("Starting of the main program\\\\\n")
        for c in self.components:
            c.write_latex(latex)
        latex.write_string("End of Main")
        return
    @property
    def opsc_code(self):
        code = []
        code += [self.opsc_start]
        for c in self.components:
            code += c.opsc_code
        code += [self.opsc_end]
        return code
    @property
    def opsc_start(self):
        return "Main Program Start \n {"
    @property
    def opsc_end(self):
        return "Main program end \n }"

class DoLoop(Loop):
    def __init__(self, iterator):
        self.loop = iterator
        self.components = []
        return
    def add_components(self, components):
        if isinstance(components, list):
            self.components += components
        else:
            self.components += [components]
        return
    def write_latex(self, latex):
        latex.write_string("Do loop %s,%s, %s\\\\\n"%(self.loop, self.loop.lower, self.loop.upper))
        for c in self.components:
            c.write_latex(latex)
        latex.write_string("Ending Do loop %s\\\\\n"%(self.loop))
        return
    @property
    def opsc_code(self):
        code = []
        code += [self.opsc_start]
        for c in self.components:
            code += c.opsc_code
        code += [self.opsc_end]
        return code
    @property
    def opsc_start(self):
        return "for(int %s=%s, %s<%s, %s++)\n{"%(self.loop, str(self.loop.lower), self.loop, str(self.loop.upper), self.loop)
    @property
    def opsc_end(self):
        return "}"
class DefDecs(object):
    def __init__(self):
        self.components = []
    def add_components(self, constants):
        if isinstance(components, list):
            self.components += components
        else:
            self.components += [components]

class Constants(DefDecs):
    def __init__(self):
        self.components = []
    def add_components(self, constants):
        if isinstance(components, list):
            self.components += components
        else:
            self.components += [components]

class Datasets(DefDecs):
    def __init__(self):
        self.components = []
    def add_components(self, constants):
        if isinstance(components, list):
            self.components += components
        else:
            self.components += [components]

class TraditionalAlgorithmRK(object):
    """ It is where the algorithm is generated, This is a seperate layer
    which gives user control to do any modifications for extra functionality that
    is to be performed like, doing some post processing for every time loop or
    sub rk loop
    """
    def __init__(self, blocks):
        if isinstance(blocks, SB):
            self.MultiBlock = False
            blocks = [blocks]
        else:
            self.MultiBlock = True
            raise NotImplementedError("")
        self.check_temporal_scheme(blocks)
        self.prg = MainPrg()
        self.spatial_solution(blocks)
        # Now try the algorithm generation
        return

    def add_definitions_declarations(self, blocks):
        defdecs = DefDecs()
        for b in blocks:
            defdecs.add_components()
            b.block_datasets

        return

    def spatial_solution(self, blocks):
        """ Add the spatial kernels to the temporal solution i.e temporalscheme.solution
        """
        print "Writing algorithm \n\n"
        fname = './algorithm.tex'
        latex = LatexWriter()
        latex.open('./algorithm.tex')
        metadata = {"title": "Algorithm for the equations", "author": "Jammy", "institution": ""}
        latex.write_header(metadata)
        all_kernels = []
        if self.MultiBlock:
            raise NotImplementedError("")
        else:
            b = blocks[0]
            bc_kernels = []
            inner_temporal_advance_kernels = []
            temporal_start = []
            temporal_end = []
            spatial_kernels = []
            for scheme in b.get_temporal_schemes:
                for key, value in scheme.solution.iteritems():
                    if isinstance(key, SimulationEquations):
                        print "Yes"
                        # Solution advancement kernels
                        temporal_start += scheme.solution[key].start_kernels
                        temporal_end += scheme.solution[key].end_kernels
                        inner_temporal_advance_kernels += scheme.solution[key].kernels
                        bc_kernels = key.boundary_kernels
                        spatial_kernels = key.all_spatial_kernels
                    else: # Add all other types of equations
                        print "No", type(key)
            sc = b.get_temporal_schemes[0]
            innerloop = sc.generate_inner_loop(bc_kernels + spatial_kernels + inner_temporal_advance_kernels)
            temporal_iteration = Idx("iter", Symbol('niter', integer =True))
            tloop = DoLoop(temporal_iteration)
            tloop.add_components(temporal_start)
            tloop.add_components(innerloop)
            tloop.add_components(temporal_end)
            #tloop.write_latex(latex)
            # Process the initial conditions and Diagnostics if any here
            self.prg.add_components(tloop)
            self.prg.write_latex(latex)
        latex.write_footer()
        latex.close()
        return

    def check_temporal_scheme(self, blocks):
        """
        If Multi-block this checks the temporal scheme is the same for all the blocks
        """
        if self.MultiBlock:
            raise NotImplementedError("")
        else:
            if len(blocks[0].get_temporal_schemes) > 1:
                raise ValueError("More than one temporal scheme for a block")
        return

"""
Best implementation of this would be
What we will have are
a. Equations evaluated in the time loop (order)
b. Equations evaluated outside the time loop (Metrics evaluations, Diagnostics)
c. Equations evaluated both inside and outside the time loop (Statistics, Diagnostics etc)

Algorithm is a doubly linked list with the names as strings
(For kernels it would be blocknumber+kernel_no)
For BC's it would be
next, previous
insert
remove

For each of the equation classes we should have the following,
a. solution_kernels (Simulation equations) (CR+Spatial)
b. Temporal_soultion_kernels (Substage true or false for each kernel)
c.

Algorithm:
a. tloop
b. ts.start
c. Rkloop
d. SimulationEquationsBC
e. SimulationEquationsSpatial, other
f. Time advancement
g. RKend
h. Diagnostics,
i. Tend
"""
