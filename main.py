print("=" * 60)
print("🎬 COMPLETE MOVIE RECOMMENDATION SYSTEM")
print("=" * 60)

import pandas as pd
import numpy as np
from genre_based import genre_based

def collaborative_simple():
    """Simple collaborative filtering"""
    print("\n🤖 COLLABORATIVE FILTERING")
    
    movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', 
                        usecols=[0,1], names=['movie_id', 'title'])
    ratings = pd.read_csv('ml-100k/u.data', sep='\t',
                         names=['user_id', 'movie_id', 'rating', 'timestamp'])
    
    try:
        user_id = int(input("Enter User ID (1-1075): "))
        if user_id < 1 or user_id > 1075:
            print("❌ Please enter a User ID between 1-1075")
            return
    except:
        print("❌ Please enter a valid number!")
        return
    
    # Get user's ratings
    user_ratings = ratings[ratings['user_id'] == user_id]
    
    if len(user_ratings) == 0:
        print(f"❌ No ratings found for User #{user_id}")
        return
    
    print(f"\n📊 User #{user_id}'s favorite movies:")
    top_rated = user_ratings.nlargest(5, 'rating').merge(movies, on='movie_id')
    for i, (_, movie) in enumerate(top_rated.iterrows(), 1):
        print(f"   {i}. {movie['title']} (rated {movie['rating']}/5)")
    
    # Get movies user hasn't watched
    user_watched = user_ratings['movie_id'].unique()
    
    # Get movie statistics
    movie_stats = ratings.groupby('movie_id').agg({
        'rating': ['count', 'mean']
    }).round(3)
    movie_stats.columns = ['num_ratings', 'avg_rating']
    movie_stats = movie_stats.join(movies.set_index('movie_id'))
    
    # Filter out watched movies and get popular ones
    recommendations = movie_stats[~movie_stats.index.isin(user_watched)]
    popular_recs = recommendations[recommendations['num_ratings'] >= 30]
    top_recs = popular_recs.nlargest(10, 'avg_rating')
    
    print(f"\n🎬 RECOMMENDATIONS for User #{user_id}:")
    print("=" * 50)
    for i, (movie_id, movie) in enumerate(top_recs.iterrows(), 1):
        print(f"{i:2d}. {movie['title']}")
        print(f"    Rating: {movie['avg_rating']}/5 | Based on {movie['num_ratings']} reviews")
        print()

def content_simple():
    """Simple content-based recommendations""" 
    movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', 
                        usecols=[0,1], names=['movie_id', 'title'])
    ratings = pd.read_csv('ml-100k/u.data', sep='\t',
                         names=['user_id', 'movie_id', 'rating', 'timestamp'])
    
    # Get search term directly
    search_term = input("\n🔍 Enter movie name to search: ").strip()
    
    if not search_term:
        print("❌ Please enter a movie name")
        return
    
    # Find matching movies
    matches = movies[movies['title'].str.contains(search_term, case=False, na=False)]
    
    if len(matches) == 0:
        print(f"❌ No movies found containing '{search_term}'")
        return
    
    print(f"\n✅ Found {len(matches)} movies:")
    for i, (_, movie) in enumerate(matches.iterrows(), 1):
        print(f"{i}. {movie['title']}")
    
    
    # Option 2: Or if you want to show something else instead of recommendations
    # You could show movie statistics or just a completion message
    movie_ratings = ratings.groupby('movie_id').agg({'rating': ['mean', 'count']})
    movie_ratings.columns = ['avg_rating', 'num_ratings']
    movie_ratings = movie_ratings.reset_index().merge(movies, on='movie_id')
    
    # Show info about the found movies instead of recommendations
    print(f"\n📊 Information about found movies:")
    for i, (_, movie) in enumerate(matches.iterrows(), 1):
        movie_info = movie_ratings[movie_ratings['movie_id'] == movie['movie_id']]
        if len(movie_info) > 0:
            info = movie_info.iloc[0]
            print(f"{i}. {movie['title']} - Avg Rating: {info['avg_rating']:.1f}/5 ({info['num_ratings']} ratings)")
        else:
            print(f"{i}. {movie['title']} - No rating data")


def popularity_based():
    """Trending movies"""
    print("\n📊 TRENDING MOVIES ")
    
    movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', 
                        usecols=[0,1], names=['movie_id', 'title'])
    ratings = pd.read_csv('ml-100k/u.data', sep='\t',
                         names=['user_id', 'movie_id', 'rating', 'timestamp'])
    
    # Extract year from movie titles
    def extract_year(title):
        import re
        match = re.search(r'\((\d{4})\)', str(title))
        return int(match.group(1)) if match else 0
    
    movies_with_year = movies.copy()
    movies_with_year['year'] = movies['title'].apply(extract_year)
    
    # Filter only 2024-2025 movies
    recent_movies = movies_with_year[
        (movies_with_year['year'] >= 2024) & 
        (movies_with_year['year'] <= 2025)
    ]
    
    if len(recent_movies) == 0:
        #print("❌ No trending movies found in database")
        return
    
    
    # Calculate weighted rating (your original logic)
    C = ratings['rating'].mean()
    m = ratings['movie_id'].value_counts().quantile(0.9)
    
    movie_stats = ratings.groupby('movie_id').agg({
        'rating': ['count', 'mean']
    }).round(3)
    movie_stats.columns = ['num_ratings', 'avg_rating']
    movie_stats = movie_stats.join(movies_with_year.set_index('movie_id'))
    
    # Filter for 2024-2025 movies that meet the rating threshold
    qualified = movie_stats[
        (movie_stats.index.isin(recent_movies['movie_id'])) & 
        (movie_stats['num_ratings'] >= m)
    ]
    
    if len(qualified) == 0:
        #print("❌ No recent movies meet the popularity threshold yet")
        #print("📈 Showing all trending movies by rating:")
        qualified = movie_stats[movie_stats.index.isin(recent_movies['movie_id'])]
        if len(qualified) == 0:
            return
    
    qualified = qualified.copy()
    qualified['weighted_rating'] = (
        (qualified['num_ratings'] / (qualified['num_ratings'] + m)) * qualified['avg_rating'] + 
        (m / (qualified['num_ratings'] + m)) * C
    )
    
    top_trending = qualified.nlargest(10, 'weighted_rating')
    
    
    print("=" * 60)
    
    for i, (_, movie) in enumerate(top_trending.iterrows(), 1):
        print(f"{i:2d}. {movie['title']}")
        print(f"    Rating: {movie['avg_rating']}/5 | Reviews: {movie['num_ratings']}")
        print(f"    Score: {movie['weighted_rating']:.3f}")
    
    print("=" * 60)

def hybrid_system():
    """Hybrid: User's favorites + Recent movies from same genres"""
    print("\n📈 HYBRID RECOMMENDATION SYSTEM")
    
    # Load movies with genres
    movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', 
                        names=['movie_id', 'title', 'release_date', 'video_release', 'imdb_url',
                              'unknown', 'action', 'adventure', 'animation', 'childrens', 'comedy',
                              'crime', 'documentary', 'drama', 'fantasy', 'film_noir', 'horror',
                              'musical', 'mystery', 'romance', 'sci_fi', 'thriller', 'war', 'western'])
    
    ratings = pd.read_csv('ml-100k/u.data', sep='\t',
                         names=['user_id', 'movie_id', 'rating', 'timestamp'])
    
    max_user_id = ratings['user_id'].max()
    
    try:
        user_id = int(input(f"Enter User ID (1-{max_user_id}): "))
        if user_id < 1 or user_id > max_user_id:
            print(f"❌ Please enter a valid User ID")
            return
    except:
        print("❌ Please enter a valid number!")
        return
    
    # Get user's ratings
    user_ratings = ratings[ratings['user_id'] == user_id]
    
    if len(user_ratings) == 0:
        print(f"❌ No ratings found for User #{user_id}")
        return
    
    # Step 1: Show user's favorite movies
    print(f"\n📊 User #{user_id}'s FAVORITE MOVIES:")
    print("-" * 40)
    top_rated = user_ratings.nlargest(5, 'rating').merge(movies, on='movie_id')
    for i, (_, movie) in enumerate(top_rated.iterrows(), 1):
        print(f"{i}. {movie['title']} (rated {movie['rating']}/5)")
    
    # Step 2: Find user's favorite genres from their top movies
    user_watched = user_ratings['movie_id'].unique()
    user_top_movies = top_rated['movie_id'].tolist()
    
    # Get genres of user's favorite movies
    favorite_genres = set()
    for movie_id in user_top_movies:
        movie_data = movies[movies['movie_id'] == movie_id].iloc[0]
        # Check which genres are set to 1 for this movie
        genre_columns = ['action', 'adventure', 'animation', 'childrens', 'comedy',
                        'crime', 'documentary', 'drama', 'fantasy', 'film_noir', 'horror',
                        'musical', 'mystery', 'romance', 'sci_fi', 'thriller', 'war', 'western']
        for genre in genre_columns:
            if movie_data[genre] == 1:
                favorite_genres.add(genre)
    
    print(f"\n🎭 genres: {', '.join(favorite_genres)}")
    
    # Step 3: Recommend recent movies from similar genres
    # Extract year from movie titles
    def extract_year(title):
        import re
        match = re.search(r'\((\d{4})\)', str(title))
        return int(match.group(1)) if match else 0
    
    movies_with_year = movies.copy()
    movies_with_year['year'] = movies['title'].apply(extract_year)
    
    # Filter: unwatched movies from favorite genres, recent years
    recommendations = []
    for movie_id, movie in movies_with_year.iterrows():
        # Skip if user already watched this movie
        if movie['movie_id'] in user_watched:
            continue
        
        # Check if movie has any of user's favorite genres
        has_favorite_genre = False
        for genre in favorite_genres:
            if movie[genre] == 1:
                has_favorite_genre = True
                break
        
        if has_favorite_genre and movie['year'] >= 2020:  # Movies from 2020 onwards
            recommendations.append(movie)
    
    if not recommendations:
        print("\n❌ No recent similar movies found. Try a different user ID.")
        return
    
    # Convert to DataFrame and sort by year (newest first)
    rec_df = pd.DataFrame(recommendations)
    rec_df = rec_df.sort_values('year', ascending=False)
    
    # Get ratings for these movies
    movie_stats = ratings.groupby('movie_id').agg({
        'rating': ['count', 'mean']
    }).round(3)
    movie_stats.columns = ['num_ratings', 'avg_rating']
    
    rec_df = rec_df.merge(movie_stats, left_on='movie_id', right_index=True, how='left')
    rec_df['num_ratings'] = rec_df['num_ratings'].fillna(0)
    rec_df['avg_rating'] = rec_df['avg_rating'].fillna(0)
    
    # Step 4: Show recommendations
    print(f"\n🎬 RECOMMENDATIONS FOR YOU :")
    print("=" * 60)
    
    for i, (_, movie) in enumerate(rec_df.head(15).iterrows(), 1):
        year_color = "🟢" if movie['year'] >= 2024 else "🟡" if movie['year'] >= 2023 else "🔵"
        print(f"{i:2d}. {year_color} {movie['title']}")
        if movie['num_ratings'] > 0:
            print(f"     Rating: {movie['avg_rating']:.1f}/5 | Reviews: {int(movie['num_ratings'])}")
        else:
            print(f"     Rating: No ratings yet")
        print()
    
    print("=" * 60)
def main():
    while True:
        print("\n" + "="*50)
        print("🔍 CHOOSE RECOMMENDATION TYPE:")
        print("1. 🤖 User-Based (Collaborative)")
        print("2. 🎭 Find a movie")
        print("3. 🎯 Genre-Based")
        print("4. 📊 Trending Movies (Popularity)")
        print("5. 📈 Hybrid System (Combined)")
        print("6. ❌ Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            collaborative_simple()
        elif choice == '2':
            content_simple()
        elif choice == '3':
            genre_based()  
        elif choice == '4':
            popularity_based()
        elif choice == '5':
            hybrid_system()
        elif choice == '6':
            print("\n🎉 Thank you for using the Movie Recommendation System!")
            break
        else:
            print("❌ Invalid choice! Please enter 1-6.")
        

if __name__ == "__main__":
    main()
