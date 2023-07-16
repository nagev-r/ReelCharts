import streamlit as st
import requests
from config import Config


def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {Config.API_KEY}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['genres']


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
    selected_option = st.sidebar.selectbox("Select a chart", ["Home", "Box Office", "Upcoming Movies"])

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

        genres = get_selected_genres()
        movies = get_movies(filter_type, release_year, genres, search_query, vote_average_range)

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

        # creates home page columns with movie posters
        for i, movie in enumerate(movies):
            with columns[i % 3]:
                poster_url = f'https://image.tmdb.org/t/p/w200{movie["poster_path"]}'
                st.image(poster_url, width=200)
                st.write(movie['title'])


if __name__ == '__main__':
    main()
