"""
This library is used to analyst exiting code performance
"""
__all__= []
"""
# test line memory usage 
import tracemalloc 

tracemalloc.start()
from baselibs import localtest_funcs

localtest_funcs()
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[10:20]:
	print(stat)
"""

# test time consume
import timeit
setup = "from baselibs import localteset_funcs"
print(timeit.timeit("localtest_funcs",setup=setup))