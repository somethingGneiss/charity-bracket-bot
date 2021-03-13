# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 2021

@author: somethingGneiss
"""

#%%IMPORTS

import numpy as np
import pandas as pd
import praw


#%% IMPORT FOODBANKS CSV

tandb = pd.read_csv('./cbb_bot.csv')


#%% SIGN-IN AND O-AUTH

# redact inputs when pushing to github!!!
reddit = praw.Reddit( client_id     ='',
                      client_secret ='',
                      user_agent    ='',
                      username      ='',
                      password      ='' )

# get desired subreddit
subreddit = reddit.subreddit('collegebasketball')


#%% READ INCOMING POSTS AND COMMENT APPRORIATE LINKS

fake_title_list = []
past_sids  = pd.read_csv('./logged_sids.csv', index_col=0)
team_names = pd.read_csv('./logged_team_names.csv', index_col=0)
for submission in subreddit.stream.submissions():
    if '[Post Game Thread]' in submission.title:
        if submission.id not in list(past_sids.sids):
            
            # to be used later
            idx3=[]
            
            # store submission id to ensure no duplicate comments
            past_sids = past_sids.append(pd.DataFrame({'sids':[submission.id]}), 
                                                   ignore_index=True, )
            
            # read out to static csv containing only submission ids
            past_sids.to_csv('./logged_sids.csv')
            
            # need to find team names in post titles. Use known title format
            #   to our advantage and look between constant items. 
            for iii, word in enumerate(submission.title.split()):
            
                if ']' in word:
                    idx1 = iii
                    
                elif 'defeats' in word:
                    idx2 = iii
                    
                else:
                    if word[0].isnumeric():
                        idx3.append(iii)
            
            # grab team names using established indices
            team1 = submission.title.split()[idx1+1:idx2]
            team2 = submission.title.split()[idx2+1:idx3[0]]
            
            # sometimes team2 has a comma at the end...
            if ',' in team2[-1]:
                team2[-1]= team2[-1][0:-1]
            
            # ranked teams have their rank in their identified name, boot it
            for iii, word in enumerate(team1):
                if '#' in word:
                    # know rank will always be first word in name....
                    team1 = team1[iii+1:]
            for iii, word in enumerate(team2):
                if '#' in word:
                    # know rank will always be first word in name....
                    team2 = team2[iii+1:]
                
                
            #store team names in csv
            team_names = team_names.append(
                        pd.DataFrame({'teams':[team1,team2]}), 
                                                   ignore_index=True, )
            team_names.to_csv('./logged_team_names.csv')
            
            scores = submission.title.split()[idx3[0]]
            
            for iii, letter in enumerate(scores):
                if letter == '-':
                    idx4 = iii
                    
            # grab scores using established indices
            score1 = scores[0:idx4]
            score2 = scores[idx4+1:]
            
            
            ### get the comment ready to submit!
            # get team names correlated to csv to then link to url
            
            if str(team2) in list(tandb.teams):
                
                idx_t = np.where(tandb.teams == str(team2) )[0][0]
                
                reply_text = "Congratulations " + ' '.join(team1) + "! You're " +\
                    "moving on to the next round of the Dance! " +\
                    "Let's keep the celebration going by giving back! " +\
                    "Use the link below to donate to a food bank that " +\
                    "serves the area of our fallen comrades, " + ' '.join(team2) +\
                    ". You may donate in the amount" +\
                    " of the difference in the game score ("+ \
                    str(int(score1)-int(score2)) + " points = " +\
                    str(int(score1)-int(score2)) + " dollars) or in the " +\
                    "amount of your choosing. " +\
                    tandb.url[idx_t] + " Please use [this google form]" +\
                    "(placeholder) to report your donation so we can keep track " +\
                    "of how much r/CollegeBasketball raises for charities across " +\
                    "the country!"
                
                
                # print for now, comment for the real deal!
                print(reply_text)
                
                # submission.reply(reply_text)
                
            else:
                pass
    


