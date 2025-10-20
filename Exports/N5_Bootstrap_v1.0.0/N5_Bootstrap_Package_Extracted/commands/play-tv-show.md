---
date: '2025-10-09T04:12:00Z'
last-tested: '2025-10-09T04:12:00Z'
generated_date: '2025-10-09T04:12:00Z'
checksum: play_tv_show_v1_0_0
tags: [media, streaming, entertainment, tv, url-generation]
category: productivity
priority: low
related_files: []
anchors:
  input: null
  output: /home/workspace/N5/commands/play-tv-show.md
---
# `play-tv-show`

Version: 1.0.0

Summary: Generate a direct link to play a TV show episode on the Zo Stream service

Workflow: misc

Tags: media, streaming, tv-shows, url-generation

## Purpose
Generate a direct playback link for TV show episodes using The Movie Database (TMDB) ID and the Zo Stream service.

## Inputs
- --tmdbId : integer (required) — The Movie Database ID for the TV show
- --season : integer (required) — Season number
- --episode : integer (required) — Episode number
- --subtitle_language : string (optional) — Two-letter ISO 639-1 language code (e.g., 'en', 'es', 'fr')

## Outputs
- playback_url : string — Direct clickable URL to play the episode
- episode_info : text — Show title, season, episode, and metadata (if available)

## Side Effects
- external:api (TMDB API for metadata lookup)

## Process Flow
1. **Validate Input**: Verify TMDB ID, season, and episode numbers
2. **Fetch Metadata**: Retrieve show and episode details from TMDB (optional)
3. **Construct URL**: Build Vidking player URL with base URL `https://zo-stream-va.zocomputer.io`
4. **Add Parameters**: Include season, episode, and subtitle language
5. **Output**: Return formatted clickable URL

## Examples
- Basic episode: `play-tv-show --tmdbId 1399 --season 1 --episode 1`
- With subtitles: `play-tv-show --tmdbId 1399 --season 1 --episode 1 --subtitle_language fr`
- Game of Thrones S08E06: `play-tv-show --tmdbId 1399 --season 8 --episode 6`
- Breaking Bad pilot: `play-tv-show --tmdbId 1396 --season 1 --episode 1`

## URL Format
```
https://zo-stream-va.zocomputer.io/tv/{tmdbId}/{season}/{episode}?subtitle_language={lang}
```

## Notes
- The TMDB ID can be found in The Movie Database URL: `themoviedb.org/tv/{tmdbId}`
- Supported subtitle languages: en, es, fr, de, it, pt, ja, ko, zh, ru, ar, hi
- The Zo Stream service requires active user authentication
- Generated links are user-specific and temporary
- Season and episode numbers should match TMDB numbering (not network numbering)

## Related Components

**Related Commands**: [`play-movie`](../commands/play-movie.md)

**Scripts**: `N5/scripts/play_tv_show.py` (to be created)

**External APIs**: The Movie Database (TMDB)

**Service**: Zo Stream (`https://zo-stream-va.zocomputer.io`)

**Examples**: See [Examples Library](../examples/) for usage patterns

## Future Enhancements
- [ ] Search by show title instead of TMDB ID
- [ ] Auto-play next episode
- [ ] Track watch progress
- [ ] Integration with watchlist
- [ ] Auto-select subtitle language from user preferences
- [ ] Binge-watch mode (generate playlist for full season)
- [ ] Download option for offline viewing
