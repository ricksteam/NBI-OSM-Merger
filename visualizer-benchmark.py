import time
from statistics import mean

start_time = time.time_ns()

from visualiser_ox import VisualizerOX as vox

after_ox_import = time.time_ns()

from visualiser import Visualizer as v

after_non_import = time.time_ns()

# It will likely be important to see specific points compared, rather than an average.
points = [(41.3209, -96.0449),(41.3236, -96.0449),(41.3154, -96.0524),\
            (41.3293, -96.0482),(41.311 , -96.0475),(40.0249, -95.3837),\
            (41.595, -97.6183), (40.6641, -99.6057), (42.57547, -99.69451), (40.4942, -96.5962),]


# ======= OSMNX Benchmark =========
osmnx_times = []
pre_osmnx_run = time.time_ns()
for point in points:
    osmnx_point_s = time.time_ns()
    vox.analyze_point(point, show=False, save=True)
    osmnx_point_e = time.time_ns()
    osmnx_times.append(osmnx_point_e - osmnx_point_s)

post_osmnx_run = time.time_ns()

# ======= Non-NX Benchmark =========
nonx_times = []
pre_nonx_run = time.time_ns()
for point in points:
    nonx_point_s = time.time_ns()
    v.analyze_point(point, show=False, save=True)
    nonx_point_e = time.time_ns()
    nonx_times.append(nonx_point_e - nonx_point_s)

post_nonx_run = time.time_ns()

# ======= Benchmark Analysis =========
print(f'Import OX Visualizer time: \t{(after_ox_import - start_time)/(10**9)}')
print(f'Import No-OX Visualizer time: \t{(after_non_import - after_ox_import)/(10**9)}')
print()
print(f'OX Visualizer total time: \t{(post_osmnx_run - pre_osmnx_run)/(10**9)}')
print(f'OX Visualizer times: \t\t{[t/(10**9) for t in osmnx_times]}')
print(f'Average OX Visualizer time: \t{(mean(osmnx_times))/(10**9)}')
print()
print(f'No-OX Visualizer total time: \t{(post_nonx_run - pre_nonx_run)/(10**9)}')
print(f'No-OX Visualizer times: \t{[t/(10**9) for t in nonx_times]}')
print(f'Average No-OX Visualizer time: \t{(mean(nonx_times))/(10**9)}')
