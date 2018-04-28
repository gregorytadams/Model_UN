# get_positions.py

import pandas as pd 
from math import ceil
from sys import argv

'''
Current known problems:
- do schools at different times (ew)
- Bias towards double delegate committees 
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
        self.picks = self._get_picks(list(range(len(preferences))), num_delegates)
        self.assigned_committees = []
        self.num_dels_assigned = 0
            
    def _get_picks(self, sequence, num):
        '''
        Intersperses picks for small delegations.

        Takes a list of possible rounds the number of picks and returns a list of picks that they get.

        Thanks stack overflow!
        http://stackoverflow.com/questions/9873626/choose-m-evenly-spaced-elements-from-a-sequence-of-length-n
        '''
        picks = []
        length = float(len(sequence))
        for i in range(num):
            picks.append(sequence[int(ceil(i * length / num))])
        return picks


class Committee:

    def __init__(self, name, num_spots, delegation_size):
        '''
        name: name of committee
        num_spots: maximum number of delegates that can be assigned to that committee
        delegation size: 1 for single, 2 for double, and so on 
        assigned schools: the schools who have a spot on the committee 
        '''
        self.name = name
        self.num_spots = num_spots
        self.delegation_size = delegation_size
        self.assigned_schools = []

def read_info(school_info_filename, committee_info_filename):
    '''
    Takes the filepaths and returns the dataframes
    '''
    schools = pd.read_csv(school_info_filename)
    comms = pd.read_csv(committee_info_filename)
    return schools, comms

def format_for_main(schools, comms):
    '''
    Creates all the objects and fills in the information from the dataframes

    inputs:
    schools, comms: pandas dataframes from read_info

    outputs:
    teams, a list of Team objects
    committees, a dict mapping committee names to Committee objects
    '''
    teams = []
    committees = {}
    max_at_conf = 0
    comms.columns = ['Committee', 'Number of Spots', 'Delegation Size']
    schools.columns = ['School', 'Number of Delegates'] + \
                      ["Preference {}".format(str(i)) for i in range(len(comms))]
    for index, row in comms.iterrows():
        comm = Committee(row['Committee'], row['Number of Spots'], row['Delegation Size'])
        committees[row['Committee']] = comm
        max_at_conf += row['Delegation Size']
    for index, row in schools.iterrows():
        prefs = [j for j in row[2:]] 
        for i in range(ceil(row['Number of Delegates'] / max_at_conf)): # handling more delegates requested 
                                                                        # than there are committees.  
            num_dels = row['Number of Delegates'] - i * max_at_conf
            if num_dels > max_at_conf:
                team = Team(row['School']+str(i+2), max_at_conf, prefs)
                teams.append(team)
            else:
                team = Team(row['School'], row['Number of Delegates'], prefs) 
                teams.append(team)
    return teams, committees



def assign(teams, committees):
    '''
    My algorithm! Draft-based assignment.  Takes the teams' constraints/preferences and committees and 
    simulates a draft. Each team got picks assigned at initialization (first round, fourth round, etc.),
    and it iterates through each round of the draft until either all delegates are assigned or all 
    committees are filled.

    Inputs:
    teams, a list of Team objects from format_for_main
    committees, a dict of committees (name : Committee object) from format_for_main

    Outputs:
    teams, a list of Team objects with assignments 
    committees, a dict of committees (formatted the same) with assignments 
    '''
    for r in range(len(committees)):
        print("round {}".format(r))
        for team in teams:
            if r in team.picks and len(team.assigned_committees) < team.num_delegates:
                # print(team.name, team.preferences)
                for pref in team.preferences:
                    p = team.preferences.pop(team.preferences.index(pref))
                    c = committees[p]
                    if len(c.assigned_schools) < c.num_spots and team.num_dels_assigned < team.num_delegates \
                                                                                          - 1 + c.delegation_size:
                        c.assigned_schools.append(team.name)
                        team.assigned_committees.append(c.name)
                        team.num_dels_assigned += c.delegation_size
                        if team.num_dels_assigned > team.num_delegates:
                            for i, val in enumerate(team.assigned_committees):
                                if committees[val].delegation_size == 1:
                                    index_to_drop = i #no break so I can grab the last value
                                    c_to_drop = val
                            committees[c_to_drop].assigned_schools.pop(committees[c_to_drop]\
                            .assigned_schools.index(team.name))
                            team.assigned_committees.pop(index_to_drop)

                        print("assigned {} to {}".format(team.name, c.name))
                        break
                    else:
                        continue
            else:
                continue
    return teams, committees

def output(teams, committees):
    '''
    Outputs the master documents.

    Inputs from assign 
    '''
    all_school_assignments = []
    all_comm_assignments = []
    for team in teams:
        all_school_assignments.append([team.name, team.num_delegates] + team.assigned_committees)
    for comm in committees:
        all_comm_assignments.append([comm, committees[comm].num_spots, committees[comm].delegation_size] \
                                    + committees[comm].assigned_schools)
    schools_df = pd.DataFrame(all_school_assignments)
    schools_df.rename(columns = {0:'School', 1:'Number of Delegates'}, inplace = True)
    comm_df = pd.DataFrame(all_comm_assignments)
    schools_df.to_csv('all_school_assignments.csv')
    comm_df.to_csv("all_committees_assignments.csv")
    for index, row in schools_df.iterrows():
        row.to_csv("school_assignments/{}'s_assignments.csv".format(row['School']))

def go(school_filename, committee_filename):
    '''
    Runs the whole darn thing. 
    '''
    schools, comms = read_info(school_filename, committee_filename)
    teams, committees = format_for_main(schools, comms)
    teams, committees = assign(teams, committees)
    output(teams, committees)
    s = 0
    for i in teams: s += i.num_delegates 
    s2 = 0
    for key in committees: s2 += len(committees[key].assigned_schools)*committees[key].delegation_size
    if s == s2:
        print("It worked! :)")
    else:
        print("There's a bug. Bad computer. :(")

if __name__ == "__main__":
    try:
        go(argv[1], argv[2])
    except:
        print("Something went wrong.  Please make sure your usage is correct and  files are formatted correctly.")
        print("Usage: python3 get_positions.py [school_info_filepath] [committee info filepath]")







