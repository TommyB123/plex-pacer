# Plex Pacer
Plex Pacer is a simple and somewhat jank script that can be used to organize the [One Pace](https://onepace.net) edit of the One Piece anime for your Plex library. It offers the ability to organize your files into season folders appropriately, apply respective metadata through the Plex API and also assign custom season posters.

Optional support for Onigashima Paced, another One Piece edit that currently fills in the gap for episodes of the Wano arc that the Pace team have yet to cover, is also available.

[Click here to download](https://github.com/TommyB123/plex-pacer/archive/refs/heads/main.zip)

# How to use
* Ensure the Python programming language is available on your system. If you don't have it, you can easily grab it through the [Microsoft Store](https://apps.microsoft.com/detail/9pnrbtzxmb4z)
* Install the Plex API library for Python. Enter `pip install plexapi` into your command prompt/terminal.
* Download the latest release [here](https://github.com/TommyB123/plex-pacer/archive/refs/heads/main.zip).
* Extract the zip file to a folder.
    * If you intend to use the script to organize your One Pace episodes, you must place the script files in a directory that contains either the episodes or a child directory with the episodes.
* Edit `config.json` with any text editor and fill out your Plex username and password alongside the name of the media server you will be creating your One Pace series entry on.
* Answer Y/N (yes/no) to each prompt as they appear. 

# Benefits of this script
* Very easy to update with new releases.
* Hardlinks files when organizing into season folders, avoiding needless file duplication while also keeping original downloads intact.
* Preserves original file names (Aside from the Dressrosa arc, whose batch is named differently from literally every other release. The Dressrosa episodes are renamed by the script to match the other One Pace releases. This is required because they will not be parsed in Plex properly otherwise.)
* Uses the Plex API to directly apply metadata to One Pace episode entries inside of Plex. This means that you can also use alternative One Pace-compatible edits like Muhn Pace if you're a dub watcher. Do note that this script is not written to organize other edits and can only apply metadata to edits that follow One Pace's episode structure. This also means that additional series parser plugins and etc not are needed.
* Does not apply the episode's release date to Plex. Since One Pace episodes are released in random orders, this ensures Plex doesn't try to play incorrect episodes when a season ends.

# Data sources
[Series Posters](https://imgur.com/a/one-pace-arc-wanted-posters-updated-2024-Dc5tTZN)

[Episode Titles](https://github.com/one-pace/one-pace-public-subtitles/blob/main/main/title.properties)

[Episode Descriptions](https://docs.google.com/spreadsheets/d/1M0Aa2p5x7NioaH9-u8FyHq6rH3t5s6Sccs8GoC6pHAM/)

[Onigashima Paced Episode Titles](https://docs.google.com/spreadsheets/d/1HoYogAchoU5DWxVJzUy3eZcHMZk_hUmzUVnQm9KxeFI/)
