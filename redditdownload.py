import praw,requests,re, random

r = praw.Reddit(client_id ='h8abz6nGs4rXlg7dUNfUGg',
                client_secret='BX47L5mxpq6arDZDPcm8PAbWNHgC5g',
                user_agent ='web:minecraftbot_r:v1 (by u/darq_souls_so_easy)')

class RedditPost:
    submission: praw.Reddit.submission

class RedditDownload():
    def getRandom(subreddit: str):
        global r

        subreddit = r.subreddit(subreddit)
        posts = [post for post in subreddit.hot(limit=20)]
        random_post_number = random.randint(0, 20)
        random_post = posts[random_post_number]
        post :RedditPost = RedditPost()
        post.submission = random_post
        return post
    def getTop(subreddit : str, time_filter : str):
        global r

        subreddit = r.subreddit(subreddit)
        for submission in subreddit.top(time_filter='day', limit=1):
            post :RedditPost = RedditPost()
            post.submission = submission
            return post

if __name__ == '__main__':
    print(RedditDownload.getTop('EarthPorn', 'day'))