"""
 * -----------------------------------------------------------------------------*
 * "THE BEER-WARE LICENSE" (Revision 42):                                       *
 * Bloody Loki wrote this file. As long as you retain this notice you           *
 * can do whatever you want with this stuff. If we meet some day, and you think *
 * this stuff is worth it, you can buy me a beer in return                      *
 *                                                      Léo Michel Claude Barré *
 * -----------------------------------------------------------------------------*
"""

import random as rd
from functools import reduce

import npcomplete as np
import kcolor as kc



class Tile: #----------------------------------------------------------------------------
	"""
	A tile fo some form (given by relative indexes) that can be used for a 'pavage'.
	(x,y) are the coordinates of its top-left corner.
	"""
	def __init__(self, indexes,\
				 pos=(0,0), id=""):
		self.x = pos[0]
		self.y = pos[1]
		self._new_indexes(indexes)
		self._id = id

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

	@property                           	#
	def pos(self):                      	#
		return (self.x,self.y)              #
	@pos.setter                         	#
	def pos(self,value):                	#   pos = (x,y)
		self.x=value[0]                     #
		self.y=value[1]                     #   indexes : copy of _indexes
	@property                           	#	
	def indexes(self):                  	#	
		return self._indexes.copy()         #	
	@property								#	
	def id(self):							#	
		return self._id						#	
	@property                           	#   tlc (top-left corner)
	def tlc(self):                      	#   brc (bottom-right corner)
		return (self._x_min,self._y_min)    #       their relative position
	@property                           	#       to the (0,0) point
	def brc(self):                      	#
		return (self._x_max,self._y_max)    #   xsize / ysize of the Tile
	@property                           	#
	def xsize(self):                   	    #
		return self._x_max - self._x_min +1 #   area : number of cells covered
	@property                           	#          by the Tile
	def ysize(self):                    	#
		return self._y_max - self._y_min +1 #
	@property                           	#
	def area(self):                     	#
		return len(self._indexes)           #


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

		return hash((self.id,self.x,self.y) + tuple(set(self._indexes)))


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


	def get_graph_neighborslist(self):
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


	def get_put_indexes(self):
		return map(lambda a: (a[0]+self.x,a[1]+self.y), self)


	def is_connected(self): # TODO
		"""
		Returns True if the Tile is connected, meaning that every cell
		of the tile is connected to the others.
		┌─┐                ┌─┐              ┌─┐
		│ └─┐ : True   ;   └─┘ : True   ;   └─┼─┐ : False
		└───┘                                 └─┘
		"""
		neighlist = self.get_graph_neighborslist()
		group = set()
		nodes_to_check = {0}
		while nodes_to_check:
			node = nodes_to_check.pop()
			if node not in group:
				group.add(node)
				nodes_to_check |= neighlist[node]
		return len(group) == self.area


	def rd_weight(self,weighted=False):
		"""
		Give the wieght of the Tile.
		Can be used to make some Tiles more valuable than others.
		"""
		return 1-weighted\
				+ weighted*(self.area*self.area*self.area)


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
		grid = [[0 for j in range(self.ysize)] for i in range(self.xsize)]
		for i,j in self._indexes:
			grid[i-self._x_min][j-self._y_min]=1
		return grid


	def get_tlcoords(self):
		"""
		Give the Tile's coordinates relative to the top-left corner
		  ┏━┓ ┏                ┓     ∙ ┎─┐ ┏               ┓
		┌─┚╍╿ ┃          (0,0) ┃     ┍━┛ │ ┃         (0,1) ┃
		│   │ ┃ (1,-1) , (1,0) ┃ ->  │   │ ┃ (1,0) , (1,1) ┃
		└───┘ ┃ (2,-1) , (2,0) ┃     └───┘ ┃ (2,0) , (2,1) ┃
		      ┗                ┛           ┗               ┛
		"""
		return [(x - self._x_min , y - self._y_min) for x,y in self._indexes]


	def create_id(self):
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
		self._id = key[:-1]
		return self._id


	def fancy_display(self):
		f = self.get_form()
		for l in f:
			for c in l:
				if c:
					print("██",end="")
				else:
					print("  ",end="")
			print("")


	####################################
	#                                  #
	#    SPECIAL TILE(S) GENERATORS    #
	#                                  #
	####################################

	default_x_dir = "right" # The default directions of the xs and ys when drawing a form
	default_y_dir = "down"  # My other algorithms considers x->"down" and y->"right"

	def rectangle(h,w,pos=(0,0)):
		"""Generate a rectangular h*w Tile"""
		return Tile([(i,j) for i in range(h) for j in range(w)],pos)


	def square(c,pos=(0,0)):
		"""Generate a square c*c Tile"""
		return Tile.rectangle(c,c,pos)


	def from_form(grid,pos=(0,0),
		          x_dir="",y_dir=""):
		"""
		Use a boolean grid to generate a Tile
		[[0,0],     ┌─┐ ┏                ┓
		 [0,1], ∙ ┌─┘ │ ┃ (0,0) , (1,-1) ┃
		 [1,1], ∙ │ ┌─┘ ┃ (1,0) , (2,-1) ┃
		 [1]  ]   └─┘   ┗                ┛
		"""
		x_dir += bool(not x_dir)*Tile.default_x_dir
		y_dir += bool(not y_dir)*Tile.default_y_dir
		x_dirs = {"down" :(False, False), 
		          "up"   :(False, True ),
		          "right":(True , False),
		          "left" :(True , True )}
		y_dirs = {"down" :(True , False), 
		          "up"   :(True , True ),
		          "right":(False, False),
		          "left" :(False, True )}
		x_swap, x_back = x_dirs[x_dir]
		y_swap, y_back = y_dirs[y_dir]
		# creating the list of indexes relative to the top-left corner
		tlc_indexes = []
		i_min = float('inf') ; i_max = 0
		j_min = float('inf') ; j_max = 0
		for i in range(len(grid)):
			for j in range(len(grid[i])):
				if grid[i][j]:
					tlc_indexes.append((i,j))
					i_min = min(i_min,i) ; i_max = max(i_max,i)
					j_min = min(j_min,j) ; j_max = max(j_max,j)
		# deducing first point (0,0) (rule : always the smallest x, then y)
		x0 = (not x_swap)*((not x_back)*i_min + (x_back)*i_max)\
		    +    (x_swap)*((not x_back)*j_min + (x_back)*j_max)
		y0 = (not y_swap)*((not y_back)*j_max + (y_back)*j_min)\
		    +    (y_swap)*((not y_back)*i_max + (y_back)*i_min)
		for i,j in tlc_indexes:
			if (not x_swap)*i + (x_swap)*j == x0:
				y0 = (not y_swap)*((not y_back)*min(y0,j) + (y_back)*max(y0,j))\
		               + (y_swap)*((not y_back)*min(y0,i) + (y_back)*max(y0,i))
		# deducing other indexes relatively to point (0,0)
		indexes = [((1-2*x_back)*((not x_swap)*i+(x_swap)*j-x0),
			        (1-2*y_back)*((not y_swap)*j+(y_swap)*i-y0))
		            for i,j in tlc_indexes]
		# print(indexes)
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


	def set_for_pavage(formnrot,x_dir="",y_dir=""):
		"""
		Generate a list of Tiles given of list of couples with :
		- their form (in a boolean grid)
		- if they can be rotated
		This fuction is often used to generate a list for a Pavage object
		"""
		x_dir += bool(not x_dir)*Tile.default_x_dir
		y_dir += bool(not y_dir)*Tile.default_y_dir
		s = set()
		for form,rotate in formnrot:
			t0 = Tile.from_form(form,x_dir=x_dir,y_dir=y_dir)
			s.add(t0)
			for a in range(90,360*rotate,90):
				s.add(t0.copy().rotate(a))
		return list(s)

# {\Tile}--------------------------------------------------------------------------------



class Grid: #----------------------------------------------------------------------------
	def __init__(self,xsize,ysize,free_cells=(True,)):
		self._xs = xsize
		self._ys = ysize
		if free_cells[0]:
			self._free_cells = set(range(xsize*ysize))
		else:
			self._free_cells = free_cells[1].copy()

	@property
	def xsize(self):
		return self._xs
	@property
	def xs(self):
		return self._xs
	@property
	def ysize(self):
		return self._ys
	@property
	def ys(self):
		return self._ys
	@property
	def free_cells(self):
		return self._free_cells.copy()
	
	def __iter__(self):            # used to iter the indexes of the tile
		return Grid.Iterator(self) # for i in tile -> for i in tile._indexes
	class Iterator:
		def __init__(self,g):
			self._free_cells = list(g._free_cells)
			self._index = 0
		def __next__(self):
			try:
				res = self._free_cells[self._index]
				self._index+=1
				return res
			except (IndexError):
				raise StopIteration

	def copy(self):
		return Grid(self._xs,self._ys,(False,self._free_cells))

	def has_empty_cells(self):
		return bool(self._free_cells)

	def is_full(self):
		return not self.has_empty_cells()

	def _pos2cell(self,pos):
		return pos[0]*self._ys+pos[1]

	def _cell2pos(self,cell):
		return ( cell//self.ys , cell%self.ys )

	def cell_is_empty(self,pos):
		return self._pos2cell(pos) in self._free_cells

	def cell_random(self):
		return self._cell2pos(rd.choice(list(self._free_cells)))

	def tile_cell_coverture(self,tile,pos=()):
		pos += (not bool(pos))*tile.pos
		return set(map(lambda a: self._pos2cell(a),tile.get_put_indexes()))


	def tile_can_put(self,tile,pos):
		"""
		Check if the Tile tile can be put at pos pos
		Regards,
									   Cap'n Obvious
		"""
		x,y = pos
		return  (tile.tlc[0]+x>=0) and (tile.brc[0]+x<self._xs) \
			and (tile.tlc[1]+y>=0) and (tile.brc[1]+y<self._ys) \
			and reduce(lambda a,b : a&self.cell_is_empty((x+b[0],y+b[1])),tile,True)


	def tile_put(self,tile,pos,replace=True):
		tile.pos = replace*pos + (1-replace)*tile.pos
		self._free_cells -= self.tile_cell_coverture(tile,pos)


	def tile_unput(self,tile):
		self._free_cells |= self.tile_cell_coverture(tile,pos)


# {\Grid}--------------------------------------------------------------------------------



class Pavage: #--------------------------------------------------------------------------
	"""
	The tiling of a h*w grid. Its tiles are stocked in tiles
	  w──────>                     ┏          {0;0}              ┓
	 h┌─┬─┬─┬─┐        ╔═╦═══╦═╗   ┃  {1;1}    ┌─┐               ┃
	 │├─┼─┼─┼─┤  ───╲  ║ ╠═══╩═╣ ∙ ┃ ┌─────┐   │ │  {0;2}  {0;1} ┃
	 ∨├─┼─┼─┼─┤  ───╱  ║ ║     ║ ∙ ┃ │     │ , │ │ , ┌─┐ , ┌───┐ ┃
	  └─┴─┴─┴─┘        ╚═╩═════╝   ┗ └─────┘   └─┘   └─┘   └───┘ ┛
	"""
	def __init__(self, xs, ys, tile_set,
			   	fill     = False , # if wanna always put the biggest Tile possible
			   	weighted = False , # if the bigger the Tile, the better the chances
			   	less1x1  = False,  # if try to minimise number of 1x1
			   	dotiling = True,   # if the init DOES require a tiling
			   	):

		self._xs = xs ; self._ys = ys
		self._tiles = [] # the list of tiles that will be returned
		# if we don't need a tiling (example : if this is a copy)
		if not dotiling:
			self._tiles = [t.copy() for t in tile_set]
			return
		# else... prepare for tiling !!!
		# unoccupied_cells = set(range(xs*ys))  # set of all empty cells
		# grid = [[True for j in range(ys)] for i in range(xs)] # True : empty cell
		grid = Grid(xs,ys)
		not1x1count = less1x1 * xs * ys

		while(grid.has_empty_cells()):
			chosable_tiles = [] # where we'll stack the putable tiles
			cell_x = None ; cell_y = None # coordinates of the chosen cell

			while not chosable_tiles:
				######################################
				# randomly choose an unoccupied cell #
				######################################
				cell_x, cell_y = grid.cell_random()

				####################################
				# generate a list of putable tiles #
				####################################
				size_max = 0        # the size of the greatest putable tile
				for t in tile_set:
					eligible = grid.tile_can_put(t,(cell_x,cell_y))
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
					             and (1-(less1x1 and  (size_max==1) and eligible))
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
			grid.tile_put(tile,((cell_x , cell_y)))
			# tile.pos = (cell_x , cell_y)
			self._tiles.append(tile)
			# for i in tile:
			# 	grid[cell_x+i[0]][cell_y+i[1]] = False
			# 	unoccupied_cells.remove((cell_x+i[0])*ys+(cell_y+i[1]))


	###########################
	#                         #
	# BUILT-IN AND PROPERTIES #
	#                         #
	###########################

	@property	            #
	def xs(self):	        #   Protected variables 'get'
		return self._xs     #
	@property	            #
	def xsize(self):	    #   _xs (xsize of the tiled grid):
		return self.xs      #      xs , xsize
	@property	            #
	def ys(self):	        #   _ys (ysize of the tiled grid):
		return self._ys     #      ys , ysize
	@property	            #
	def ysize(self):	    #   _tiles (list of tiles of tiling):
		return self.ys      #      tiles
	@property	            #
	def tiles(self):	    #
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


	####################
	#                  #
	#     REPAVAGE     #
	#                  #
	####################

	class _Strict_state(np.NProblem_state): #--------------------------------------------
		def __init__(self, tile_list, tiles_choices, grid, tiles_newpos,
					 back_state=None, back_choice=None):
			self._tile_nb = len(tile_list)
			self._tile_list = tile_list
			self._tiles_choices = {t:tiles_choices[t].copy() for t in tiles_choices}
			# self._cells_choices = {c:cells_choices[t].copy() for c in cells_choices}
			self._grid = grid.copy()
			self._tiles_newpos = tiles_newpos.copy()
			super().__init__(back_state,back_choice)

		def is_solved(self):
			return self._grid.is_full()

		def is_unsolvable(self):
			return reduce( lambda a,b : a or not self._tiles_choices[b],
							self._tiles_choices, False )

		def _choices_update(self):
			for tile in self._tiles_choices:
				for pos in list(self._tiles_choices[tile]):
					if not self._grid.tile_can_put(tile,pos):
						self._tiles_choices[tile].remove(pos)
			# for cell in self._cells_choices:
			# 	pos = self._grid._cell2pos(cell)
			# 	for tile in list(self._cells_choices[pos]):
			# 		if not self._grid.tile_can_put(tile,pos):
			# 			self._cells_choices[cell].remove(tile)


		def impose_choice(self,tile,pos):
			self._tiles_newpos[tile] = pos
			self._grid.tile_put(tile,pos,replace=False)
			self._tiles_choices.pop(tile)
			self._choices_update()


		def get_solution(self):
			return self._tiles_newpos

		def _random_tile(self):
			chosable_tiles = []
			min_pos_nb = float('inf')
			for tile in self._tiles_choices:
				tile_pos_nb = len(self._tiles_choices[tile])
				chosable_tiles = (min_pos_nb <= tile_pos_nb)*chosable_tiles \
				                + (min_pos_nb >= tile_pos_nb)*[tile]
				min_pos_nb = min( min_pos_nb , tile_pos_nb )
			return rd.choice(chosable_tiles)


		def _random_pos(self,tile):
			return rd.choice(list(self._tiles_choices[tile]))

		def new_state(self):
			tile = self._random_tile()
			pos  = self._random_pos(tile)
			new_state = Pavage._Strict_state(self._tile_list, self._tiles_choices,
				                        	 self._grid, self._tile_newpos,
				                        	 back_state=self, back_node=tile)
			self.impose_choice(tile,pos)
			return new_state

		def _backtrack_update(self):
			self._back_state._tiles_choices[self._back_choice].remove(
				self._tiles_newpos[self._back_choice])

		def tile_heuristics(self,tile):
			if len(self._tiles_choices[tile])==1:
				self.impose_choice(tile,self._tiles_choices[tile].pop())
				return True
			return False

		def cell_heuristics(self,cell):
			return False

		def update(self):
			return super().update([(self.tile_heuristics, self._tiles_choices),
								   (self.cell_heuristics, self._grid)
								  ])


		def first(xsize,ysize,tiles):
			tiles_choices = None
			grid = Grid(xsize,ysize)
			tiles_newpos = [None for i in range(self._tile_nb)]
			return Pavage._Strict_state(tiles, tiles_choices, grid, tiles_newpos)


	# {\Pavage._Strict_state}------------------------------------------------------------

	def repavage(self):
		state = Pavage._Strict_state.first(self.xs,self.ys,self._tiles)
		newpos = Pavage._Strict_state.solve(state)
		newtiles = self.tiles
		for i in range(len(self.tiles)):
			newtiles[i].pos = newpos[i]
		return Pavage(self.xs, self.ys, newtiles, dotiling=False)


	##################
	#                #
	#     OTHERS     #
	#                #
	##################

	def copy(self):
		return Pavage(self._xs, self._ys, self._tiles, dotiling = False)


	def json(self,color_nb=0):
		json_dict = {}
		json_dict["size"] = {"xsize" : self._xs,
							 "ysize"  : self._ys
						 }
		json_dict["tiles"]=[]
		for t in self._tiles:
			json_dict["tiles"].append(t.json())
		if color_nb:
			grid = self.get_numbered_grid()
			colors = self.get_coloration(color_nb)
			for i in range(self._tiles):
				tile = self._tile[i]
				json_dict["tiles"][i]["tag"] = colors[grid[tile.x][tile.y]]
		return json_dict


	def get_graph_neighborslist(self):
		"""
		Give the associated graph of the object
		under the form of a neighbors'list
		"""
		grid = self.get_numbered_grid()
		neighlist = [set() for i in range(len(self._tiles))]
		for i in range(self._xs-1):
			for j in range(self._ys-1):
				for di,dj in [(1,0),(0,1)]:
					neighlist[grid[ i  ][ j  ]].add(grid[i+di][j+dj])
					neighlist[grid[i+di][j+dj]].add(grid[ i  ][ j  ])
			neighlist[grid[ i ][-1]].add(grid[i+1][-1])
			neighlist[grid[i+1][-1]].add(grid[ i ][-1])
		for j in range(self._ys-1):
			neighlist[grid[-1][ j ]].add(grid[-1][j+1])
			neighlist[grid[-1][j+1]].add(grid[-1][ j ])
		for i in range(len(neighlist)):
			neighlist[i] -= {i}
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
		count = {"Total":[l,float(100),float(100)]}
		tmp_count = {}
		for t in self._tiles:
			key = t.create_id()
			_ = key.split("\n")
			key = "%sx%s" % (len(_[0]), len(_))
			if key not in tmp_count:
				tmp_count[key] = [0,0,0]
			tmp_count[key][0] += 1
			tmp_count[key][1]  = round(tmp_count[key][0]/l*100,
				                        roundto)
			tmp_count[key][2]  = round(tmp_count[key][0]*t.area/(self._xs*self._ys)*100,
				                        roundto)

		count["tiles"] = {k:(tmp_count[k][0],
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
		return kc.coloration(self.get_graph_neighborslist(),color_nb)


	fancy_colors = ["\033[31m","\033[32m", # colors for fancy_display on Unix terminal
	                "\033[34m","\033[33m", # in order : red, green, blue,
	                "\033[35m","\033[36m", #            yellow, magenta, cyan
	                "\033[37m","\033[30m", #            white, black
	                "\033[91m","\033[92m", #            and the same 8 in bright
	                "\033[94m","\033[93m", #            
	                "\033[95m","\033[96m", #            
	                "\033[97m","\033[90m", #            
	               ]
	fancy_end = "\033[0m"
	def fancy_display(self,colors=0):
		"""
		Print the pavage in a fancy way. It'll look just like the drawings
		I made with the Box Unicode characters. They're sooooo pretty <3
		"""
		grid = self.get_numbered_grid()
		if colors:
			colo = self.get_coloration(colors)
			for i in range(self._xs):
				for j in range(self._ys):
					this_color = Pavage.fancy_colors[colo[grid[i][j]]]
					print(this_color + "██" + Pavage.fancy_end,end="")
				print("")
		else:
			print("╔",end="")
			for j in range(self._ys):
				print("══",end="")
				if j == self._ys-1:
					print("╗",end="")
				elif grid[0][j] != grid[0][j+1]:
					print("╦",end='')
				else:
					print("═",end="")
			print("")
			for i in range(self._xs):
				print("║",end="")
				for j in range(self._ys):
					print("  ",end="")
					if j == self._ys-1 or grid[i][j] != grid[i][j+1]:
						print("║",end='')
					else:
						print(" ",end="")
				print("")
				if i < self._xs-1:
					if grid[i][0] != grid[i+1][0]:
						print("╠",end="")
					else:
						print("║",end='')
					for j in range(self._ys):
						if grid[i][j] != grid[i+1][j]:
							print("══",end="")
							if j == self._ys-1:
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
							if j == self._ys-1:
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
					for j in range(self._ys):
						print("══",end="")
						if j == self._ys-1:
							print("╝",end="")
						elif grid[i][j] != grid[i][j+1]:
							print("╩",end='')
						else:
							print("═",end="")
				print("")
		# done ! (￣^￣)ゞ


	def get_numbered_grid(self):
		"""
		Generate a xsize*ysize grid in which each cell contains
		the index of the put Tile in the tiles
		"""
		grid = [[None for j in range(self._ys)] for i in range(self._xs)]
		for i in range(len(self._tiles)):
			for j in self._tiles[i]:
				grid[self._tiles[i].x+j[0]][self._tiles[i].y+j[1]]=i
		return grid

	def tag_tiles(self, nbKcol):
		"""
			Retourne les tiles taggués
		"""
		grigrid = self.get_numbered_grid()
		colors = self.get_coloration(nbKcol)
		json_dict = self.json()
		for tile in json_dict["tiles"]:
			x, y = tile["pos"]
			tile["tag"] = colors[grigrid[tile["pos"][0]][tile["pos"][1]]]
		return json_dict


	######################################
	#                                    #
	#    SPECIAL PAVAGE(S) GENERATORS    #
	#                                    #
	######################################

	def from_json(jsondict):
		return Pavage(jsondict["size"]["xsize"],
			          jsondict["size"]["ysize" ],
			          [Tile.from_json(d) for d in jsondict["tiles"]],
			          dotiling=False)

# {\Pavage}------------------------------------------------------------------------------