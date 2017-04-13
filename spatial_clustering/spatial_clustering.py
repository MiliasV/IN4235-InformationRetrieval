import numpy as np
import json
from pysal import W
import pysal
import pickle
from scipy.spatial.distance import euclidean
import plotly
from plotly.graph_objs import Scatter, Layout
from random import randint
file_path = "airbnb.geojson.filter"
#windows_file_path = "C:\Users\Raj\Dropbox\sem2\InformationRetrieval\project\\airbnb.geojson.filter"


class CollectionAirbnbPlaces:
    def __init__(self, file_name):
        self.filePath = file_name
        self.points = []
        self.get_relevant_data()
        self.floor_variable = np.ones((len(self.points), 1), float)
        self.floor = 4

    def plot_coordinates(self):
        coordinates = self.get_ids_coordinates()
        plotly.offline.plot({
            "data": [Scatter(x=[x[1][0] for x in coordinates], y=[x[1][1] for x in coordinates], mode='markers')],
            "layout": Layout(title="Coordinates"),
        })

    def plot_regions(self, maxp):
        regions = maxp.regions
        coordinates = self.get_map_ids_coordinates()

        data = []
        for region in regions:
            r, g, b = randint(0, 255), randint(0, 255), randint(0, 255)
            data.append(
                Scatter(
                    x=[coordinates[id][0] for id in region],
                    y=[coordinates[id][1] for id in region],
                    mode='markers',
                    marker=dict(
                        size=5,
                        color='rgba(%d, %d, %d, .8)' % (r, g,b)
                    )
                )
            )
        plotly.offline.plot({
            "data": data,
            "layout": Layout(title="Regions"),
        })

    def load_weights(self,k):
        with open('weights_const/weights_k_%d.pkl' % k, 'rb') as input:
            weight_vector = pickle.load(input)
        return weight_vector

    def load_maxp(self,k):
        with open('clusters/cluster_k_%d.pkl' % k, 'rb') as input:
            maxp = pickle.load(input)
        return maxp

    with open('clusters/cluster_k_3.pkl', 'rb') as input:
            regions = pickle.load(input)

    def save_pysal_max_p(self):
        for floor in range(4, 15):
            weights = self.load_weights(5)
            print("Weights loaded k = %d" % 5)

            pysal_weights = W(weights[0], weights[1])
            attributes = self.get_attributes()

            print("Started clustering floor = %d" % floor)
            result = pysal.region.Maxp(pysal_weights, attributes, floor, self.floor_variable, verbose=True, initial=20)
            print("Ended clustering floor = %d.\nStarted dumping " % floor)

            pickle.dump(result, open('clusters/cluster_floor_%d.pkl' % floor, 'wb'), pickle.HIGHEST_PROTOCOL)

    def get_relevant_data(self):
        # Read from file
        with open(self.filePath) as data_file:
            data = json.load(data_file)
        point_id = 0
        for point in data["features"]:
            coordinates = point["geometry"]["coordinates"]
            price_per_person = point["properties"]["price_per_person"]
            total_price = point["properties"]["total_price"]
            capacity = point["properties"]["capacity"]
            self.points.append(AirbnbPlace(coordinates, total_price, price_per_person, point_id, capacity))
            point_id += 1

    def get_attributes(self):
        return np.asarray(map(lambda x: [x.price_per_person], self.points))

    # Return [(id, coordinates), ... ]
    def get_ids_coordinates(self):
        return map(lambda x: (x.id, x.coordinates), self.points)

    # Return {id:coordinates, ...}
    def get_map_ids_coordinates(self):
        result = {}
        for point in self.points:
            result[point.id] = point.coordinates
        return result

    def save_weights_to_file(self):
        neighbors, weights = self.get_neighbors_weights(7)
        result_neighbors = []
        result_weights = []
        for i in range(3,8):
            result_neighbors.append({})
            result_weights.append({})
            for id in neighbors:
                result_neighbors[i-3][id] = neighbors[id][:i]
                result_weights[i-3][id] = weights[id][:i]

        weights_3 = (result_neighbors[0],result_weights[0])
        weights_4 = (result_neighbors[1],result_weights[1])
        weights_5 = (result_neighbors[2],result_weights[2])
        weights_6 = (result_neighbors[3],result_weights[3])
        weights_7 = (result_neighbors[4],result_weights[4])

        pickle.dump(weights_3, open('weights/weights_k_3.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(weights_4, open('weights/weights_k_4.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(weights_5, open('weights/weights_k_5.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(weights_6, open('weights/weights_k_6.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(weights_7, open('weights/weights_k_7.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)


    # Return pysal.weights.weights.W(neighbors, weigths)
    # neighbors = {id1:[neighbor_1, ... , neighbor_k], ... ]
    # weights = {id1:[weight_neighbor_1, ... , weight_neighbor_k], ... ]
    def get_neighbors_weights(self,k):
        all_points = self.get_ids_coordinates()
        neighbors = {}
        weights = {}
        for point in all_points:
            print (str(point[0]) + " of " + str(len(all_points)))
            distances = map(lambda other_point: (other_point[0], euclidean(point[1], other_point[1])), all_points)
            filtered_distances = filter(lambda other_point: other_point[0] != point[0], distances)
            sorted_distances = sorted(filtered_distances, key=lambda x: x[1])
            neighbors[point[0]] = map(lambda x: x[0], sorted_distances[0:k])
            weights[point[0]] = map(lambda x: x[1], sorted_distances[0:k])
        return neighbors, weights


class AirbnbPlace:
    def __init__(self, coordinates, total_price, price_per_person, point_id, capacity):
        self.coordinates = (float(coordinates[0]), float(coordinates[1]))
        self.total_price = float(total_price)
        self.price_per_person = float(price_per_person)
        self.id = int(point_id)
        self.capacity = int(capacity)
        self.neighbors_ids = []

    def __str__(self):
        return "Id: %d \n" \
               "\tCoordinates: (%f,%f) \n" \
               "\tTotal price: %f \n" \
               "\tPrice per person: %f \n" \
               "\tCapacity: %d" % \
               (self.id, self.coordinates[0], self.coordinates[1], self.total_price, self.price_per_person, self.capacity)
print(9)

CollectionAirbnbPlaces(file_path).save_pysal_max_p()
#a.plot_regions(a.load_maxp(4))
#print(solution.regions[0])
#np.random.seed(100)
#w = pysal.lat2W(10,10)
#z = np.random.random_sample((w.n,2))
#p = np.ones((w.n,1), float)
#floor = 3#
#solution = pysal.region.Maxp(w, z, floor, floor_variable=p, initial=100)
#
#min([len(region) for region in solution.regions])
#print w.weights
#print solution.regions[0]
