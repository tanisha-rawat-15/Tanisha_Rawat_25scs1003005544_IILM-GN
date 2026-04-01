import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import warnings
warnings.filterwarnings('ignore')

class CollaborativeFiltering:
    def __init__(self):
        self.movies = None
        self.ratings = None
        self.user_movie_matrix = None
        self.svd_model = None
        
    def load_data(self):
        """Load and prepare the movie data"""
        print("🎬 Loading MovieLens 100K dataset...")
        
        # Load movies data
        self.movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', 
                                usecols=[0,1], names=['movie_id', 'title'])
        
        # Load ratings data
        self.ratings = pd.read_csv('ml-100k/u.data', sep='\t',
                                 names=['user_id', 'movie_id', 'rating', 'timestamp'])
        
        print(f"✅ Loaded {len(self.movies)} movies and {len(self.ratings)} ratings")
        return self
    
    def create_user_item_matrix(self):
        """Create user-item rating matrix"""
        print("📊 Creating user-item matrix...")
        
        # Create pivot table: users as rows, movies as columns
        self.user_movie_matrix = self.ratings.pivot_table(
            index='user_id', 
            columns='movie_id', 
            values='rating',
            fill_value=0
        )
        
        print(f"✅ Matrix shape: {self.user_movie_matrix.shape}")
        return self
    
    def apply_svd(self, n_components=50):
        """Apply Singular Value Decomposition for dimensionality reduction"""
        print("🤖 Applying SVD for collaborative filtering...")
        
        self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
        self.user_factors = self.svd_model.fit_transform(self.user_movie_matrix)
        self.movie_factors = self.svd_model.components_
        
        print(f"✅ Explained variance: {self.svd_model.explained_variance_ratio_.sum():.2%}")
        return self
    
    def recommend_for_user(self, user_id, n_recommendations=10):
        """Generate recommendations for a specific user"""
        print(f"\n🎯 Generating recommendations for User #{user_id}...")
        
        # Get user's rated movies
        user_ratings = self.ratings[self.ratings['user_id'] == user_id]
        rated_movies = user_ratings['movie_id'].unique()
        
        # Calculate predicted ratings for all movies
        user_vector = self.user_factors[user_id - 1]  # user_id is 1-indexed
        predicted_ratings = np.dot(user_vector, self.movie_factors)
        
        # Create recommendations dataframe
        recommendations = pd.DataFrame({
            'movie_id': range(1, len(predicted_ratings) + 1),
            'predicted_rating': predicted_ratings
        })
        
        # Filter out already rated movies and join with movie titles
        recommendations = recommendations[~recommendations['movie_id'].isin(rated_movies)]
        recommendations = recommendations.merge(self.movies, on='movie_id')
        
        # Get top recommendations
        top_recommendations = recommendations.nlargest(n_recommendations, 'predicted_rating')
        
        print(f"\n📈 User #{user_id}'s Profile:")
        top_rated = user_ratings.nlargest(3, 'rating').merge(self.movies, on='movie_id')
        for _, movie in top_rated.iterrows():
            print(f"   👍 Loved: {movie['title']} (rated {movie['rating']}/5)")
        
        print(f"\n🎬 TOP {n_recommendations} RECOMMENDATIONS:")
        print("=" * 60)
        for i, (_, movie) in enumerate(top_recommendations.iterrows(), 1):
            print(f"{i:2d}. {movie['title']}")
            print(f"    Predicted Rating: {movie['predicted_rating']:.2f}")
        
        return top_recommendations

# Main execution
if __name__ == "__main__":
    # Initialize and run the collaborative filtering system
    cf = CollaborativeFiltering()
    cf.load_data()
    cf.create_user_item_matrix()
    cf.apply_svd(n_components=50)
    
    # Generate recommendations for different users
    for user_id in [1, 10, 20]:
        cf.recommend_for_user(user_id, n_recommendations=5)
        print("\n" + "="*60 + "\n")
