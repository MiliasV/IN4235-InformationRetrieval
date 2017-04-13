import clusterpy
    c = clusterpy.importArcData("input/voronoi_40percent")
    c.cluster('maxpTabu', ['price_per_', 'capacity'], threshold=150, std=1)
    c.exportArcData("output/maxp_capacity_150")
