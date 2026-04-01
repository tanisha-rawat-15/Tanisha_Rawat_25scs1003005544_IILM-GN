import pandas as pd
import numpy as np

def genre_based():
    """Genre-based movie recommendations"""
    print("\n🎯 GENRE-BASED RECOMMENDATIONS")
    
    # Load movies with genres
    movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', 
                        names=['movie_id', 'title', 'release_date', 'video_release', 'imdb_url',
                              'unknown', 'action', 'adventure', 'animation', 'childrens', 'comedy',
                              'crime', 'documentary', 'drama', 'fantasy', 'film_noir', 'horror',
                              'musical', 'mystery', 'romance', 'sci_fi', 'thriller', 'war', 'western'])
    
    ratings = pd.read_csv('ml-100k/u.data', sep='\t',
                         names=['user_id', 'movie_id', 'rating', 'timestamp'])
    
    # Genre mapping
    genres = {
        1: "Action", 2: "Adventure", 3: "Animation", 4: "Children's", 
        5: "Comedy", 6: "Crime", 7: "Documentary", 8: "Drama", 
        9: "Fantasy", 10: "Film-Noir", 11: "Horror", 12: "Musical",
        13: "Mystery", 14: "Romance", 15: "Sci-Fi", 16: "Thriller",
        17: "War", 18: "Western"
    }
    
    print("\n🎭 AVAILABLE GENRES:")
    print("=" * 30)
    for i, (genre_id, genre_name) in enumerate(genres.items(), 1):
        print(f"{i:2d}. {genre_name}")
    
    try:
        choice = int(input("\n🎯 Select genre (1-18): "))
        if choice < 1 or choice > 18:
            print("❌ Please select a valid genre (1-18)")
            return
        
        selected_genre_id = choice
        selected_genre_name = genres[selected_genre_id]
        
        # Get the correct column name for the selected genre
        genre_columns = ['unknown', 'action', 'adventure', 'animation', 'childrens', 'comedy',
                        'crime', 'documentary', 'drama', 'fantasy', 'film_noir', 'horror',
                        'musical', 'mystery', 'romance', 'sci_fi', 'thriller', 'war', 'western']
        
        genre_col_name = genre_columns[selected_genre_id]
        
        # Filter movies that have this genre set to 1
        genre_movies = movies[movies[genre_col_name] == 1]
        
        if len(genre_movies) == 0:
            print(f"❌ No movies found in {selected_genre_name} genre")
            return
        
        print(f"\n✅ Found {len(genre_movies)} movies in {selected_genre_name} genre")
        
        # Get ratings data
        movie_stats = ratings.groupby('movie_id').agg({
            'rating': ['count', 'mean']
        }).round(3)
        movie_stats.columns = ['num_ratings', 'avg_rating']
        
        # Merge with genre movies
        genre_movies_with_ratings = genre_movies.merge(
            movie_stats, left_on='movie_id', right_index=True, how='left'
        )
        
        # Fill NaN values
        genre_movies_with_ratings['num_ratings'] = genre_movies_with_ratings['num_ratings'].fillna(0)
        genre_movies_with_ratings['avg_rating'] = genre_movies_with_ratings['avg_rating'].fillna(0)
        
        # Separate movies with and without ratings
        rated_movies = genre_movies_with_ratings[genre_movies_with_ratings['num_ratings'] > 0]
        unrated_movies = genre_movies_with_ratings[genre_movies_with_ratings['num_ratings'] == 0]
        
        print(f"\n🎬 TOP {selected_genre_name.upper()} MOVIES:")
        print("=" * 60)
        
        if len(rated_movies) > 0:
            # Sort by rating and number of reviews
            top_movies = rated_movies.sort_values(['avg_rating', 'num_ratings'], ascending=[False, False])
            
            for i, (_, movie) in enumerate(top_movies.head(15).iterrows(), 1):
                print(f"{i:2d}. {movie['title']}")
                print(f"    Rating: {movie['avg_rating']:.1f}/5 | Reviews: {int(movie['num_ratings'])}")
        else:
            print("No rated movies found in this genre")
        
        # Show unrated movies if any
        if len(unrated_movies) > 0:
            print(f"\n📝 OTHER {selected_genre_name.upper()} MOVIES (NO RATINGS YET):")
            print("-" * 50)
            for i, (_, movie) in enumerate(unrated_movies.head(10).iterrows(), 1):
                print(f"{i:2d}. {movie['title']} (No ratings yet)")
        
        print("=" * 60)
        
    except ValueError:
        print("❌ Please enter a valid number")
    except Exception as e:
        print(f"❌ Error: {e}")
