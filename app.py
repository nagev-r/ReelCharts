import streamlit as st
import requests
import pandas as pd  # Gio to implente tables feature
import numpy as np
from config import Config
import pandas as pd


def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {Config.API_KEY}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['genres']


def get_box_office(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {Config.API_KEY}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data.get('revenue', 0)


def get_movies(filter_type, release_year=None, genres=None, search_query=None, vote_average_range=None):
    filters = {
        'Popular': 'popular',
        'Now Playing': 'now_playing',
        'Top Rated': 'top_rated',
        'Upcoming': 'upcoming'
    }

    genre_ids = [genre['id'] for genre in genres] if genres else None
    genre_query = f'&with_genres={",".join(str(id) for id in genre_ids)}' if genre_ids else ''

    if search_query:
        url = f"https://api.themoviedb.org/3/search/movie?language=en-US&query={search_query}&page=1"
    else:
        url = f"https://api.themoviedb.org/3/movie/{filters[filter_type]}?language=en-US&page=1{genre_query}"
        if release_year:
            url += f"&year={release_year}"  # Add release year as a filter
        if vote_average_range:
            url += f"&vote_average.gte={vote_average_range[0]}&vote_average.lte={vote_average_range[1]}"  # Add vote average range as a filter

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {Config.API_KEY}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    return data['results']


def main():
    st.title('Reel Charts')

    st.sidebar.title('Charts')
    # Sidebar options
    selected_option = st.sidebar.selectbox("Select a chart",
                                           ["Home", "Movie Table", "Popularity Chart", "Box Office Line Graph", "Map"])

    def get_selected_genres():
        all_genres = get_genres()
        genre_names = [genre['name'] for genre in all_genres]
        selected_genres = st.sidebar.multiselect('Select Genres', genre_names)
        selected_genre_ids = [genre['id'] for genre in all_genres if genre['name'] in selected_genres]
        selected_genres = [{'id': genre_id, 'name': genre_name} for genre_id, genre_name in
                           zip(selected_genre_ids, selected_genres)]
        return selected_genres

    # home page filters
    if selected_option == 'Home':
        filter_type = st.radio('What movies would you like to see?',
                               ['Popular', 'Now Playing', 'Top Rated', 'Upcoming'])
        search_query = st.text_input("Search by movie title")
        release_year = st.number_input("Filter by release year", min_value=1990, max_value=2023, step=1,
                                       value=2023)  # Set default value to 2023
        vote_average_range = st.slider("Filter by vote average range", min_value=0.0, max_value=10.0,
                                       value=(0.0, 10.0), step=0.1)  # Slider widget for vote average range

        # Dynamically change the header based on the selected filter type
        header_text = filter_type + " Movies"
        st.header(header_text)

        # Clear Filters button
        if st.button("Clear Filters"):
            search_query = None
            release_year = 2023
            vote_average_range = (0.0, 10.0)
            genres = None

        columns = st.columns(3)
        genres = get_selected_genres()

        movies = get_movies(filter_type, release_year, genres, search_query, vote_average_range)

        # creates home page columns with movie posters
        for i, movie in enumerate(movies):
            with columns[i % 3]:
                poster_url = f'https://image.tmdb.org/t/p/w200{movie["poster_path"]}'
                st.image(poster_url, width=200)
                st.write(movie['title'])

    # Zach Code Start
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

    if selected_option == 'Box Office Line Graph':
        if selected_option == 'Box Office Line Graph':
            st.header('Box Office Income for 5 Movies (Month of July)')
            st.write(
                'Movies: Spider-Man: Across the Spider-Verse, Elemental, Transformers: Rise of the Beasts, Guardians of the Galaxy Vol. 3, Indiana Jones and the Dial of Destiny')

            # Simulated box office data for the 5 movies for the last month
            # Replace these with actual box office incomes or data fetching logic
            movie_incomes = [
                [340377908, 357678700, 368800269, 375209269],  # Movie 1 weekly incomes
                [89607297, 109624302, 125688508, 137157319],  # Movie 2 weekly incomes
                [136463958, 146829334, 152785930, 155664410],  # Movie 3 weekly incomes
                [355096603, 357570077, 358488599, 358826794],  # Movie 4 weekly incomes
                [60368101, 122126405, 145628290, 158997363],  # Movie 5 weekly incomes
            ]

            # Weekly intervals for the last month
            weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']

            movie_titles = ['Spider-Man: Across the Spider-Verse', 'Elemental', 'Transformers: Rise of the Beasts',
                            'Guardians of the Galaxy Vol. 3', 'Indiana Jones and the Dial of Destiny']

            # Create a dataframe for the line chart
            data = pd.DataFrame({
                'Week': weeks,
                **{title: incomes for title, incomes in zip(movie_titles, movie_incomes)}
            })

            # Set the 'Week' column as the index for the dataframe
            data.set_index('Week', inplace=True)

            # Display the line chart using Streamlit
            st.line_chart(data)
    # Zach Code End

    # Gio code start
    if selected_option == "Movie Table":

        # Movie seach name table
        st.title("TMDB Movie Search")

        TMDB_URL = "https://api.themoviedb.org/3/search/movie"
        API_KEY = "9bc1882d52cb1a350bd25fb47aa8ff26"

        def fetch_movies(query):
            params = {
                'api_key': API_KEY,
                'query': query
            }

            response = requests.get(TMDB_URL, params=params)
            data = response.json()

            if data and 'results' in data:
                return data['results']
            else:
                return []

        query = st.text_input("Enter movie name:", value='').strip()

        if query:
            movies = fetch_movies(query)

            if movies:
                # Convert the results into a pandas DataFrame for display
                df = pd.DataFrame(movies)
                st.write(df[["title", "release_date", "overview", "popularity", "vote_average"]])
                st.success(f'Data results for "{query}" ✅')
            else:
                ##t.write("No movies found!")
                st.error(f'No movies found for "{query}" 🚨')

                ##COMPLETE

        # Gio Code end

    # Nageline Code
    if selected_option == "Map":
        # Load_data utilizes location points for specific provider chosen
        # and returns values to map data points to be displayed
        def load_data(provider):
            data = {
                'Netflix': {'lat': 34.0522, 'lon': -118.2437},
                'Apple TV': {'lat': 37.3318, 'lon': -122.0312},
                'Amazon Prime Video': {'lat': 47.6062, 'lon': -122.3321},
                'Hulu': {'lat': 34.0522, 'lon': -118.2437},
                'Max': {'lat': 40.7128, 'lon': -74.0060},
            }
            return pd.DataFrame([data[provider]])

        st.title("Streaming Provider Headquarters Map")

        # List of top available streaming providers
        providers = ['Netflix', 'Apple TV', 'Amazon Prime Video', 'Hulu', 'Max']

        # User selection via selectbox
        selected_provider = st.selectbox("Select a streaming provider to view their headquarters:", providers)

        # Load data for the selected provider
        data = load_data(selected_provider)

        # Display the map with the selected provider's headquarters using streamlit
        st.map(data=data, zoom=12)

    # End Code


if __name__ == '__main__':
    main()
