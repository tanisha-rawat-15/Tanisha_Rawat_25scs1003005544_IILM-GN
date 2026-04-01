print("=== PERSONALIZED MOVIE RECOMMENDER ===")

import pandas as pd

# Load data
movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', 
                    usecols=[0,1], names=['movie_id', 'title'])
ratings = pd.read_csv('ml-100k/u.data', sep='\t',
                     names=['user_id', 'movie_id', 'rating', 'timestamp'])

# Let's look at User #1's taste
user_id = 1
user_ratings = ratings[ratings['user_id'] == user_id]

print(f"\n📊 User #{user_id}'s favorite genres:")
# Get top rated movies by this user
user_top_ratings = user_ratings[user_ratings['rating'] >= 4.0]
user_top_movies = user_top_ratings.merge(movies, on='movie_id')

print("Movies they loved:")
for _, movie in user_top_movies.head(5).iterrows():
    print(f"⭐ {movie['title']} (rated {movie['rating']}/5)")

# Recommend similar popular movies
print(f"\n🎯 RECOMMENDATIONS for User #{user_id}:")
all_movies = ratings.groupby('movie_id').agg({'rating': ['count', 'mean']}).round(2)
all_movies.columns = ['num_ratings', 'avg_rating']
all_movies = all_movies.join(movies.set_index('movie_id'))

# Filter out movies user already watched
watched_movies = user_ratings['movie_id'].unique()
recommendations = all_movies[~all_movies.index.isin(watched_movies)]
popular_recommendations = recommendations[recommendations['num_ratings'] >= 30]
top_recommendations = popular_recommendations.sort_values('avg_rating', ascending=False)

for i, (movie_id, row) in enumerate(top_recommendations.head(10).iterrows(), 1):
    print(f"{i}. {row['title']} (Rating: {row['avg_rating']}/5)")

print(f"\n🎉 Based on your taste, we think you'll love these!")
