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
- finish coloration (BUGGED !)
"""

import random as rd
from functools import reduce

class Color: #---------------------------------------------------------------------------
	def __init__(self,colors):
		self._colors = set(colors)

	@property
	def color_nb(self):
		return len(self._colors)

	def __iter__(self):
		return Color.Iterator(self)
	class Iterator:
		def __init__(self,c):
			self._cs = list(c._colors)
			self._index = 0
		def __next__(self):
			try:
				res = self._cs[self._index]
				self._index+=1
				return res
			except (IndexError):
				raise StopIteration

	def __eq__(self,c):
		return self._colors == c._colors

	def copy(self):
		return Color(self._colors)

	def is_colored(self):
		return self.color_nb == 1

	def is_empty(self):
		return self.color_nb == 0

	def get_color(self):
		return next(iter(self._colors))

	def remove_colors(self,c):
		self._colors -= c._colors

	#################
	# SPECIAL INITS #
	#################

	def gradient(color_nb):
		return Color( range(color_nb) )

	def monochrome(color):
		return Color( [color] )

	def intersection(c1,c2):
		return Color( c1._colors & c2._colors )

	def union(c1,c2):
		return Color( c1._colors | c2._colors )

# {\Color}-------------------------------------------------------------------------------


class _Kcoloration_state: #--------------------------------------------------------------
	def __init__(self,color_nb,neighbors,colors, color_count,
		         back_state=None, back_node=None):
		self._color_nb = color_nb
		self._node_nb  = len(neighbors)
		self._neighbors = [n.copy() for n in neighbors]
		self._colors = [c.copy() for c in colors]
		self._color_count = color_count.copy()
		self._back_state = back_state
		self._back_node = back_node

	@property
	def colors(self):
		return self._colors.copy()
	@property
	def color_count(self):
		return self._color_count.copy()	

	def is_solved(self):
		return reduce( lambda a,b : a and b.is_colored(), self._colors, True  )

	def is_unsolvable(self):
		return reduce( lambda a,b : a or  b.is_empty(),   self._colors, False )

	def _random_node(self):
		# used by new_state, returns the node to select a color from
		# as for now : choose a node with the smallest amount of chosable colors
		chosable_nodes = []
		# min_color_nb = float('inf')
		# for node in range(self._node_nb):
		# 	node_color_nb = self._colors[node].color_nb
		# 	chosable_nodes = (min_color_nb <= node_color_nb)*chosable_nodes \
		# 	                + (min_color_nb >= node_color_nb)*[node]
		# 	min_color_nb = min( min_color_nb , node_color_nb )
		chosable_nodes = list(range(self._node_nb))
		# print(chosable_nodes)
		return rd.choice(chosable_nodes)


	def _random_color(self,node):
		# used by new_state, returns a color for the chosen node
		# as for now : choose a color that is the least present
		chosable_colors = []
		# mini = float('inf')
		# for c in self._colors[node]:
		# 	chosable_colors = (mini <= self._color_count[c])*chosable_colors \
		# 	                 + (mini >= self._color_count[c])*[Color.monochrome(c)]
		# 	mini = min(mini,self._color_count[c])
		chosable_colors = [Color.monochrome(c) for c in self._colors[node]._colors]
		# print([c.get_color() for c in chosable_colors])
		return rd.choice(chosable_colors)


	def new_state(self):
		node  = self._random_node()
		color = self._random_color(node)
		new_state = _Kcoloration_state(self._color_nb,self._neighbors,
			                           self._colors, self._color_count,
			                           back_state=self, back_node=node)
		new_state._colors[node] = color
		new_state._color_count[color.get_color()] += 1
		# print("MAKING NEW STATE :")
		# print(new_state._back_state == self)
		# print("\tnode  : " + str(node))
		# print("\tcolor : " + str(color.get_color()))
		return new_state


	def backtrack(self):
		# print("BACKTRACKING")
		if self._back_state:
			self._back_state._colors[self._back_node].remove_colors(
			                                            self._colors[self._back_node])
		return self._back_state


	def heuristics(self,node):
		"""
		For a node, use some heuristics to determine better the possible colors
		it can take.
		Returns True if a change was made.
		"""
		node_colors_at_beginning = self._colors[node].copy()
		# First : is the node already colored ?
		if self._colors[node].is_colored():
			return False
		for neighbor in list(self._neighbors[node]):
			# Second : is the neighbour already colored ?
			if self._colors[neighbor].is_colored():
				self._colors[node].remove_colors(self._colors[neighbor])
		# Finally : if now the node is colored, add it to the total
		if self._colors[node].is_colored() :
			self._color_count[self._colors[node].get_color()] += 1
		return not (node_colors_at_beginning == self._colors[node])


	def update(self):
		"""
		Try to update the possible colors of all nodes as many times as it can.
		Stops when no change can be made via heuristics.
		Three possible outcomes :
		 - returns 0 : Stopped (but still solvable, may need new_state)
		 - returns 1 : Success (all nodes colored)
		 - returns 2 : Failure (at least one node empty, may need backtracking)
		"""
		anychange = True
		while anychange:
			anychange = False
			for node in range(self._node_nb):
				anychange |= self.heuristics(node)
		return self.is_solved() + 2*self.is_unsolvable()

	def first(color_nb, neighbors):
		node_nb = len(neighbors)
		return _Kcoloration_state(color_nb, neighbors,
			                      [Color.gradient(color_nb) for i in range( node_nb)],
			                      [           0             for i in range(color_nb)])


# {\_Kcoloration_state}------------------------------------------------------------------


def coloration(neighbors,color_nb=3):
	"""
	Given a number of colors color_nb, associate
	to each of its tiles a color (more of a number)
	such that two neighbour nodes don't have the same.
	This problem is NP-complete and this algorithm uses heuristics and back-tracking.
	"""
	state = _Kcoloration_state.first(color_nb, neighbors)
	end = False
	while not end:
		end = state.update()
		if not end:
			state = state.new_state()
			continue
		elif end == 2:
			backstate = state.backtrack()
			del state
			state = backstate
			end = 2*(not state)
	if end == 1:
		print(state._color_count)
		return [c.get_color() for c in state.colors]
	return None
