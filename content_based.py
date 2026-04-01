import pandas as pd
import numpy as np


def content_advanced():
    """Advanced content-based with genre focus"""
    print("\n🎭 GENRE-BASED RECOMMENDATIONS")
    print("Loading data...")
    
    # Load full movie data with genres
    movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', 
                        header=None,
                        names=['movie_id', 'title'] + [f'genre_{i}' for i in range(19)])
    
    ratings = pd.read_csv('ml-100k/u.data', sep='\t',
                         names=['user_id', 'movie_id', 'rating', 'timestamp'])
    
    # Genre names
    genre_names = [
        'Unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy',
        'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
        'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
    ]
    
    # Show available genres
    print("\n🎯 AVAILABLE GENRES:")
    for i, genre in enumerate(genre_names[1:], 1):  # Skip 'Unknown'
        print(f"{i}. {genre}")
    
    # Get genre choice
    try:
        genre_choice = int(input("\n🔍 Choose a genre (1-18): "))
        if genre_choice < 1 or genre_choice > 18:
            print("❌ Please enter a number between 1-18")
            return
    except:
        print("❌ Please enter a valid number!")
        return
    
    selected_genre = genre_names[genre_choice]
    print(f"\n🎬 Searching for {selected_genre} movies...")
    
    # Find movies with the selected genre
    genre_column = f'genre_{genre_choice-1}'  # Adjust for 0-based indexing
    genre_movies = movies[movies[genre_column] == 1]
    
    print(f"Found {len(genre_movies)} movies in {selected_genre} genre")
    
    # Get movie ratings (if they exist)
    movie_stats = ratings.groupby('movie_id').agg({
        'rating': ['count', 'mean']
    }).round(3)
    movie_stats.columns = ['num_ratings', 'avg_rating']
    
    # Combine with genre movies (use left join to keep all movies)
    genre_movies_with_stats = genre_movies.merge(
        movie_stats, left_on='movie_id', right_index=True, how='left'
    )
    
    # Fill NaN values for movies with no ratings
    genre_movies_with_stats['num_ratings'] = genre_movies_with_stats['num_ratings'].fillna(0)
    genre_movies_with_stats['avg_rating'] = genre_movies_with_stats['avg_rating'].fillna(0)
    
    # Show ALL movies in the genre, sorted by year (newest first)
    print(f"\n🔥 ALL {selected_genre.upper()} MOVIES:")
    print("=" * 60)
    
    # Separate new and classic movies
    new_movies = []
    classic_movies = []
    
    for i, (_, movie) in enumerate(genre_movies_with_stats.iterrows(), 1):
        raw_title = movie['title']
        rating = movie['avg_rating']
        reviews = int(movie['num_ratings'])
        
        # Clean the title - extract from URL
        title = raw_title
        if 'title-exact?' in raw_title:
            # Extract clean title from URL
            try:
                title_part = raw_title.split('title-exact?')[-1]
                title = title_part.split(')')[0] + ')'  # Get everything before closing parenthesis
                title = title.replace('%20', ' ')  # Replace URL spaces
            except:
                title = raw_title  # Fallback to original
        
        # Extract year from title
        year = 0
        if '(' in title and ')' in title:
            try:
                year_str = title.split('(')[-1].split(')')[0]
                year = int(year_str) if year_str.isdigit() else 0
            except:
                year = 0
        
        movie_data = (title, rating, reviews, year, i)
        
        # Check if it's a new movie (2000 or later)
        if year >= 2000:
            new_movies.append(movie_data)
        else:
            classic_movies.append(movie_data)
    
    # Sort new movies by year (newest first)
    new_movies.sort(key=lambda x: x[3], reverse=True)
    
    # Show new movies first
    if new_movies:
        print(f"\n🎉 NEW {selected_genre.upper()} MOVIES (2000+):")
        print("-" * 50)
        for title, rating, reviews, year, orig_idx in new_movies:
            rating_display = f"{rating}/5" if rating > 0 else "No ratings"
            reviews_display = f"{reviews} reviews" if reviews > 0 else "No reviews"
            print(f"{orig_idx:2d}. {title}")
            print(f"    {rating_display} | {reviews_display}")
    
    # Then show classics
    if classic_movies:
        print(f"\n🏛️  CLASSIC {selected_genre.upper()} MOVIES:")
        print("-" * 50)
        for title, rating, reviews, year, orig_idx in classic_movies[:10]:  # Show top 10 classics
            rating_display = f"{rating}/5" if rating > 0 else "No ratings"
            reviews_display = f"{reviews} reviews" if reviews > 0 else "No reviews"
            print(f"{orig_idx:2d}. {title}")
            print(f"    {rating_display} | {reviews_display}")
