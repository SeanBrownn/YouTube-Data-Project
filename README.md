For this project, I implemented a query processing engine for multiple large sets of YouTube video data. It supports entity search and range queries, allowing users to filter it and get insights on specific videos (e.g. those with the same category, those with a minimum length/rating, etc.). Each row in the datasets consists of one video followed by up to 20 recommended videos for it. For each dataset, I found the most influential videos and analyzed their characteristics to test the effectiveness of YouTube's recommendation system. To do this, I implemented the pageRank algorithm.
