import streamlit as st
import requests
from config import Config
import pandas as pd


def main():
    st.title('Reel Charts')

    st.sidebar.title('Charts')
    # Sidebar options
    selected_option = st.sidebar.selectbox("Select a chart",
                                           ["Home", "Box Office", "Upcoming Movies", "Popularity Chart"])

    def get_movies(filter_type, release_year=None, search_query=None):
        filters = {
            'Popular': 'popular',
            'Now Playing': 'now_playing',
            'Top Rated': 'top_rated',
            'Upcoming': 'upcoming'
        }

        if search_query:
            url = f"https://api.themoviedb.org/3/search/movie?language=en-US&query={search_query}&page=1"
        else:
            url = f"https://api.themoviedb.org/3/movie/{filters[filter_type]}?language=en-US&page=1"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {Config.API_KEY}"
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        return data['results']

    # home page filters
    if selected_option == 'Home':
        filter_type = st.radio('What movies would you like to see?',
                               ['Popular', 'Now Playing', 'Top Rated', 'Upcoming'])
        search_query = st.text_input("Search by movie title")

        # Clear release_year input if a search query is entered
        if search_query:
            release_year = None
        else:
            release_year = st.number_input("Filter by release year", min_value=1990, max_value=2023, step=1)

        movies = get_movies(filter_type, release_year, search_query)

        st.header('Popular Movies')

        columns = st.columns(3)

        # creates home page columns with movie posters
        for i, movie in enumerate(movies):
            with columns[i % 3]:
                poster_url = f'https://image.tmdb.org/t/p/w200{movie["poster_path"]}'
                st.image(poster_url, width=200)
                st.write(movie['title'])

    if selected_option == 'Popularity Chart':
        movies = get_movies('Popular')
        if movies:
            # Create horizontal bar chart
            movie_titles = [movie['title'] for movie in movies]
            movie_popularity = [movie['popularity'] for movie in movies]
            # Rescale popularity to a range of 1 to 10
            min_popularity = min(movie_popularity)
            max_popularity = max(movie_popularity)
            rescaled_popularity = [
                1 + (popularity - min_popularity) * 9 / (max_popularity - min_popularity)
                for popularity in movie_popularity
            ]
            chart_data = pd.DataFrame({'Movie': movie_titles, 'Popularity': rescaled_popularity})
            chart_data = chart_data.nlargest(10, 'Popularity')  # Limit to top 10 movies
            chart_data = chart_data.sort_values('Popularity', ascending=True)  # Sort in ascending order
            chart_data = chart_data[::-1]  # Reverse the order of rows
            st.header('Top 10 Current Movies by Popularity')

            # Display horizontal bar chart
            for index, row in chart_data.iterrows():
                movie_info = st.empty()
                popularity_bar = st.empty()
                popularity_text = st.empty()
                movie_info.text(f"{row['Movie']} ({row['Popularity']: .1f} / 10.0)")
                popularity_bar.progress(row['Popularity'] / 10.0)


if __name__ == '__main__':
    main()
