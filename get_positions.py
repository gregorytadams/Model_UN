# get_positions.py

import pandas as pd 

'''
Current known problems:
- need to handle large teams (num delegates > num committees)
	save prefs when you pop
	rerun algo in loop with teams with unassigned delegates
- do schools at different times (ew)
'''



class Team:

	def __init__(self, name, num_delegates, preferences):
		'''
		num_delegats is an int of the total number of delegates
		preferences is the ranked preferences as a list, in order (all committees must be present)
		picks is the picks we assign to make the draft fair
		assigned committees will be the committees assigned to be outputted
		'''
		self.name = name
		self.num_delegates = num_delegates
		self.preferences = preferences
		self.picks =  list(range(len(preferences)))[::round(len(preferences)/num_delegates)]
		self.assigned_committees = []



	# def assign_committee(self, committee):
	# 	self.preferences.index(committee)

class Committee:

	def __init__(self, name, num_spots):
		self.name = name
		self.num_spots = num_spots
		self.assigned_schools = []

	# def assign_school(self, team):
	# 	'''
	# 	team is Team object.  If school can be added, adds them.  If school cannot be added, returns false and removes preference.
	# 	'''
	# 	if len(assigned_schools) < self.num_spots:
	# 		self.assigned_schools.append(team)
	# 		return True
	# 	else:
	# 		team.preferences.pop(self.name)
	# 		return False


def read_info(school_info_filename, committee_info_filename):
	schools = pd.read_csv(school_info_filename)
	comms = pd.read_csv(committee_info_filename)
	return schools, comms

def format_for_main(schools, comms):
	teams = []
	committees = {}
	rounds = max(schools["number of delegates"])
	for index, row in schools.iterrows():
		prefs = [j for j in row[2:]]
		team = Team(row['School'], row['number of delegates'], prefs) 
		teams.append(team)
	for index, row in comms.iterrows():
		comm = Committee(row['Committee'], row['number of spots'])
		committees[row['Committee']] = comm
	return teams, committees, rounds



def assign(teams, committees, num_rounds):
	for r in range(num_rounds):
		print("round {}".format(r))
		for team in teams:
			if r in team.picks and len(team.assigned_committees) < team.num_delegates:
				for pref in team.preferences:
					p = team.preferences.pop(team.preferences.index(pref))
					c = committees[p]
					if len(c.assigned_schools) < c.num_spots:
						c.assigned_schools.append(team.name)
						team.assigned_committees.append(c.name)
						print("assigned {} to {}".format(team.name, c.name))
						break
					else:
						continue
			else:
				continue
	return teams, committees

def go():
	schools, comms = read_info('school_info.csv', 'committee_info.csv')
	teams, committees, rounds = format_for_main(schools, comms)
	teams, committees = assign(teams, committees, rounds)
	for i in teams:
		print(i.assigned_committees)
	for key in committees:
		print(len(committees[key].assigned_schools))


if __name__ == "__main__":
	go()







