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

	# form = [[0,1],
	# 	 	[1,1],
	# 		[1,1],
	# 		[0,0]]
	# t = Tile.from_form(form)
	# print(t.graph_neighborslist())
	# j = t.json()
	# print(j)
	# print(t)
	# print(t.get_tlcoords())
	# print(Tile.from_json(j))
	# sys.exit(0)

	Tile.default_x_dir = "down"
	Tile.default_y_dir = "right"

	X = 7
	Y = 15
	TILE_LIMIT = 2
	AREA_LIMIT = float('inf')
	FILL = True
	WEIGHTED = False
	LESS1X1 = True
	COLO = 7

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

	setile3=Tile.set_for_pavage(forms)
	# setile3=Tile.rectangle_range(3)
	# for t in setile3:
	# 	t.fancy_display()
	# 	print("")
	# print("-------------------------")
	# sys.exit(0)
	# setile.append(Tile.from_form(form))



	# jsondict = {'size': {'xsize': 4, 'ysize': 4}, 'tiles': [{'pos': (1, 2), 'indexes': [[0, 0], [1, -1], [1, 0], [1, 1], [2, 0]]}, {'pos': (0, 3), 'indexes': [[0, 0], [1, 0]]}, {'pos': (3, 0), 'indexes': [[0, 0], [0, 1]]}, {'pos': (0, 1), 'indexes': [[1, 0], [1, -1], [0, 0]]}, {'pos': (3, 3), 'indexes': [[0, 0]]}, {'pos': (0, 0), 'indexes': [[0, 0]]}, {'pos': (0, 2), 'indexes': [[0, 0]]}, {'pos': (2, 0), 'indexes': [[0, 0]]}]}
	# tiles = Pavage.from_json(jsondict)

	tiles = Pavage(X,Y,setile3,fill=FILL,weighted=WEIGHTED,less1x1=LESS1X1)
	tiles.fancy_display(colors=COLO)
	# print(tiles.json())
	# print("")
	# count = tiles.count()
	# for index in count:
	# 	print(str(index) + "\t: " + str(count[index]),end="\n\n")

	colo = tiles.get_coloration(COLO)
	# grigrid = tiles.get_numbered_grid()
	# for l in grigrid:
	# 	for c in l:
	# 		print(colo[c],end="")
	# 	print("")
	# print("")

	isright = True
	graph = tiles.get_graph_neighborslist()
	for n in range(len(graph)):
		for v in list(graph[n]):
			isright &= colo[n] != colo[v]
	print(isright)


	# for i in range(len(tiles.tiles)):
	# 	print(str(tiles.tiles[i]) + "\n\t -> " + str(colo[i]))

	# print(Pavage.count(tiles))# for t in tiles:
	# for t in tiles:
	# 	print(t)