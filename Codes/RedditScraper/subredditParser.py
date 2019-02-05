# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 18:13:29 2019

@author: Tugce
"""

from os.path import isfile
import praw
import pandas as pd
from time import sleep
from psaw import PushshiftAPI
#import urllib.request as req

reddit = praw.Reddit(client_id='',
                     client_secret='',
                     user_agent='',
                     username = '',
                     password = '')
api = PushshiftAPI(reddit)


subredditList = ['HaircareScience','femalehairadvice','malehairadvice',
                 'curlyhair','Hair','FierceFlow']

class SubredditScraper:

    def __init__(self, sub, sort='top', lim=997, time='day', mode='w'):
        self.sub = sub 
        self.sort = sort
        self.lim = lim
        self.time = time
        self.mode = mode
        
        print(
            f'SubredditScraper instance created with values '
            f'sub = {sub}, sort = {sort}, lim = {lim}, time = {time}, mode = {mode}')

    def setSort(self):
        if self.sort == 'new':
            return self.sort, reddit.subreddit(self.sub).new(self.time, limit=self.lim)
        elif self.sort == 'top':
            return self.sort, reddit.subreddit(self.sub).top(self.time, limit=self.lim)
        elif self.sort == 'hot':
            return self.sort, reddit.subreddit(self.sub).hot(self.time, limit=self.lim)
        else:
            self.sort = 'top'
            print('Sort method was not recognized, defaulting to top.')
            return self.sort, reddit.subreddit(self.sub).hot(self.time, limit=self.lim)

    def getPosts(self):
        """Get unique posts from a specified subreddit."""

        subDict = {
            'selftext': [], 'title': [], 'id': [], 'sortedBy': [],
            'numComments': [], 'score': [], 'ups': [], 'downs': [], 'url': []
            }
        csv = f'new_{self.sub}_posts.csv'
        csv2 = f'new_{self.sub}_comments.csv'
        csv3 = f'new_{self.sub}_replies.csv'

        # Specify a sorting method
        sort, subreddit = self.setSort()

        # Set csvLoaded to True if csv exists 
        df, csvLoaded = (pd.read_csv(csv), 1) if isfile(csv) else ('', 0)
        df2, csvLoaded = (pd.read_csv(csv2), 1) if isfile(csv2) else ('', 0)
        df3, csvLoaded = (pd.read_csv(csv3), 1) if isfile(csv3) else ('', 0)

        print(f'csv = {csv}')
        print(f'After set_sort(), sort = {sort} and sub = {self.sub}')
        print(f'csvLoaded = {csvLoaded}')

        print(f'Collecting information from r/{self.sub}.')
        
        for post in subreddit:

            # Check if post.id is in df and set to True if df is empty.
            # This way new posts are still added to dictionary when df = ''
            uniqueId = post.id not in tuple(df.id) if csvLoaded else True
            
            # Save any unique, non-stickied posts with descriptions to subDict.
            if uniqueId:
                subDict['selftext'].append(post.selftext)
                subDict['title'].append(post.title)
                subDict['id'].append(post.id)
                subDict['sortedBy'].append(sort)
                subDict['numComments'].append(post.num_comments)
                subDict['score'].append(post.score)
                subDict['ups'].append(post.ups)
                subDict['downs'].append(post.downs)
                subDict['url'].append(post.url)
                productKeywords = ['shampoo','conditioner','spray','volumizer','gel',
                   'treatment','oil','conditioning','mousse','product',
                   'pomade','cream','mist','wax','fiber','clay','paste',
                   'balm','detangler','serum','heat protectant','pump',
                   'mask','texturizer','antifrizz','anti-frizz',
                   'i use','i recommend','deva','tonic','salon','essence','cleanse',
                   'smoother','haircare','color conserve','hairboutique','chemical',
                   'lather','butter','detox','elixir','vitamin','formula','leave-in',
                   'color glow','repair','powder','creme','smoothing','supplement']
                #req.urlretrieve(post.url, (str(post.id)+'_'+self.sort+'_'+self.time+'_'+str(post.subreddit)))
                post.comments.replace_more(limit=5)
                post.comment_limit = 10
                post.comment_sort = 'top'
                comment=post.comments
                commentDict={'id': [], 'parentID': [], 'linkID': [], 'score': [], 
                             'isSubmitter': [], 'body': []}
                replyDict={'id': [], 'parentID': [], 'linkID': [], 'score': [], 
                             'isSubmitter': [], 'body': []}
                for com in comment:
                    com.reply_sort = 'top' 
                    if any(keyword in com.body.lower() for keyword in productKeywords):
                        commentDict['id'].append(com.id)
                        commentDict['parentID'].append(com.parent_id)
                        commentDict['linkID'].append(com.link_id)
                        commentDict['score'].append(com.score)
                        commentDict['isSubmitter'].append(com.is_submitter)
                        commentDict['body'].append(com.body)
                    if (len(comment[0].replies) != 0):
                        children = com.replies
                        for child in children:
                            if any(keyword in child.body.lower() for keyword in productKeywords):
                                replyDict['id'].append(child.id)
                                replyDict['parentID'].append(child.parent_id)
                                replyDict['linkID'].append(child.link_id)
                                replyDict['score'].append(child.score)
                                replyDict['isSubmitter'].append(child.is_submitter)
                                replyDict['body'].append(child.body)
            sleep(0.1)

        new_df = pd.DataFrame(subDict)
        new_df2 = pd.DataFrame(commentDict)
        new_df3 = pd.DataFrame(replyDict)
        
        # Add new_df to df if df exists then save it to a csv.
        if 'DataFrame' in str(type(df)) and self.mode == 'w':
            pd.concat([df, new_df], axis=0, sort=0).to_csv(csv, index=False)
            print(
                f'{len(new_df)} new posts collected and added to {csv}')
        elif self.mode == 'w':
            new_df.to_csv(csv, index=False)
            print(f'{len(new_df)} posts collected and saved to {csv}')
        else:
            print(
                f'{len(new_df)} posts were collected but they were not '
                f'added to {csv} because mode was set to "{self.mode}"')
        
        
        if 'DataFrame' in str(type(df2)) and self.mode == 'w':
            pd.concat([df2, new_df2], axis=0, sort=0).to_csv(csv2, index=False)
            print(
                f'{len(new_df2)} new comments collected and added to {csv2}')
        elif self.mode == 'w':
            new_df2.to_csv(csv2, index=False)
            print(f'{len(new_df2)} comments collected and saved to {csv2}')
        else:
            print(
                f'{len(new_df2)} comments were collected but they were not '
                f'added to {csv2} because mode was set to "{self.mode}"')
           
            
        if 'DataFrame' in str(type(df3)) and self.mode == 'w':
            pd.concat([df3, new_df3], axis=0, sort=0).to_csv(csv3, index=False)
            print(
                f'{len(new_df3)} new replies collected and added to {csv3}')
        elif self.mode == 'w':
            new_df3.to_csv(csv3, index=False)
            print(f'{len(new_df3)} replies collected and saved to {csv3}')
        else:
            print(
                f'{len(new_df3)} replies were collected but they were not '
                f'added to {csv3} because mode was set to "{self.mode}"')    
            
# options for sort are top, hot, new
# options for time are all, year, month, week, day
for i in subredditList:
    if __name__ == '__main__':
        SubredditScraper(i, lim=2, time = 'day', mode='w', sort='top').getPosts()
