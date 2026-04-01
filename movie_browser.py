import pandas as pd

def browse_movies():
    """Show available movies to help with searching"""
    print("🎬 MOVIE DATABASE BROWSER")
    print("=" * 50)
    
    # Load movies
    movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', 
                        usecols=[0,1], names=['movie_id', 'title'])
    
    print(f"Total movies in database: {len(movies)}")
    
    while True:
        print("\n🔍 Search options:")
        print("1. Show all movies (first 50)")
        print("2. Search by title")
        print("3. Show popular movies")
        print("4. Exit browser")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            print("\n📝 First 50 movies:")
            for i, (_, movie) in enumerate(movies.head(50).iterrows(), 1):
                print(f"{i:2d}. {movie['title']}")
                
        elif choice == '2':
            search_term = input("Enter search term: ").strip().lower()
            if search_term:
                matches = movies[movies['title'].str.lower().str.contains(search_term, na=False)]
                print(f"\n🔍 Found {len(matches)} movies:")
                for i, (_, movie) in enumerate(matches.head(20).iterrows(), 1):
                    print(f"{i:2d}. {movie['title']}")
                if len(matches) > 20:
                    print(f"... and {len(matches) - 20} more")
            else:
                print("❌ Please enter a search term")
                
        elif choice == '3':
            # Load ratings to find popular movies
            ratings = pd.read_csv('ml-100k/u.data', sep='\t',
                                names=['user_id', 'movie_id', 'rating', 'timestamp'])
            
            # Get movies with most ratings
            popular_movies = ratings.groupby('movie_id').size().nlargest(20)
            popular_movies = popular_movies.reset_index().merge(movies, on='movie_id')
            
            print("\n🔥 Most rated movies:")
            for i, (_, movie) in enumerate(popular_movies.iterrows(), 1):
                rating_count = ratings[ratings['movie_id'] == movie['movie_id']].shape[0]
                print(f"{i:2d}. {movie['title']} ({rating_count} ratings)")
                
        elif choice == '4':
            print("👋 Returning to main menu...")
            break
            
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    browse_movies()
