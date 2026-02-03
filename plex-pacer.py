import os
import json
import re
from pathlib import Path
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.video import Show, Episode

with open('episodes.json', encoding="utf-8") as f:
    series_data = json.load(f)

with open('config.json') as f:
    plex_data = json.load(f)

with open('onigashima.json') as f:
    onigashima_data = json.load(f)

PACE_SERIES_NAME = 'One Pace'

# your plex username or email
PLEX_LOGIN = plex_data['plex_username']

# your plex password
PLEX_PASSWORD = plex_data['plex_password']

# the name of your plex media server
PLEX_SERVER_NAME = plex_data['plex_server_name']

# variables for suppelementing the incomplete Wano arc with the Onigashima Paced edit alongside One Pace proper
ONIGASHIMA_START = 23
ONIGASHIMA_END = 48
WANO_SEASON_NUMBER = 35

# global variables for plex data and etc
plex_account: MyPlexAccount = None
plex_server: PlexServer = None
pace_series: Show = None
dry_run: bool = False

pace_seasons = [
    'Romance Dawn',  # Season 1
    'Orange Town',  # Season 2
    'Syrup Village',  # Season 3
    'Gaimon',  # Season 4
    'Baratie',  # Season 5
    'Arlong Park',  # Season 6
    'The Adventures of Buggy\'s Crew',  # Season 7
    'Loguetown',  # Season 8
    'Reverse Mountain',  # Season 9
    ('Whiskey Peak', 'Whisky Peak'),  # Season 10
    'The Trials of Koby-Meppo',  # Season 11
    'Little Garden',  # Season 12
    'Drum Island',  # Season 13
    ('Arabasta', 'Alabasta'),  # Season 14
    'Jaya',  # Season 15
    'Skypiea',  # Season 16
    'Long Ring Long Land',  # Season 17
    'Water Seven',  # Season 18
    'Enies Lobby',  # Season 19
    'Post-Enies Lobby',  # Season 20
    'Thriller Bark',  # Season 21
    'Sabaody Archipelago',  # Season 22
    'Amazon Lily',  # Season 23
    'Impel Down',  # Season 24
    'The Adventures of the Straw Hats',  # Season 25
    'Marineford',  # Season 26
    'Post-War',  # Season 27
    'Return to Sabaody',  # Season 28
    'Fishman Island',  # Season 29
    'Punk Hazard',  # Season 30
    'Dressrosa',  # Season 31
    'Zou',  # Season 32
    'Whole Cake Island',  # Season 33
    'Reverie',  # Season 34
    'Wano',  # Season 35
    'Egghead',  # Season 36
]

# special dict for dressrosa episodes because they're named differently from literally every other arc and incompatible with plex by default
dressrosa_episodes = {
    "700-701": "01",
    "702-703": "02",
    "704-705": "03",
    "706-707": "04",
    "708-709": "05",
    "710-711": "06",
    "712-713": "07",
    "714-715": "08",
    "716-717": "09",
    "718-719": "10",
    "720-721": "11",
    "722-723": "12",
    "724-725": "13",
    "726-727": "14",
    "728-729": "15",
    "730-731": "16",
    "732-733": "17",
    "734-735": "18",
    "736-737": "19",
    "738-739": "20",
    "740-741": "21",
    "742-743": "22",
    "744-745": "23",
    "746-747": "24",
    "748-749": "25",
    "750-751": "26",
    "752-753": "27",
    "754-755": "28",
    "756-757": "29",
    "758-759": "30",
    "760-761": "31",
    "762-763": "32",
    "764-765": "33",
    "766-767": "34",
    "768-769": "35",
    "770-771": "36",
    "772-773": "37",
    "774-775": "38",
    "776-778": "39",
    "779-781": "40",
    "782-783": "41",
    "784-785": "42",
    "786-787": "43",
    "788-790": "44",
    "791-793": "45",
    "794-795": "46",
    "796-797": "47",
    "798-800": "48",
}


def get_pace_episode_metadata(season: int, episode: int):
    season_name = pace_seasons[season - 1]
    if isinstance(season_name, tuple):
        season_name = season_name[0]  # use the og/outdated season names because that's what's in our episodes.json file

    episode_index = episode - 1
    season = series_data.get(season_name)
    if season is None:
        return None
    else:
        if episode_index < len(season):
            return season[episode_index]
        else:
            # skip episode that's > than the current One Pace edits.
            # this shouldn't happen outside of cases where users have added other One Piece edits to the series.
            return None


def main():
    ask_dry_run()
    organize_files()
    apply_plex_metadata()

    if dry_run is False:
        apply_plex_posters()

    ask_extra_edits()
    extra_edit_plex_metadata()


def ask_dry_run():
    confirm = input('Would you like to do a dry run? No files or Plex metadata will be modified.\nY/N\n')
    if confirm.lower() == 'y':
        global dry_run
        dry_run = True


def organize_files():
    # prompt user to scan for pace episodes
    confirm = input('Scan for and organize One Pace episodes?\nY/N\n')
    if confirm.lower() != 'y':
        return

    PACE_PATH = None
    cwd = os.path.basename(os.getcwd())
    if cwd == PACE_SERIES_NAME:
        PACE_PATH = '.'

    files_moved = 0
    # organize files first
    for path, dirs, files in os.walk('.'):
        if path == 'One Pace' or path.find('Season') != -1:  # skip over one pace or season folders
            continue

        for file in files:
            if not file.endswith(('.mkv', '.mp4')):  # skip over non-video files
                continue

            season_index = 0
            for season in pace_seasons:
                if season == 'Dressrosa' and file.find('Dressrosa') == -1:  # bless this arc's batch torrent for having a different naming scheme from all the others
                    match = re.match(r'\[One Pace] Chapter ([-0-9]*) \[720p](\[.*])', file)
                    if match is not None and file.find('Chapter') != -1:
                        episode_number = dressrosa_episodes.get(match.group(1))
                        final_name = f'[One Pace][{match.group(1)}] Dressrosa {episode_number} [720p]{match.group(2)}.mkv'
                        print(f'Renaming Dressrosa episode from {file} to {final_name}')
                else:
                    if isinstance(season, tuple):
                        for subseason in season:
                            match = re.match(fr'\[One Pace\].* {subseason} [0-9]*', file)
                    else:
                        match = re.match(fr'\[One Pace\].* {season} [0-9]*', file)
                    final_name = file

                if match is None:
                    season_index += 1
                    continue

                if file.endswith('.mkv') and season in ['The Adventures of Buggy\'s Crew', 'The Trials of Koby-Meppo', 'The Adventures of the Straw Hats']:
                    # rename cover story special MKVs because their files don't have episode numbers, but the streamable MP4s do
                    final_name = final_name.replace(season, f'{season} 01')

                # prepare directories
                if PACE_PATH is None:
                    if os.path.exists(PACE_SERIES_NAME) is False:
                        print('creating root series directory for One Pace')
                        if dry_run is False:
                            os.makedirs(PACE_SERIES_NAME)

                PACE_PATH = PACE_SERIES_NAME

                season_number = season_index + 1
                season_path = f'Season {season_number:02d}'

                if os.path.exists(f'{PACE_PATH}/{season_path}') is False:
                    print(f'creating season folder for season {season_number}')
                    if dry_run is False:
                        os.makedirs(f'{PACE_PATH}/{season_path}')

                final_file = Path(f'{PACE_PATH}/{season_path}/{final_name}')
                if os.path.exists(final_file):
                    # quietly skip over already existing episodes
                    continue

                # copy (hardlink) episode to its final destination
                print(f'copying {file} to {season_path}')
                if dry_run is False:
                    os.link(f'{path}/{file}', final_file)

                files_moved += 1
                season_index += 1
                break

    print(f'{files_moved} episode(s) have been moved to their appropriate folders.')
    print('Please copy these files to your Plex series folder before attempting to apply metadata.\n')


def apply_plex_metadata():
    confirm = input('Would you like to apply One Pace episode metadata to Plex? Please only proceed when you\'ve moved the edited episodes and verified they\'re present in your media server.\nY/N\n')
    if confirm.lower() != 'y':
        return

    if plex_auth() is False:
        return

    print('Successfully found One Pace series. Searching for episodes to apply metadata to.')
    episodes_changed = 0
    episodes: Episode = pace_series.episodes()
    for episode in episodes:
        metadata = get_pace_episode_metadata(episode.seasonNumber, episode.episodeNumber)
        if metadata is None:
            print(f'Could not find any One Pace metadata for {episode.seasonEpisode.upper()}')
            continue

        changed = False
        if episode.title != metadata['title']:
            if dry_run is False:
                episode.editTitle(metadata['title'])
                episode.editSortTitle(metadata['title'])

            print(f"Applied episode title to {episode.seasonEpisode.upper()} ({metadata['title']})")
            changed = True

        new_summary = f'{metadata['summary']}\nManga Chapters: {metadata['chapters']}\nEdited Episodes: {metadata['episodes']}'
        if episode.summary != new_summary:
            if dry_run is False:
                episode.editSummary(new_summary)

            print(f"Applied episode summary to {episode.seasonEpisode.upper()}")
            changed = True

        if changed is True:
            episodes_changed += 1

    print(f'Applied metadata to {episodes_changed} One Pace episodes.')


def apply_plex_posters():
    confirm = input('Would you like to apply custom posters and backgrounds to the One Pace series and its seasons? This is strongly recommended as they\'ll be blank otherwise and you\'ll need to update them manually.\nY/N\n')
    if confirm.lower() != 'y':
        return

    if plex_auth() is False:
        return

    if os.path.exists('assets/series_poster.png') is True:
        pace_series.uploadPoster(filepath='assets/series_poster.png')
        print('Applied series poster to One Pace')

    if os.path.exists('assets/background.jpg') is True:
        pace_series.uploadArt(filepath='assets/background.jpg')
        print('Applied background to One Pace')

    for season in pace_series.seasons():
        if os.path.exists(f'assets/posters/{season.index:02d}.png') is True:
            season.uploadPoster(filepath=f'assets/posters/{season.index:02d}.png')
            print(f'Applied poster to Season {season.index:02d}')


def ask_extra_edits():
    confirm = input('OPTIONAL: Would you like to organize Onagashima Paced? Select N if you don\'t have it.\nY/N\n')
    if confirm.lower() != 'y':
        return

    current_wano_length = len(series_data['Wano'])
    print('Since Onigashima Paced is another edit that will be placed alongside One Pace episodes, the episode numbering won\'t line up.')
    print('In order to fix this, we\'ll be renumbering the episode files. Pick an episode number to begin the renumbering at.')
    print('I recommend whatever the latest One Pace Wano episode is and adding 10 to it. This leaves plenty of wiggle room for episode length deviation between edits.')
    print(f'One Pace Wano currently has {current_wano_length} episodes.')
    print('NOTE: The script assumes you aren\'t using Onigashima Paced episodes that have been made obsolete by One Pace proper.')
    while True:
        try:
            new_episode_start = int(input('Choice: '))
        except Exception:
            print('Could not parse your input as an integer.')
            continue

        if new_episode_start < current_wano_length:
            print('You can\t start Onigashima Paced episodes with an episode number less than the current Wano episodes.')
            continue

        break

    episodes = []
    for path, dirs, files in os.walk('.'):
        if path == 'One Pace' or path.find('Season') != -1:  # skip over One Pace series and season folders
            continue

        for file in files:
            if file.endswith('.mp4') is False:  # skip over non-mp4 files
                continue

            if file.find('End of Wano') != -1:  # no regex needed for the end of wano episodes at this point
                episodes.append((path, file))
                continue

            match = re.match(r'\[[-0-9]*] (?:Onigashima|Onigashima\+) ([0-9]*) - .*.mp4', file)
            if match is not None:
                if int(match.group(1)) >= ONIGASHIMA_START:
                    episodes.append((path, file))

    if len(episodes) == 0:
        print('No Wano episodes found')
        return

    print(f'Found {len(episodes)} suitable Onigashima Paced episodes. Now organizing files.')
    episodes.sort()

    # create series folder if it doesn't exist
    if os.path.exists(PACE_SERIES_NAME) is False:
        print('creating root series directory for One Pace')
        if dry_run is False:
            os.makedirs(PACE_SERIES_NAME)

    # create season folder if it doesn't exist
    season_path = f'Season {WANO_SEASON_NUMBER:02d}'
    if os.path.exists(f'{PACE_SERIES_NAME}/{season_path}') is False:
        print(f'creating season folder for season {WANO_SEASON_NUMBER:02d}')
        if dry_run is False:
            os.makedirs(f'{PACE_SERIES_NAME}/{season_path}')

    # finally organize the files
    for path, name in episodes:
        match = re.match(r'\[[-0-9]*] (?:Onigashima|Onigashima\+|End of Wano) ([0-9]*) - .*.mp4', name)
        original_ep_number = int(match.group(1))
        if name.find('End of Wano') != -1:
            new_episode_number = (ONIGASHIMA_END - ONIGASHIMA_START + original_ep_number) + new_episode_start
        else:
            new_episode_number = (original_ep_number - ONIGASHIMA_START) + new_episode_start

        new_name = name.replace(match.group(1), f'{new_episode_number} ({original_ep_number})')
        final_file = f'{PACE_SERIES_NAME}/{season_path}/{new_name}'

        if os.path.exists(final_file) is True:
            continue  # quietly skip over existing files

        print(f'copying {new_name} to {season_path}')
        if dry_run is False:
            os.link(f'{path}/{name}', final_file)


def extra_edit_plex_metadata():
    confirm = input('OPTIONAL: Would you like to apply Onigashima Paced episode metadata to Plex? Please only proceed when you\'ve moved the edited episodes and verified they\'re present in your media server.\nY/N\n')
    if confirm.lower() != 'y':
        return

    if plex_auth() is False:
        return

    print('Successfully found One Pace series.')

    # try to find the season 35 (Wano)
    print('Attempting to fetch Wano season folder')
    for season in pace_series.seasons():
        if season.index == WANO_SEASON_NUMBER:
            wano_season = season
            break

    if wano_season is None:
        print('Could not find the Wano arc. Please ensure it\'s present in your Plex instance under Season 35')
        return

    episodes = wano_season.episodes()
    if len(episodes) <= len(series_data['Wano']):
        print('Could not find any episodes beyond One Pace\'s Wano episodes.')
        return

    print('Successfully fetched Wano season folder. Searching for Onigashima Paced episodes to apply metadata to.')
    onigashima_episodes = []
    for episode in episodes:
        if episode.episodeNumber > len(series_data['Wano']):  # assume it's an Onigashima Paced episode
            onigashima_episodes.append(episode)

    episodes_changed = 0
    for i in range(len(onigashima_episodes)):
        new_title = onigashima_data[i]
        episode = onigashima_episodes[i]

        changed = False
        if episode.title != new_title:
            if dry_run is False:
                episode.editTitle(new_title)
                episode.editSortTitle(new_title)

            print(f"Applied episode title to {episode.seasonEpisode.upper()} ({new_title})")
            changed = True

        if changed is True:
            episodes_changed += 1

    print(f'Applied metadata to {episodes_changed} Onigashima Paced episodes.')


def plex_auth():
    global plex_account
    if plex_account is None:
        print('Attempting to authenticate with Plex using the credentials provided.')
        plex_account = MyPlexAccount(PLEX_LOGIN, PLEX_PASSWORD)
        if plex_account is None:
            print('Failed to authenticate with Plex.')
            return False

    global plex_server
    if plex_server is None:
        print(f'Successfully authenticated with Plex. Now attempting to connect to media server ({PLEX_SERVER_NAME})')
        plex_server = plex_account.resource(PLEX_SERVER_NAME).connect()
        if plex_server is None:
            print(f'Failed to connected to the media server ({PLEX_SERVER_NAME})')
            return False

    global pace_series
    if pace_series is None:
        print('Searching for One Pace TV series')
        pace_series = plex_server.search('One Pace', 'show')[0]
        if pace_series is None:
            print('Unable to find One Pace TV series. Pleae add it to your plex library and populate it with Pace episodes.')
            return False

    return True


main()
