from math import pow

def distance_between(coord1, coord2):
	return pow(coord1[0]-coord2[0],2) + pow(coord1[1]-coord2[1],2)
