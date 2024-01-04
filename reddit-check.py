import praw
import time
import os
import datetime
import requests

# Reddit API credentials
client_id = 'asdf'
client_secret = 'asdf'
user_agent = 'script:watchexchange_keyword_monitor:v1.0 (by /u/chrislovessushi)'

# Keywords to search for
keywords = ['submariner', '16610', '14060', '16800']

# Pushover details
pushover_user_key = 'asdf'
pushover_api_token = 'asdf'
notification_title = 'New Post'

# File to store the last checked timestamp
state_file = 'last_checked.txt'

def check_new_posts(subreddit, last_checked):
    for submission in subreddit.new(limit=10):
        if submission.created_utc > last_checked and \
           any(keyword.lower() in submission.title.lower() for keyword in keywords):
            yield submission

def send_notification(post):
    url = 'https://api.pushover.net/1/messages.json'
    data = {
        'token': pushover_api_token,
        'user': pushover_user_key,
        'message': f"New post: {post.url}",
        'title': notification_title
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print('Notification sent successfully')
    else:
        print(f'Failed to send notification: {response.text}')

def read_last_checked():
    try:
        with open(state_file, 'r') as file:
            return float(file.read().strip())
    except FileNotFoundError:
        return 0

def write_last_checked(timestamp):
    with open(state_file, 'w') as file:
        file.write(str(timestamp))

def main():
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    subreddit = reddit.subreddit('watchexchange')

    last_checked = read_last_checked()

    while True:
        print(f"Checking for new posts at {datetime.datetime.now()}")
        for post in check_new_posts(subreddit, last_checked):
            send_notification(post)
            print(f"Notification sent for post: {post.title}")
            last_checked = post.created_utc
            write_last_checked(last_checked)

        time.sleep(180)  # Wait for 3 minutes

if __name__ == '__main__':
    main()
