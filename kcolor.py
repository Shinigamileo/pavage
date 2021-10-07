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
- finish coloration
"""

import random as rd
from functools import reduce

class Color: #---------------------------------------------------------------------------
	def __init__(self,colors):
		self._colors = set(colors)

	@property
	def color_nb(self):
		return len(self._colors)

	def is_colored(self):
		return self.color_nb == 1

	def is_empty(self):
		return self.color_nb == 0

	def get_color(self):
		return next(iter(self._colors))

	def remove_colors(self,c):
		self._colors -= c._colors

	def copy(self):
		return Color(self._colors)

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

	#################
	# SPECIAL INITS #
	#################

	def gradient(color_nb):
		return Color( range(color_nb) )

	def monochrome(color):
		return Color( list(color) )

	def intersection(c1,c2):
		return Color( c1._colors & c2._colors )

	def union(c1,c2):
		return Color( c1._colors | c2._colors )

# {\Color}-------------------------------------------------------------------------------


class Kcoloration_state: #---------------------------------------------------------------
	def __init__(self,color_nb,neighbors,colors, color_count,
		         back_state=None, back_choice=None):
		self._color_nb = color_nb
		self._neighbors = [n.copy() for n in neighbors]
		self._colors = [c.copy() for c in colors]
		self._color_count = color_count.copy()
		self._back_state = back_state
		self._back_choice = back_choice

	def finished(self):
		return reduce( lambda a,b : a & b.is_colored(), self._colors, True )

	def new_state(self,choice,color):
		new_state = Kcoloration_state(self._color_nb,self._neighbors,
			                           self._colors, self._color_count,
			                           back_state=self, back_choice=choice)
		new_state._colors[choice] = color
		new_state._color_count[color.get_color()] += 1
		return new_state

	def backtrack(self):
		if self._back_state:
			self._back_state._colors[self._back_choice].remove_colors(
			                                            self._colors[self._back_choice])
		return self._back_state

	def random_color(self,choice):
		chosable_color = []
		mini = float('inf')
		for c in self._colors[choice]:
			chosable_color = (mini <= self._color_count[c])*chosable_color \
			                 + (mini >= self._color_count[c])*list(Color.monochrome(c))
			mini = min(mini,self._color_count[c])
		return rd.choice(chosable_color)

# {\Kcoloration_state}-------------------------------------------------------------------


def coloration(neighbors,color_nb=3):
	"""
	Given a number of colors color_nb, associate
	to each of its tiles a color (more of a number)
	such that two neighbour nodes don't have the same.
	This problem is NP-complete and this algorithm uses heuristics and back-tracking.
	"""
	return None