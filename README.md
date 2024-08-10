# HiAnime to MyAnimeList Transfer Tool

This project provides a web interface to automate the transfer of anime lists from HiAnime.to to MyAnimeList.net. The tool helps users connect their MyAnimeList.net account and import their anime list from HiAnime.to with just a few clicks.

## Features

- **OAuth Integration**: Connect to MyAnimeList.net using OAuth for secure authentication.
- **HiAnime Cookie Import**: Guide users to extract and input their `connect.sid` cookie from HiAnime.to.
- **Automated Transfer**: Automates the process of transferring anime entries from HiAnime.to to MyAnimeList.net.

## Prerequisites

- **Django**: Ensure you have Django installed to run the server.
- **Static Files**: The necessary CSS is included in the `static` folder.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/abdbbdii/hianime-to-myanimelist.git
   cd hianime-to-myanimelist
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory of your project:
     ```bash
     code .env
     ```
   - Open the `.env` file and add the following variables:
     ```env
     DJANGO_SECRET_KEY=your_django_secret_key
     MAL_CLIENT_ID=your_mal_client_id
     MAL_CLIENT_SECRET=your_mal_client_secret
     DATABASE_URL=your_database_url
     ```
   - Replace `your_django_secret_key`, `your_mal_client_id`, `your_mal_client_secret`, and `your_database_url` with your actual values.

4. Run the Django server:
   ```bash
   python manage.py runserver
   ```

5. Access the application in your browser at `http://127.0.0.1:8000/`.

## Usage

### Step 1: Connect to MyAnimeList.net
- Click the "Connect MyAnimeList.net" button to authenticate via OAuth.
- The status will update to "Connected" upon successful authentication.

### Step 2: Import HiAnime Cookie
- Follow the instructions provided to extract your `connect.sid` cookie from HiAnime.to.
- Paste the cookie into the provided input field.

### Step 3: Transfer Your Anime List
- Click the "Transfer" button to start the process.
- The status will update as the transfer progresses.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you find any bugs or have suggestions for new features. Suggestions for supporting additional anime platforms are also appreciated.