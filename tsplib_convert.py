import os
import sys

class Convert:
	def __init__(self, citySet:dict, name:str, dimension:str, edge_type:str="EUC_2D", prob_type:str="TSP"):
		self.citySet = citySet
		self.name, self.dim, self.edge_type, self.type = name, dim, edge_type, prob_type
		self.structure()

	def structure(self):
		self.struct = ""
		self.struct += f"NAME: {self.name}"
		self.struct += f"TYPE: {self.type}"
		self.struct += f"DIMENSION: {self.dim}"
		self.struct += f"EDGE_WEIGHT_TYPE: {self.edge_type}"
		self.struct += f"NODE_COORD_SECTION: \n"
		self.struct += self.citySet
		
		print(self.struct)
		sys.stdout.flush()

	def set_params(self, citySet:dict, name:str, dimension:str):
		self.citySet = citySet
		self.name, self.dim, self.edge_type, self.type = name, dim, edge_type, prob_type


	def __call__(self):
		dir_head = os.path.abspath(os.path.dirname(__file__))
		with open(dir_head + name + '.txt', 'w') as file:
			for i in self.struct:
			file.write()