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
		if self.is_colored():
			return next(iter(self._colors))
		return tuple(self._colors)

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


class KColoration_state(np.NProblem_state): #--------------------------------------------
	def __init__(self,color_nb,neighbors,
		         colors=[], color_count=[],
		         back_state=None, back_node=None):
		node_nb = len(neighbors)
		colors += bool(not colors)*[Color.gradient(color_nb) for i in range(node_nb)]
		color_count += bool(not color_count)*[0 for i in range(color_nb)]
		self._color_nb = color_nb
		self._node_nb  =  node_nb
		self._neighbors = neighbors # since neighbors is never changed, no copy needed
		self._colors = [c.copy() for c in colors]
		self._color_count = color_count.copy()
		super().__init__(back_state,back_node)

	@property
	def _back_node(self):
		return self._back_choice
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

	def impose_choice(self,node,color):
		self._colors[node] = Color.monochrome(color)
		self._color_count[color] += 1


	def get_solution(self):
		return [c.get_color() for c in self._colors]


	def _random_node(self):
		# used by new_state, returns the node to select a color from
		# as for now : choose a node with the smallest amount of chosable colors
		chosable_nodes = []
		min_color_nb = float('inf')
		for node in range(self._node_nb):
			node_color_nb = self._colors[node].color_nb
			if node_color_nb == 1:
				continue
			chosable_nodes = (min_color_nb <= node_color_nb)*chosable_nodes \
			                + (min_color_nb >= node_color_nb)*[node]
			min_color_nb = min( min_color_nb , node_color_nb )
		# chosable_nodes = [n for n in range(self._node_nb)
		#                   if not self._colors[n].is_colored()]
		# print(chosable_nodes)
		return rd.choice(chosable_nodes)


	def _random_color(self,node):
		# used by new_state, returns a color for the chosen node
		# as for now : choose a color that is the least present
		chosable_colors = []
		min_color_count = float('inf')
		for c in self._colors[node]:
			this_count = self._color_count[c]
			chosable_colors = (min_color_count <= this_count)*chosable_colors \
			                 + (min_color_count >= this_count)*[Color.monochrome(c)]
			min_color_count = min(min_color_count,this_count)
		# chosable_colors = [Color.monochrome(c) for c in self._colors[node]._colors]
		# print([c.get_color() for c in chosable_colors])
		return rd.choice(chosable_colors)


	def new_state(self):
		"""
		Create a new state instance by chosing a node and a color to color it with
		The current instance can be retrieved with backtrack
		"""
		node  = self._random_node()
		color = self._random_color(node)
		new_state = KColoration_state(self._color_nb,self._neighbors,
			                           self._colors, self._color_count,
			                           back_state=self, back_node=node)
		new_state._colors[node] = color
		new_state._color_count[color.get_color()] += 1
		return new_state


	def _backtrack_update(self):
		self._back_state._colors[self._back_node].remove_colors(
		                                            self._colors[self._back_node])


	def loop_heuristics(self,node):
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
			# Second : is the neighbour already colored -> the node can't have the same
			if self._colors[neighbor].is_colored():
				self._colors[node].remove_colors(self._colors[neighbor])
		# Finally : if now the node is colored, add it to the total
		if self._colors[node].is_colored() :
			self._color_count[self._colors[node].get_color()] += 1
		return not (node_colors_at_beginning == self._colors[node])


	def update(self):
		return super().update(self._node_nb)


# {\KColoration_state}-------------------------------------------------------------------


def coloration(neighbors,color_nb=3):
	"""
	Given a number of colors color_nb, associate
	to each of its tiles a color (more of a number)
	such that two neighbour nodes don't have the same.
	This problem is NP-complete and this algorithm uses heuristics and back-tracking.
	"""
	state = KColoration_state(color_nb, neighbors)
	state.impose_choice(rd.randint(0,len(neighbors)-1),rd.randint(0,color_nb-1))
	return KColoration_state.solve(state)


def same_coloration(c1,c2):
	"""
	Check if the two coloration c1 and c2 have the same group partitions
	"""
	if len(c1) != len(c2):
		return False
	groups = dict()
	for i in range(c1):
		if c1[i] in groups:
			if groups[c1[i]] != c2[i]:
				return False
		groups[c1[i]] = c2[i]
	return True