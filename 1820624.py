import module
import tutor
import ReaderWriter
import timetable
import random
import math

class Scheduler:

	def __init__(self,tutorList, moduleList):
		self.tutorList = tutorList
		self.moduleList = moduleList

	#-------------- TASK 1 --------------------------------
	#This method returns a timetable object with a schedule that is legal according to all constraints of task 1.
	def createSchedule(self):
		timetableObj = timetable.Timetable(1)

		# variables to be used in backtrack function
		count = 0 
		slots = list() # stores the slots that have been assigned
		orderedVariables = self.generateOrder() 

		# create ordered schedule of modules without tutors assigned
		self.orderedSchedule(timetableObj, orderedVariables)
		# call backtracking algorithm to create assignments
		self.backtrack(timetableObj,orderedVariables,slots,count)

		return timetableObj

	# recursive method to make assignments incrementally
	def backtrack(self,timetable,orderedVariables,slots,count):
		# base case - if all assignments are made, return true
		if (count == 25):
			return True

		# store the next module to be assigned
		var = orderedVariables[count][0]
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

		# cycle through the list of tutors that can teach the module
		for tut in orderedVariables[count][2]:

			# cycle through all slots in timetable
			for day in range(0,5):
				for slot in range(1,6):	
					# if slot is unassigned
					if [days[day],slot] not in slots:	
						# check if tutor has another slot in the current day	
						sameDay = False
						for session in range(1,6):
							if timetable.getSession(days[day],session)[0]==tut:
								sameDay = True
						# checks how many slots the tutor has in the current week
						sameWeek = 0
						for day2 in range (0,5):
								for slot2 in range(1,6):
									if timetable.getSession(days[day2],slot2)[0]==tut:
										sameWeek+=1

						# if constraints are satisfied, assign slot
						if not(sameDay) and sameWeek<2:
							timetable.addSession(days[day], slot, tut, var, "module")
							slots.append([days[day],slot])

							# recursive call with count incremented
							if (self.backtrack(timetable,orderedVariables,slots,count+1)):
								return True
							else :
								# undo assignment
								timetable.addSession(days[day], slot, "t", var, "module")
								slots.remove([days[day],slot])

		return False

	# orders all modules based on the number of tutors that can teach it
	def generateOrder(self):
		tlist = list()
		for module in self.moduleList:
			teachCount = 0 # number of tutors that can teach the module
			
			tuts = list() # list of tutors that can teach the module

			# check what tutors can teach this module
			for tutor in self.tutorList:
				if set(module.topics).issubset(set(tutor.expertise)):
					teachCount += 1
					tuts.append(tutor)

			tlist.append([module,teachCount,tuts])

		#returns list of modules, sorted by number of tutors that can teach it
		return sorted(tlist, key = lambda x: x[1])

	# create schedule based on the ordered list of modules
	def orderedSchedule(self, timetableObj, orderedVariables):
		sessionNumber = 1
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		dayNumber = 0
		
		# for each module in orderedVariables, add to timetable with blank tutor
		for elem in orderedVariables:
			timetableObj.addSession(days[dayNumber], sessionNumber, "t", elem[0], "module")
			sessionNumber = sessionNumber + 1

			if sessionNumber == 6:
				sessionNumber = 1
				dayNumber = dayNumber + 1

	#-------------- TASK 2 --------------------------------
	#This method should return a timetable object with a schedule that is legal according to all constraints of task 2.
	def createLabSchedule(self):
		timetableObj = timetable.Timetable(2)
		# create variables to be used in backtrackLab
		count = 0
		slots = list()
		orderedVariables = self.generateOrder2()

		# create ordered schedule of modules and labs without tutors assigned
		self.orderedSchedule2(timetableObj,orderedVariables)
		# call backtracking algorithm to create assignments
		self.backtrackLab(timetableObj,orderedVariables,slots,count)

		return timetableObj

	#recursive method to make assignments
	def backtrackLab(self,timetable,orderedVariables,slots,count):
		if (count == 50):
			return True

		# store next module/lab to be assigned
		var = orderedVariables[count][0]
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

		# cycle through the list of tutors that can teach the module/lab
		for tut in orderedVariables[count][2]:

			# if the variable type is a module
			if orderedVariables[count][3] == "module":
				# cycle through slots in timetable
				for day in range(0,5):
					for slot in range(1,11):	
						# if slot is unassigned
						if [days[day],slot] not in slots:	

							# call method to check tutor credits on this day and week
							sameDay = self.evaluateConstraints(timetable,day,tut)[0]
							sameWeek = self.evaluateConstraints(timetable,day,tut)[1]

							# if constraints are satisfied, attempt to add module to the timetable
							if sameDay==0 and sameWeek<3:
								timetable.addSession(days[day], slot, tut, var, "module")
								slots.append([days[day],slot])

								# recursively call method with count incremented and current assignments
								if (self.backtrackLab(timetable,orderedVariables,slots,count+1)):
									return True
								else:
									print("undo")
									# otherwise undo assignment 
									timetable.addSession(days[day], slot, "t", var, "module")
									slots.remove([days[day],slot])

			# otherwise the variable type is a lab
			else: 
				# cycle through slots in timetable
				for day in range(0,5):
					for slot in range(1,11):
						# if slot is unassigned	
						if [days[day],slot] not in slots:	

							# check constraints
							sameDay = self.evaluateConstraints(timetable,day,tut)[0]
							sameWeek = self.evaluateConstraints(timetable,day,tut)[1]

							# if constraints are satisfied, attempt to make assignment of lab
							if sameDay<2 and sameWeek<4:
								timetable.addSession(days[day], slot, tut, var, "lab")
								slots.append([days[day],slot])

								# recursive call with assignment
								if (self.backtrackLab(timetable,orderedVariables,slots,count+1)):
									return True
								else:
									print("undo")
									# otherwise undo assignment
									timetable.addSession(days[day], slot, "t", var, "lab")
									slots.remove([days[day],slot])
		return False

	# this method calculates the number of credits the tutor has on the given day, and the week
	def evaluateConstraints(self,timetable,d,tut):
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		
		# cycle through the slots in the given day d
		sameDay = 0
		for session in range(1,11):
			if timetable.getSession(days[d],session)[0]==tut:
				if (timetable.getSession(days[d],session)[2] == "module"):
					sameDay += 2
				else:
					sameDay += 1

		# cycle through slots in the week
		sameWeek = 0
		for day in range (0,5):
				for slot in range(1,11):
					if timetable.getSession(days[day],slot)[0]==tut:
						if (timetable.getSession(days[day],slot)[2] == "module"):
							sameWeek += 2
						else:
							sameWeek += 1

		# return the number of credits / day and / week
		return [sameDay,sameWeek]

	# orders all modules and labs based on the number of tutors that can teach it
	def generateOrder2(self):
		llist = list()
		# cycle through all modules and calculate the number of tutors that can teach it
		for module in self.moduleList:
			teachableM = 0
			tuts = list()
			for tutor in self.tutorList:
				if set(module.topics).issubset(set(tutor.expertise)):
					teachableM += 1
					tuts.append(tutor)

			llist.append([module,teachableM,tuts,"module"])

		# cycle through all labs and calculate the number of tutors that can teach it
		# the above loop and this loop could be combined, but keeping seperate for greater clarity
		for lab in self.moduleList:
			teachableL = 0
			tuts = list()
			for tutor in self.tutorList:
				if any(elem in lab.topics for elem in tutor.expertise):
					teachableL += 1
					tuts.append(tutor)

			llist.append([lab,teachableL,tuts,"lab"])

		#returns list of modules, sorted by number of tutors that can teach it
		return sorted(llist,key = lambda x: x[1])

	# create schedule based on the ordered list of modules and labs
	def orderedSchedule2(self, timetableObj, orderedVariables):
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		dayNumber = 0
		sessionNumber = 1

		# for each module/lab in ordered list add to timetable
		for elem in orderedVariables:
			if (elem[3]=="module"):
				timetableObj.addSession(days[dayNumber], sessionNumber, "t", elem[0], "module")
			else:
				timetableObj.addSession(days[dayNumber], sessionNumber, "t", elem[0], "lab")

			sessionNumber = sessionNumber + 1

			if sessionNumber == 11:
				sessionNumber = 1
				dayNumber = dayNumber + 1

	#-------------- TASK 3 --------------------------------
	#This method returns a timetable object with a schedule that is legal according to all constraints of task 3.
	def createMinCostSchedule(self):
		timetableObj = timetable.Timetable(3)

		print("Calculating the minimum cost...")
		print("Can take longer for problems 6 and 8")

		solutions = list()
		takenTutors = dict()

		loopcount = 0
		loop = True

		# create loop to repeat backtracking until minimum value solution is found
		while loop:
			assignment = list() # stores the successful assignments
			slots = list()
			solutionCost = 0 # stores solution cost of this backtrack call

			# sets all tutors as available
			for tutor in self.tutorList:
				takenTutors[tutor] = 0

			# create empty schedule without anything assigned
			self.emptySchedule(timetableObj)
			# calls backtrack method
			self.backtrack3(timetableObj,assignment,slots,solutionCost,solutions,takenTutors)

			# if optimal solution is reached
			if solutions[loopcount][1] <= 10050:
				loop = False

			loopcount += 1

			# timeout for cases when optimal solution is not 10050
			if loopcount > 200:
				loop = False

		# sort the solutions by the cost
		sortedSolutions = sorted(solutions,key = lambda x: x[1])
		# minimum cost is at first index
		finalAssignment = sortedSolutions[0][0]

		# add lowest cost assignment to timetable object
		for x in range(len(finalAssignment)):
				t = finalAssignment[x][0]
				m = finalAssignment[x][1]
				d = finalAssignment[x][2]
				s = finalAssignment[x][3]
				ty = finalAssignment[x][4]
				if ty == "module":
					timetableObj.addSession(d, s, t, m, "module")
				else:
					timetableObj.addSession(d, s, t, m, "lab")
	
		return timetableObj

	# recursive method to make assignments
	def backtrack3(self,timetable,assignment,slots,solutionCost,solutions,takenTutors):
		# create dictionaries to store the status of modules and labs
		takenModules = dict()
		takenLabs = dict()

		# check to see what tutors are available and which have reached the weekly credit limit
		for t in self.tutorList:
			sWeek = self.evaluateConstraints2(timetable,0,t,takenTutors)[1]
			if sWeek == 4:
				takenTutors[t] = 1
			else:
				takenTutors[t] = 0

		# check to see which modules and labs have already been assigned 
		for m in self.moduleList:
			takenModules[m] = 0
			takenLabs[m] = 0
			for e in assignment:
				if e[1]==m and e[4] == "module":
					takenModules[m] = 1

			for el in assignment:
				if el[1]==m and el[4] == "lab":
					takenLabs[m] = 1

		# creates ordered list of variables, taking into account the already assigned modules, labs and tutors
		orderedVariables = self.generateOrder3(takenTutors,takenModules,takenLabs)

		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]	

		# base case for recursion if all assignments have been made
		if (len(assignment) == 50):
			labscost = 0
			# calculate the cost of labs for each tutor
			for x in self.tutorList:
				labl = list() # to store the list of labs taught by the tutor

				for dday in range(0,5):
					for sslot in range(1,11):
						# if tutor teaches the lab session add to the list
						if timetable.getSession(days[dday],sslot)[0]==x and (timetable.getSession(days[dday],sslot)[2] == "lab"):
							labl.append([dday,sslot])

				# calculate the cost of the all the labs taught by the tutor and add to overall lab cost
				labscost = labscost + self.previousLabCost(labl)
			
			# add all lab costs to overall solution cost
			solutionCost = solutionCost + labscost
			# add the assignment and solution cost to list of solutions
			solutions.append([assignment,solutionCost])

			return True

		# store next module/lab to be assigned
		var = orderedVariables[0][0]
		ttList = orderedVariables[0][2]
		sessionType = orderedVariables[0][3]

		# generate the assignments for variable - every available slot in timetable with all the tutors that can teach it
		# sorted by the cost
		listOfCosts = self.costList(timetable,var,ttList,slots,sessionType,assignment)

		# cycle through possible assignments 
		for elem in listOfCosts:

			cost = elem[0]
			tut = elem[1]
			day = elem[2]
			slot = elem[3]

			# if the variable type is a module
			if sessionType == "module":

				if [days[day],slot] not in slots:	
					# call method to check tutor credits on this day and week
					sameDay = self.evaluateConstraints2(timetable,day,tut,takenTutors)[0]
					sameWeek = self.evaluateConstraints2(timetable,day,tut,takenTutors)[1]

					# if constraints are satisfied, attempt to add module to the timetable
					if sameDay==0 and sameWeek<3:

						timetable.addSession(days[day], slot, tut, var, "module")
						assignment.append([tut,var,days[day],slot,"module",cost])
						slots.append([days[day],slot])
						solutionCost = solutionCost + cost

						# recursively call backtrack method with new solutionCost and assignment
						if (self.backtrack3(timetable,assignment,slots,solutionCost,solutions,takenTutors)):
							return True
						else:
							# otherwise undo assignment
							assignment.remove([tut,var,days[day],slot,"module",cost])
							timetable.addSession(days[day], slot, "t", var, "module")
							slots.remove([days[day],slot])
							solutionCost = solutionCost - cost

			# otherwise the variable type is a lab
			else: 
				# cycle through slots in timetable
				if [days[day],slot] not in slots:	
					# check constraints
					sameDay = self.evaluateConstraints2(timetable,day,tut,takenTutors)[0]
					sameWeek = self.evaluateConstraints2(timetable,day,tut,takenTutors)[1]

					# if constraints are satisfied, attempt to make assignment of lab
					if sameDay<2 and sameWeek<4:
						timetable.addSession(days[day], slot, tut, var, "lab")
						assignment.append([tut,var,days[day],slot,"lab",cost])
						slots.append([days[day],slot])
						
						# recursive call with assignment
						if (self.backtrack3(timetable,assignment,slots,solutionCost,solutions,takenTutors)):
							return True
						else:
							# otherwise undo assignment
							assignment.remove([tut,var,days[day],slot,"lab",cost])
							timetable.addSession(days[day], slot, "t", var, "lab")
							slots.remove([days[day],slot])
							
		
		return False

	# this method calculates the number of credits the tutor has on the given day, and the week
	def evaluateConstraints2(self,timetable,d,tut,takenTutors):
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

		# cycle through the slots in the given day d
		sameDay = 0
		for session in range(1,11):
			if timetable.getSession(days[d],session)[0]==tut:
				if (timetable.getSession(days[d],session)[2] == "module"):
					sameDay += 2
				else:
					sameDay += 1

		# cycle through slots in the week
		sameWeek = 0
		for day in range (0,5):
				for slot in range(1,11):
					if timetable.getSession(days[day],slot)[0]==tut:
						if (timetable.getSession(days[day],slot)[2] == "module"):
							sameWeek += 2
						else:
							sameWeek += 1

		# return the number of credits / day and / week
		return [sameDay,sameWeek]

	# this method takes a module/lab and a list of tutors that can teach it
	# and returns a list of [cost, tutor, day, slot] sorted by the cost of making that assignment
	def costList(self,timetable,module,ttList,slots,sessionType,assignment):
		costList = list()
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

		# for each tutor that can teach the module
		for tut in ttList:
			# goes through every slot in the timetable
			for day in range(0,5):
					for slot in range(1,11):
						# if slot is not taken
						if [days[day],slot] not in slots:
							# calculate the cost of making the assignment of the tutor at this slot
							c = self.calculateCost(timetable,tut,day,slot,sessionType,module)
							
							# calculate number of free slots on this day for heuristic
							slotHeuristic = 0
							for ses in range(1,11):
								if [days[day],ses] not in slots:
									slotHeuristic -= 1

							# add the assignment and cost to list
							costList.append([c,tut,day,slot,slotHeuristic])
							
		# sorts the cost list and if the costs are equal, sorts them by the number of free slots
		temp = sorted(costList,key = lambda x: (x[0],x[4],random.random()))

		# removes the slot heuristic from the end list
		sortedCostList = list()
		for elem in temp:
			sortedCostList.append([elem[0],elem[1],elem[2],elem[3]])
		
		return sortedCostList

	# this method takes a tutor and a slot and calculates cost of assigning to that slot
	def calculateCost(self,timetable,tut,d,s,sessionType,module):
		cost = 0
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		
		labcount = 0
		labdaycount = 0

		# if session type is module
		if sessionType == "module":
			# check if tutor taught module yesterday or tomorrow
			consecutiveB = False
			for slot in range(1,11):
				if d!=0 and timetable.getSession(days[d-1],slot)[0] == tut and timetable.getSession(days[d-1],slot)[2] == "module":
						consecutiveB = True

			consecutiveA = False
			for slot in range(1,11):
				if d!=4 and timetable.getSession(days[d+1],slot)[0] == tut and timetable.getSession(days[d+1],slot)[2] == "module":
						consecutiveA = True

			# check if tutor has taught module this week at all
			sameWeek = False
			for day in range (0,5):
				for sl in range(1,11):
					if timetable.getSession(days[day],sl)[0]==tut and (timetable.getSession(days[day],sl)[2] == "module"):
						sameWeek = True
			
			# returns the module costs
			if sameWeek == False:
				cost = 500
			elif consecutiveB == True or consecutiveA == True:
				cost = 100
			else:
				cost = 300

		# else type is lab
		else:
			# count how many labs occur on this day and week
			for slo in range(1,11):
				if timetable.getSession(days[d],slo)[0]==tut and (timetable.getSession(days[d],slo)[2] == "lab"):
					labdaycount += 1

			for day in range (0,5):
				for sl in range(1,11):
					if timetable.getSession(days[day],sl)[0]==tut and (timetable.getSession(days[day],sl)[2] == "lab"):
							labcount+=1

			labposition = 0
			count = 0
			prevlablist = list() # stores the day and slot of all previous labs taught by this tutor

			# calculate the position of the lab in the week, in terms of this tutor
			for day in range (0,5):
				for sl in range(1,11):
					# end the search when this slot is reached
					if day==d and sl == s:
						labposition = count

					#count the number of labs previous to this slot
					elif timetable.getSession(days[day],sl)[0]==tut and (timetable.getSession(days[day],sl)[2] == "lab"):
						count+=1
						prevlablist.append([day,sl])

			# calculates the sum of the previous labs taught by this tutor
			prevLabSum = self.previousLabCost(prevlablist)

			# calculates the cost of assigning the lab in this slot, taking into account discounts to labs previously assigned
			# the position of the lab matters because there are many different orders that the labs can be assigned in
			# hence the need for the previous lab sum being needed to differentiate between orders
			if labcount == 0:
				cost = 250
			elif labcount == 1 and labdaycount == 0:
				cost = 200
			elif labcount == 1 and labdaycount == 1:
				cost = -25 
			elif labcount == 2 and labdaycount == 0:
				cost = 150 
			elif labcount == 2 and labdaycount == 1 and labposition == 0:
				cost = 75 - 125 - 50 
			elif labcount == 2 and labdaycount == 1 and labposition == 1:
				cost = 75 - 100 - 50
			elif labcount == 2 and labdaycount == 1 and labposition == 2:
				cost = -25
			elif labcount == 2 and labdaycount == 2:
				cost = 75
			elif labcount == 3 and labdaycount == 0 and labposition == 0 and prevLabSum == 300:
				cost = 175
			elif labcount == 3 and labdaycount == 0 and labposition == 0 and prevLabSum > 300:
				cost = 150
			elif labcount == 3 and labdaycount == 0 and labposition == 1 and prevLabSum == 425:
				cost = 150
			elif labcount == 3 and labdaycount == 0:
				cost = 100
			elif labcount == 3 and labdaycount == 1 and labposition == 2 and prevLabSum == 375:
				cost = -25
			elif labcount == 3 and labdaycount == 1 and labposition == 2 and prevLabSum > 375:
				cost = -75
			elif labcount == 3 and labdaycount == 1:
				cost = -25
			elif labcount == 3 and labdaycount == 2 and labposition == 3:
				cost = 50
			elif labcount == 3 and labdaycount == 2:
				cost = 25
			else:
				cost = 50

		return cost

	# this method takes a list of slots that labs are assigned in, and calculates the cost.
	def previousLabCost(self,lablist):
		if (len(lablist)==0):
			return 0

		labcount = 0
		cost = 0

		# goes through every slot and calculates the cost of the labs
		for day in range(0,5):
			teachingToday = False
			possibleDiscount = 0

			for slot in range(1,11):

				if [day,slot] in lablist:

					labcount += 1

					if teachingToday == True:
						init = (300 - (50 * labcount)) / 2
					
						if possibleDiscount != 0:
							init = init - possibleDiscount
							possibleDiscount = 0

						cost = cost + init
						teachingToday = True
					else:
						init = (300 - (50 * labcount))
						disc = init/2
						possibleDiscount = disc

						cost = cost + init
						teachingToday = True

		# returns the cost of the labs
		return cost

	# orders all modules and labs based on the number of tutors that can teach it
	def generateOrder3(self,takenTutors,takenModules,takenLabs):
		# create list of available tutors
		avaTutors = list()
		for elem in self.tutorList:
			if takenTutors[elem] == 0:
				avaTutors.append(elem)

		# create list of unassigned modules
		ml = list()
		for ele in self.moduleList:
			if takenModules[ele] == 0:
				ml.append(ele)

		# create list of unassigned labs
		ll = list()
		for element in self.moduleList:
			if takenLabs[element] == 0:
				ll.append(element)

		# shuffles the list of modules and labs
		random.shuffle(ml)
		random.shuffle(ll)

		llist = list()

		# cycle through all available modules and calculate the number of tutors that can teach it
		for module in ml:
			
			teachableM = 0
			tuts = list()

			# adds tutors that can teach the module
			for tutor in avaTutors:
				if set(module.topics).issubset(set(tutor.expertise)):
					teachableM += 1

					#calculate how many modules the tutor can teach for sorting later
					tutHeuristic = 0
					for mo in self.moduleList:
						if set(mo.topics).issubset(set(tutor.expertise)):
							tutHeuristic += 1

					tuts.append([tutor,tutHeuristic])

			#sort tutors by how many modules they can teach, to assign the tutors with fewer modules teachable first
			tutSorted = sorted(tuts,key = lambda x: (x[1],random.random()))

			# remove tutHeuristic from final list of tutors that can teach the module
			tutFinal = list()
			for elem1 in tutSorted:
				tutFinal.append(elem1[0])

			llist.append([module,teachableM,tutFinal,"module"])

		# cycle through all labs and calculate the number of tutors that can teach it
		for lab in ll:
			
			teachableL = 0
			tuts = list()

			# adds tutors that can teach the lab
			for tuto in avaTutors:
				if any(elem in lab.topics for elem in tuto.expertise):
					teachableL += 1

					#calculate how many labs the tutor can teach for sorting later
					tutHeuristic = 0
					for mo in self.moduleList:
						if set(mo.topics).issubset(set(tuto.expertise)):
							tutHeuristic += 1
					
					#tuts.append(tutor)
					tuts.append([tuto,tutHeuristic])

			# #sort tutors by how many labs they can teach, to assign the tutors with fewer labs teachable first
			tutSorted = sorted(tuts,key = lambda x: (x[1],random.random()))

			# remove tutHeuristic from final list of tutors that can teach the lab
			tutFinal = list()
			for elem2 in tutSorted:
				tutFinal.append(elem2[0])

			llist.append([lab,teachableL,tutFinal,"lab"])

		#returns list of modules, sorted by number of tutors that can teach it
		return sorted(llist,key = lambda x: (x[1],random.random()))

	# create schedule based on the ordered list of modules and labs
	def emptySchedule(self, timetableObj):
		sessionNumber = 1
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		dayNumber = 0

		for day in range (0,5):
			for slot in range(1,11):
				timetableObj.addSession(days[day], slot, " ", " ", "module")
					






