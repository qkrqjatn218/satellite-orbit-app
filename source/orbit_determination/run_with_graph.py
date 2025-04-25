from pycallgraph2 import PyCallGraph
from pycallgraph2.output import GraphvizOutput
from orbit_determination import propagation

graphviz = GraphvizOutput(output_file='callgraph.png')

with PyCallGraph(output=graphviz):
    propagation._dpper()  # 또는 추적하고 싶은 함수 호출
