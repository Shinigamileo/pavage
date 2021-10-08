from pavage import *
import json
import sys

#####################################
#                                   #
#             ATTENTION             #
#           ZONE DE TESTS           #
#                                   #
#####################################


if __name__=="__main__":

	form = [[0,1,1,1],
		 	[1,1,0,1],
			[1,0,0,1],
			[0,0,1,1,1]]
	t = Tile.from_form(form)
	print(t.graph_neighborslist())
	j = t.json()
	print(j)
	print(t)
	print(Tile.from_json(j))
	sys.exit(0)

	X = 20
	Y = 30
	TILE_LIMIT = 2
	AREA_LIMIT = float('inf')
	FILL = False
	WEIGHTED = True
	LESS1X1 = True

	forms = [([[0,1,1,1],
		 	   [1,1,0,1],
			   [1,0,0,1],
			   [0,0,1,1,1]],True),
			  ([[1]],True),
			  ([[1,1,1],
			  	[1,0,0]],True),
			  ([[1,1],
			  	[1,0]],True),
			  ([[1,1]],True),
			  ([[0,1,0],
			  	[1,1,1],
			  	[0,1,0]],True),
			  ([[1,0,1],
			  	[1,1,1],
			  	[1,0,1]],True)
			]
	# t = Tile.from_form(form)
	# print(t)
	# o = t.output()
	# print(o)
	# t1 = Tile.from_form(form)
	# t2 = t1.clone()
	# for i in range(4):
	# 	f = t2.get_form()
	# 	for l in f:
	# 		print(l)
	# 	print(hash(t1)==hash(t2))
	# 	print(",")
	# 	t2.rotate(90)
	# sys.exit(0)

	# s = set()

	# for form,b in forms:
	# 	t1 = Tile.from_form(form)
	# 	t2 = t1.clone()
	# 	s.add(t1)
	# 	for i in range(4):
	# 		f = t2.get_form()
	# 		for l in f:
	# 			print(l)
	# 		print(hash(t1)==hash(t2))
	# 		print(t2 in s)
	# 		print(",")
	# 		# s |= set([t2])
	# 		t2.rotate(90)
	# 		print(s)
	# sys.exit(0)		

	# print(Tile.rectangle_range(TILE_LIMIT,AREA_LIMIT))

	# setile = Tile.rectangle_range(TILE_LIMIT,AREA_LIMIT)
	# setile2 = [(t.get_form(),True) for t in setile]
	# setile2.append((form,True))
	# for t in setile2:
	# 	f = t[0]
	# 	for l in f:
	# 		print(l)
	# 	print(",")
	# print("-------------------------")

	# setile3=Tile.set_for_pavage(forms)
	setile3=Tile.rectangle_range(3)
	# for t in setile3:
	# 	f = t.get_form()
	# 	for l in f:
	# 		print(l)
	# 	print(",")
	# print("-------------------------")
	# sys.exit(0)
	# setile.append(Tile.from_form(form))

	tiles = Pavage(X,Y,setile3,\
				   fill=FILL,weighted=WEIGHTED,less1x1=LESS1X1)
	tiles.fancy_display()
	count = tiles.count()
	for index in count:
		print(str(index) + "\t: " + str(count[index]),end="\n\n")

	# print(Pavage.count(tiles))# for t in tiles:
	# for t in tiles:
	# 	print(t)