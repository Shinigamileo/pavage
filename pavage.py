"""
 * -----------------------------------------------------------------------------*
 * "THE BEER-WARE LICENSE" (Revision 42):                                       *
 * Bloody Loki wrote this file. As long as you retain this notice you           *
 * can do whatever you want with this stuff. If we meet some day, and you think *
 * this stuff is worth it, you can buy me a beer in return                      *
 *                                                      Léo Michel Claude Barré *
 * -----------------------------------------------------------------------------*
"""

"""
TODO :
- Tile.is_connected()
- Pavage.coloration()
"""

import random as rd
from functools import reduce
import kcolor as kc



class Tile: #----------------------------------------------------------------------------
	"""
	A tile fo some form (given by relative indexes) that can be used for a 'pavage'.
	(x,y) are the coordinates of its top-left corner.
	"""
	def __init__(self, indexes,\
				 pos=(0,0)):
		self.x = pos[0]
		self.y = pos[1]
		self._new_indexes(indexes)

	def _new_indexes(self,indexes):
		self._x_min = 0
		self._x_max = 0
		self._y_min = 0
		self._y_max = 0
		self._indexes = []
		for i in indexes:
			self._indexes.append(tuple(i))
			self._x_min = min(self._x_min,i[0])
			self._x_max = max(self._x_max,i[0])
			self._y_min = min(self._y_min,i[1])
			self._y_max = max(self._y_max,i[1])


	###########################
	#                         #
	# BUILT-IN AND PROPERTIES #
	#                         #
	###########################

	@property								#
	def pos(self):							#
		return (self.x,self.y)				#
	@pos.setter								#
	def pos(self,value):					#   pos = (x,y)
		self.x=value[0]						#
		self.y=value[1]						#   indexes : copy of _indexes
	@property								#
	def indexes(self):						#
		return self._indexes.copy()			#
	@property								#   tlc (top-left corner)
	def tlc(self):							#   brc (bottom-right corner)
		return (self._x_min,self._y_min)	#       their relative position
	@property								#       to the (0,0) point
	def brc(self):							#
		return (self._x_max,self._y_max)	#   height / width of the Tile
	@property								#
	def height(self):						#
		return self._x_max - self._x_min +1	#   area : number of cells covered
	@property								#          by the Tile
	def width(self):						#
		return self._y_max - self._y_min +1	#
	@property								#
	def area(self):							#
		return len(self._indexes)			#


	def __iter__(self):            # used to iter the indexes of the tile
		return Tile.Iterator(self) # for i in tile -> for i in tile._indexes
	class Iterator:
		def __init__(self,t):
			self._t = t
			self._index = 0
		def __next__(self):
			try:
				res = self._t._indexes[self._index]
				self._index+=1
				return res
			except (IndexError):
				raise StopIteration


	def __str__(self): # ex: {0,1}(1,2)
		return "{"+str(self.x)+";"+str(self.y)+"}"+str(self._indexes)


	def __eq__(self,t):
		return self.x == t.x \
		     and self.y == t.y \
		     and set(self._indexes) == set(t._indexes)


	def __hash__(self):
		return hash((self.x,self.y) + tuple(set(self._indexes)))


	##################
	#                #
	#     OTHERS     #
	#                #
	##################

	def copy(self):
		return Tile(self._indexes, (self.x, self.y))


	def json(self):
		return {"pos"    : (self.x,self.y),
		        "indexes": [list(i) for i in self._indexes]
		       }


	def graph_neighborslist(self):
		"""
		Give the associated graph of the object
		under the form of a neighbors'list
		"""
		neighlist = [set() for t in self._indexes]
		dict_indexes = {self._indexes[i]:i for i in range(len(self._indexes))}
		for ci,cj in self._indexes:
			for di,dj in [(0,1),(1,0),(0,-1),(-1,0)]:
				if (ci+di,cj+dj) in dict_indexes:
					neighlist[dict_indexes[(ci,cj)]].add(dict_indexes[(ci+di,cj+dj)])
		return neighlist


	def is_eligible(self, grid, pos):
		"""
		Check if the Tile can be put in a more or less filled grid at pos pos
		Regards, Cap'n Obvious
		"""
		x,y = pos
		return (self._x_min+x>=0) and (self._x_max+x<h) \
		   and (self._y_min+y>=0) and (self._y_max+y<w) \
		   and reduce(lambda a,b : a&grid[x+b[0]][y+b[1]],self._indexes,True)


	def rd_weight(self,weighted=False):
		"""
		Give the wieght of the Tile.
		Can be used to make some Tiles more valuable than others.
		"""
		return 1-weighted\
				+ weighted*(self.area*self.area*self.area)


	def is_connected(self): # TODO
		"""
		Returns True if the Tile is connected, meaning that every cell
		of the tile is connected to the others.
		┌─┐                ┌─┐              ┌─┐
		│ └─┐ : True   ;   └─┘ : True   ;   └─┼─┐ : False
		└───┘                                 └─┘
		"""
		neighlist = self.graph_neighborslist()
		group = set()
		return None


	def rotate(self,a):
		"""
		Rotate the Tile of a°
		 a≡0°    a≡90°  a≡180°  a≡270° (mod 360)
		┌─┐     ┌───┐   ┌───┐     ┌─┐
		│ └─┐ ; │ ┌─┘ ; └─┐ │ ; ┌─┘ │
		└───┘   └─┘       └─┘   └───┘
		(Note : only multiples of )
		"""
		a = (a//90)%4 # a ≡   0 -> 0 -> 00
		b0 = a&1      #      90 -> 1 -> 01
		b1 = (a>>1)&1 #     180 -> 2 -> 10
		b0x1 = b0^b1  #     270 -> 3 -> 11
		# looking for new (0,0)
		new_x0 = (1-b0)*((1-b1)*self._x_min + b1*self._x_max)\
				+ b0*((1-b1)*self._x_min + b1*self._x_max)
		new_y0 = b0*((1-b1)*self._y_min + b1*self._y_max)\
				+ (1-b0)*((1-b1)*self._y_max + b1*self._y_min)
		for i,j in self._indexes:
			new_x0 = (((1-b0)|(new_y0!=j))*new_x0
					+ (b0&(new_y0==j))*((1-b1)*max(new_x0,i)
										+b1*min(new_x0,i)))
			new_y0 = ((b0|(new_x0!=i))*new_y0
					+ ((1-b0)&(new_x0==i))*(b1*max(new_y0,j)
										    +(1-b1)*min(new_y0,j)))
		# placing the indexes relatively to the new (0,0)
		new_indexes = []
		for i,j in self._indexes:
			relative_x = i - new_x0 # relative position of the cell (i,j)
			relative_y = j - new_y0 # from the new (0,0), prior to rotation
			new_x = (2*(1-b1  )-1)*((1-b0)*relative_x + b0*relative_y)# 00: x, y 01: y,-x
			new_y = (2*(1-b0x1)-1)*((1-b0)*relative_y + b0*relative_x)# 10:-x,-y 11:-y, x
			new_indexes.append((new_x,new_y))
		self._new_indexes(new_indexes)
		return self


	def get_form(self):
		"""
		Code the Tile's form as a boolean grid
		  ┌─┐ ┏                ┓   [[0,1],
		┌─┘ │ ┃ (0,0) , (1,-1) ┃ ∙  [1,1],
		│ ┌─┘ ┃ (1,0) , (2,-1) ┃ ∙  [1,0]]
		└─┘   ┗                ┛
		"""
		grid = [[0 for j in range(self.width)] for i in range(self.height)]
		for i,j in self._indexes:
			grid[i-self._x_min][j-self._y_min]=1
		return grid


	def get_key(self):
		"""
		Create a key associated to the type of tile.
		Used for dictionnaries.
		"""
		form = self.get_form()
		key = ""
		for l in form:
			for c in l:
				key += str(c)
			key += "\n"
		return key[:-1]


	####################################
	#                                  #
	#    SPECIAL TILE(S) GENERATORS    #
	#                                  #
	####################################

	def rectangle(h,w,pos=(0,0)):
		"""Generate a rectangular h*w Tile"""
		return Tile([(i,j) for i in range(h) for j in range(w)],pos)


	def square(c,pos=(0,0)):
		"""Generate a square c*c Tile"""
		return Tile.rectangle(c,c,pos)


	def from_form(grid,pos=(0,0)):
		"""
		Use a boolean grid to generate a Tile
		[[0,0],     ┌─┐ ┏                ┓
		 [0,1], ∙ ┌─┘ │ ┃ (0,0) , (1,-1) ┃
		 [1,1], ∙ │ ┌─┘ ┃ (1,0) , (2,-1) ┃
		 [1]  ]   └─┘   ┗                ┛
		"""
		# delete first useless lines only composed of 0s
		while(not sum(grid[0])):
			grid = grid[1:]
		# deducing first point (0,0) (rule : always the left-most point on top)
		j0 = 0
		while(not grid[0][j0]):
			j0+=1
		# creating all indexes
		indexes = []
		for i in range(len(grid)):
			for j in range(len(grid[i])):
				indexes += grid[i][j]*[(i,j-j0)]
		return Tile(indexes,pos)


	def from_json(jsondict):
		return Tile([tuple(i) for i in jsondict["indexes"]],jsondict["pos"])


	def rectangle_range(b,area_max=float('inf')):
		"""
		Generate a list of all rectangular Tiles
		which sizes are ≤ b
		  and area is ≤ area_max
		"""
		return [Tile.rectangle(i,j) for i in range(1,b+1) for j in range(1,b+1)
				if i*j < area_max]


	def square_range(b):
		"""
		Generate a list of all square Tiles
		which size is ≤ b
		"""
		return Tile.rectangle_range(b)


	def set_for_pavage(formnrot):
		"""
		Generate a list of Tiles given of list of couples with :
		- their form (in a boolean grid)
		- if they can be rotated
		This fuction is often used to generate a list for a Pavage object
		"""
		s = set()
		for form,rotate in formnrot:
			t0 = Tile.from_form(form)
			s.add(t0)
			for a in range(90,360*rotate,90):
				s.add(t0.copy().rotate(a))
		return list(s)

# {\Tile}--------------------------------------------------------------------------------




class Pavage: #--------------------------------------------------------------------------
	"""
	The tiling of a h*w grid. Its tiles are stocked in tiles
	  w──────>                     ┏          {0;0}              ┓
	 h┌─┬─┬─┬─┐        ╔═╦═══╦═╗   ┃  {1;1}    ┌─┐               ┃
	 │├─┼─┼─┼─┤  ───╲  ║ ╠═══╩═╣ ∙ ┃ ┌─────┐   │ │  {0;2}  {0;1} ┃
	 ∨├─┼─┼─┼─┤  ───╱  ║ ║     ║ ∙ ┃ │     │ , │ │ , ┌─┐ , ┌───┐ ┃
	  └─┴─┴─┴─┘        ╚═╩═════╝   ┗ └─────┘   └─┘   └─┘   └───┘ ┛
	"""
	def __init__(self, h, w, tile_set,
			   	fill     = False , # if wanna always put the biggest Tile possible
			   	weighted = False , # if the bigger the Tile, the better the chances
			   	less1x1  = False,  # if try to minimise number of 1x1
			   	dotiling = True,   # if the init DOES require a tiling
			   	):

		self._h = h ; self._w = w
		self._tiles = [] # the list of tiles that will be returned
		# if we don't need a tiling (example : if this is a copy)
		if not dotiling:
			self._tiles = [t.copy() for t in tile_set]
			return
		# else... prepare for tiling !!!
		unoccupied_cells = set(range(h*w))  # set of all empty cells
		grid = [[True for j in range(w)] for i in range(h)] # True : empty cell
		not1x1count = less1x1 * h * w

		while(unoccupied_cells):
			chosable_tiles = [] # where we'll stack the putable tiles
			cell_x = None ; cell_y = None # coordinates of the chosen cell

			while not chosable_tiles:
				######################################
				# randomly choose an unoccupied cell #
				######################################
				cell = rd.choice(list(unoccupied_cells))
				cell_x = cell//w
				cell_y = cell%w 

				####################################
				# generate a list of putable tiles #
				####################################
				size_max = 0        # the size of the greatest putable tile
				for t in tile_set:
					eligible = (t.tlc[0]+cell_x>=0) and (t.brc[0]+cell_x<h) \
						   and (t.tlc[1]+cell_y>=0) and (t.brc[1]+cell_y<w) \
						   and reduce(lambda a,b : a&grid[cell_x+b[0]][cell_y+b[1]],t,1)
					tile_weight = eligible*t.rd_weight(weighted)

					# the old tiles we already have in our list of chosable.
					# we don't keep them only if :
					# - the 'fill' option is checked
					#   & the new tile is greater than those before
					#   & the new tile can be put
					# or
					# - the 'less1x1' option is checked
					#   & the old tiles are of area 1 (= are 1x1 squares)
					#   & the new tile can be put
					old_tiles = (    (1-(fill and (t.area>size_max) and eligible))
					             and (1-(less1x1 and (size_max==1) and eligible))
					            )*chosable_tiles
					# the new tile we gathered for our list of chosable.
					# we don't add it only if :
					# - the 'fill' option is checked
					#   & the new tile is smaller than those before
					# or
					# - the 'less1x1' option is checked and not1x1count is greater than 0
					#   & the new tile is of area 1 (= is a 1x1 square)
					new_tiles = (    (1-(fill and (t.area<size_max)))
						         and (1-(bool(not1x1count) and (t.area==1)))
					            )*[t for k in range(tile_weight)]

					chosable_tiles = old_tiles + new_tiles

					size_max = max(size_max,t.area*eligible)
				not1x1count = max( not1x1count - (not chosable_tiles), 0)
			#########################################################
			# randomly choose a type of tile in the generated list, #
			# fill the grid and delete the now occupied cell        #
			#########################################################
			tile = rd.choice(chosable_tiles).copy()
			tile.pos = (cell_x , cell_y)
			self._tiles.append(tile)
			for i in tile:
				grid[cell_x+i[0]][cell_y+i[1]] = False
				unoccupied_cells.remove((cell_x+i[0])*w+(cell_y+i[1]))


	###########################
	#                         #
	# BUILT-IN AND PROPERTIES #
	#                         #
	###########################

	@property				#
	def h(self):			#   Protected variables 'get'
		return self._h		#
	@property				#
	def height(self):		#   _h (height of the tiled grid):
		return self.h		#      h , height
	@property				#
	def w(self):			#   _w (width of the tiled grid):
		return self._w		#      w , width
	@property				#
	def width(self):		#   _tiles (list of tiles of tiling):
		return self.w		#      tiles
	@property				#
	def tiles(self):		#
		return [t.copy() for t in self._tiles]
		

	def __iter__(self):
		"""
		used to iter tiles in the 'pavage'
		for t in 'pavage' -> for t in 'pavage'._tiles
		"""
		return Pavage.Iterator(self)
	class Iterator:
		def __init__(self,p):
			self._p = p
			self._index = 0
		def __next__(self):
			try:
				res = self._p._tiles[self._index]
				self._index+=1
				return res
			except (IndexError):
				raise StopIteration


	##################
	#                #
	#     OTHERS     #
	#                #
	##################

	def copy(self):
		return Pavage(self._h, self._w, self._tiles, dotiling = False)


	def json(self):
		output = {}
		output["size"] = {"height" : self._h,
						  "width"  : self._w
						 }
		output["tiles"]=[]
		for t in self._tiles:
			output["tiles"].append(t.json())
		return output


	def graph_neighborslist(self):
		"""
		Give the associated graph of the object
		under the form of a neighbors'list
		"""
		grid = self.get_numbered_grid()
		neighlist = [set() for i in range(len(self._tiles))]
		for i in range(self._h-1):
			for j in range(self._w-1):
				neighlist[grid[ i ][ j ]].add(grid[i+1][ j ])
				neighlist[grid[i+1][ j ]].add(grid[ i ][ j ])
				neighlist[grid[ i ][ j ]].add(grid[ i ][j+1])
				neighlist[grid[ i ][j+1]].add(grid[ i ][ j ])
		for i in range(len(neighlist)):
			neighlist[i].remove(i)
		return neighlist


	def count(self,roundto=2):
		"""
		count the number of each form of Tiles in a pavage
		and what portion they represent of all tile / of the total area
		╔═════╦═╗   ⎧  T  : ( 5 , 100.0% , 100.0% ) ⎫
		║     ╠═╣ ∙ ⎭ 1x3 : ( 1 ,  20.0% ,  25.0% ) ⎩
		╠═╦═══╩═╣ ∙ ⎫ 2x3 : ( 1 ,  20.0% ,  50.0% ) ⎧
		╚═╩═════╝   ⎩ 1x1 : ( 3 ,  60.0% ,  25.0% ) ⎭
		"""
		l = len(self._tiles)
		tmp_count = {"T":[l,float(100),float(100)]}
		for t in self._tiles:
			key = t.get_key()
			if key not in tmp_count:
				tmp_count[key] = [0,0,0]
			tmp_count[key][0] += 1
			tmp_count[key][1]  = round(tmp_count[key][0]/l*100,
				                        roundto)
			tmp_count[key][2]  = round(tmp_count[key][0]*t.area/(self._h*self._w)*100,
				                        roundto)

		count = {k:(tmp_count[k][0],
			        tmp_count[k][1],
			        tmp_count[k][2]) for k in tmp_count}
		return count


	def get_coloration(self,color_nb=4):
		"""
		Give a coloration of the pavage with color_nb colors
		such that two neighbors tiles can't be the same color.
		The default number of colors is 4 since every tiling
		with connected tiles can be colored with at least 4 colors
		If color_nb < 4, of if some tiles aren't connected,
		there can be no viable solution.
		"""
		# COMING SOON
		return None


	def fancy_display(self):
		"""
		Print the pavage in a fancy way. It'll look just like the drawings
		I made with the Box Unicode characters. They're sooooo pretty <3
		"""
		grid = self.get_numbered_grid()
		print("╔",end="")
		for j in range(self._w):
			print("══",end="")
			if j == self._w-1:
				print("╗",end="")
			elif grid[0][j] != grid[0][j+1]:
				print("╦",end='')
			else:
				print("═",end="")
		print("")
		for i in range(self._h):
			print("║",end="")
			for j in range(self._w):
				print("  ",end="")
				if j == self._w-1 or grid[i][j] != grid[i][j+1]:
					print("║",end='')
				else:
					print(" ",end="")
			print("")
			if i < self._h-1:
				if grid[i][0] != grid[i+1][0]:
					print("╠",end="")
				else:
					print("║",end='')
				for j in range(self._w):
					if grid[i][j] != grid[i+1][j]:
						print("══",end="")
						if j == self._w-1:
							print("╣",end="")
						elif grid[i][j] != grid[i][j+1]:
							if  grid[i][j+1] == grid[i+1][j+1]:
								if grid[i+1][j] == grid[i+1][j+1]:
									print("╝",end="")
								else:
									print("╣",end="")
							elif grid[i+1][j] == grid[i+1][j+1]:
								print("╩",end="")
							else:
								print("╬",end="")
						elif grid[i+1][j] != grid[i+1][j+1]:
							if grid[i][j+1] == grid[i+1][j+1]:
								print("╗",end="")
							else:
								print("╦",end="")
						else:
							print("═",end="")
					else:
						print("  ",end="")
						if j == self._w-1:
							print("║",end="")
						elif grid[i][j] != grid[i][j+1]:
							if grid[i][j+1] != grid[i+1][j+1]:
								if grid[i+1][j] == grid[i+1][j+1]:
									print("╚",end="")
								else:
									print("╠",end="")
							else:
								print("║",end="")
						else:
							if grid[i][j] != grid[i+1][j+1]:
								print("╔",end="")
							else:
								print(" ",end="")
			else:
				print("╚",end="")
				for j in range(self._w):
					print("══",end="")
					if j == self._w-1:
						print("╝",end="")
					elif grid[i][j] != grid[i][j+1]:
						print("╩",end='')
					else:
						print("═",end="")
			print("")
		# done ! (￣^￣)ゞ


	def get_numbered_grid(self):
		"""
		Generate a height*width grid in which each cell contains
		the index of the put Tile in the tiles
		"""
		grid = [[None for j in range(self._w)] for i in range(self._h)]
		for i in range(len(self._tiles)):
			for j in self._tiles[i]:
				grid[self._tiles[i].x+j[0]][self._tiles[i].y+j[1]]=i
		return grid


	######################################
	#                                    #
	#    SPECIAL PAVAGE(S) GENERATORS    #
	#                                    #
	######################################

	def from_json(jsondict):
		return Pavage(jsondict["size"]["height"],
			          jsondict["size"]["width" ],
			          [Tile.from_json(d) for d in jsondict["tiles"]],
			          dotiling=False)

# {\Pavage}------------------------------------------------------------------------------