from abc import ABC, abstractmethod

class NProblem_state(ABC): #-------------------------------------------------------------
	def __init__(self,back_state=None, back_choice=None):
		self._back_state  = back_state
		self._back_choice = back_choice

	@abstractmethod
	def is_solved(self):
		"""
		Check if the current state is solved or not
		If so, Champagne !
		"""
		...


	@abstractmethod
	def is_unsolvable(self):
		"""
		Check if the current state is unsolvable or not
		If so, may need backtracking
		"""
		...


	@abstractmethod
	def impose_choice(self,element,choice):
		"""
		Force the element to have a certain solution.
		Mostly used if starting from scratch.
		"""
		...


	@abstractmethod
	def get_solution(self):
		...


	@abstractmethod
	def new_state(self):
		"""
		Create a new state instance by chosing a solution for an element
		The current instance can be retrieved with backtrack
		"""
		...


	@abstractmethod
	def _backtrack_update(self): ...
	def backtrack(self):
		"""
		Retreat to the still solvable previous state
		"""
		if self._back_state:
			self._backtrack_update()
			self._back_state._colors[self._back_node].remove_colors(
			                                            self._colors[self._back_node])
		return self._back_state


	@abstractmethod
	def loop_heuristics(self,element):
		"""
		For an element, use some heuristics to determine better the possible solutions
		it can take.
		Returns True if a change was made.
		"""
		...
	def last_heuristics(self): return False


	def update(self,choice_nb):
		"""
		Try to update the possible elements as many times as it can.
		Stops when no change can be made via heuristics.
		Three possible outcomes :
		 - returns 0 : Stopped (but still solvable, may need new_state)
		 - returns 1 : Success (solved)
		 - returns 2 : Failure (unsovable, may need backtracking if possible)
		"""
		anychange = True
		while anychange:
			anychange = False
			for choice in range(choice_nb):
				anychange |= self.loop_heuristics(choice)
			anychange |= self.last_heuristics()
		return self.is_solved() + 2*self.is_unsolvable()


	def _solving_loop(state):
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
		return end, state


	def solve(state):
		end, state = type(state)._solving_loop(state)
		if end == 1:
			return state.get_solution()
		return None


# {\NProblem_state}----------------------------------------------------------------------

