import json
tweets_data = []
tweets_file = open('part2.txt', "r")
for line in tweets_file:
    try:
        tweet = json.loads(line)
        tweets_data.append(tweet)
    except:
        continue
print tweets_data[0],len(tweets_data[0])