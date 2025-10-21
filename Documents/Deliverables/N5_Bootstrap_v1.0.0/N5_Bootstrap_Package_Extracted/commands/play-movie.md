---
date: '2025-10-09T04:11:00Z'
last-tested: '2025-10-09T04:11:00Z'
generated_date: '2025-10-09T04:11:00Z'
checksum: play_movie_v1_0_0
tags: [media, streaming, entertainment, url-generation]
category: productivity
priority: low
related_files: []
anchors:
  input: null
  output: /home/workspace/N5/commands/play-movie.md
---
# `play-movie`

Version: 1.0.0

Summary: Generate a direct link to play a movie on the Zo Stream service

Workflow: misc

Tags: media, streaming, movies, url-generation

## Purpose
Generate a direct playback link for movies using The Movie Database (TMDB) ID and the Zo Stream service.

## Inputs
- --tmdbId : integer (required) — The Movie Database ID for the movie
- --subtitle_language : string (optional) — Two-letter ISO 639-1 language code (e.g., 'en', 'es', 'fr')

## Outputs
- playback_url : string — Direct clickable URL to play the movie
- movie_info : text — Movie title and metadata (if available)

## Side Effects
- external:api (TMDB API for metadata lookup)

## Process Flow
1. **Validate Input**: Verify TMDB ID is valid
2. **Fetch Metadata**: Retrieve movie title and details from TMDB (optional)
3. **Construct URL**: Build Vidking player URL with base URL `https://zo-stream-va.zocomputer.io`
4. **Add Parameters**: Include subtitle language if specified
5. **Output**: Return formatted clickable URL

## Examples
- Basic movie: `play-movie --tmdbId 1078605`
- With subtitles: `play-movie --tmdbId 1078605 --subtitle_language es`
- From TMDB URL: `play-movie --tmdbId 550` (Fight Club)

## URL Format
```
https://zo-stream-va.zocomputer.io/movie/{tmdbId}?subtitle_language={lang}
```

## Notes
- The TMDB ID can be found in The Movie Database URL: `themoviedb.org/movie/{tmdbId}`
- Supported subtitle languages: en, es, fr, de, it, pt, ja, ko, zh, ru, ar, hi
- The Zo Stream service requires active user authentication
- Generated links are user-specific and temporary

## Related Components

**Related Commands**: [`play-tv-show`](../commands/play-tv-show.md)

**Scripts**: `N5/scripts/play_movie.py` (to be created)

**External APIs**: The Movie Database (TMDB)

**Service**: Zo Stream (`https://zo-stream-va.zocomputer.io`)

**Examples**: See [Examples Library](../examples/) for usage patterns

## Future Enhancements
- [ ] Search by movie title instead of TMDB ID
- [ ] Queue multiple movies for playlist
- [ ] Integration with watchlist
- [ ] Auto-select subtitle language from user preferences
- [ ] Download option for offline viewing
