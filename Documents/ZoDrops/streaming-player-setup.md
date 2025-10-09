# ZoDrop: Streaming Player Setup

**Shared by:** V (@va)  
**Category:** Entertainment & Media  
**Difficulty:** Intermediate  
**Estimated Setup Time:** 10-15 minutes

---

## 🎬 What This Does

This ZoDrop enables you to instantly stream movies and TV shows through your Zo Computer with a simple command. Instead of searching through streaming services, just tell Zo what you want to watch, and it generates a direct streaming link.

**Key Features:**
- Stream any movie or TV show using TMDB IDs
- Support for multiple subtitle languages
- Integrated into N5 command system for natural language invocation
- Works with Zo Stream service (requires access to Zo Stream)

---

## 📋 Prerequisites

1. **Zo Computer** with N5 command system set up
2. **Access to Zo Stream service** (this uses `https://zo-stream-va.zocomputer.io` - you may need to request access or set up your own instance)
3. **Python 3** installed (already available in Zo Computer)
4. **N5 directory structure** in your workspace

---

## 🚀 Setup Instructions

### Step 1: Create the Streaming Script

Create the file `/home/workspace/N5/scripts/n5_play_stream.py`:

```python
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Generate a Vidking streaming URL.")
    parser.add_argument("--command", required=True, help="The command to execute (play-movie or play-tv-show).")
    parser.add_argument("--tmdbId", required=True, help="The TMDB ID of the movie or TV show.")
    parser.add_argument("--season", help="The season number for TV shows.")
    parser.add_argument("--episode", help="The episode number for TV shows.")
    parser.add_argument("--subtitle_language", default="en", help="The two-letter ISO 639-1 language code for subtitles (default: en).")

    args = parser.parse_args()

    base_url = "https://zo-stream-va.zocomputer.io"
    vidking_base_url = "https://www.vidking.net/embed"

    if args.command == "play-movie":
        if args.season or args.episode:
            print("Error: --season and --episode are not applicable for movies.", file=sys.stderr)
            sys.exit(1)
        
        # Construct Vidking player URL
        vidking_url = f"{vidking_base_url}/movie/{args.tmdbId}"
        
        # Construct the URL with query parameters
        params = {"subtitle": args.subtitle_language}
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        final_url = f"{base_url}/movie/{args.tmdbId}?{query_string}"

    elif args.command == "play-tv-show":
        if not args.season or not args.episode:
            print("Error: --season and --episode are required for TV shows.", file=sys.stderr)
            sys.exit(1)
        
        # Construct Vidking player URL
        vidking_url = f"{vidking_base_url}/tv/{args.tmdbId}/{args.season}/{args.episode}"

        # Construct the URL with query parameters
        params = {"subtitle": args.subtitle_language}
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        final_url = f"{base_url}/tv/{args.tmdbId}/{args.season}/{args.episode}?{query_string}"

    else:
        print(f"Error: Unknown command '{args.command}'.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Clickable Link: {final_url}")

if __name__ == "__main__":
    main()
```

**Important:** If you're not using the shared Zo Stream instance, replace `https://zo-stream-va.zocomputer.io` with your own streaming service URL.

---

### Step 2: Create Command Definition Files

Create `/home/workspace/N5/commands/play-movie.md`:

```markdown
# Command: play-movie

## Purpose
Generate a direct link to play a movie on the Zo Stream service.

## Usage
play-movie --tmdbId <TMDB_MOVIE_ID> [--subtitle_language <LANGUAGE_CODE>]

## Steps
1. Receive TMDB movie ID and optional subtitle language.
2. Construct the Vidking player URL using the Zo Stream service base URL.
3. If `subtitle_language` is provided, append it to the URL parameters.
4. Output the generated clickable URL.

## Examples
- Play movie with ID 1078605: `play-movie --tmdbId 1078605`
- Play movie with ID 1078605 and Spanish subtitles: `play-movie --tmdbId 1078605 --subtitle_language es`

## Notes
- The TMDB ID refers to The Movie Database ID for a specific movie.
- The `subtitle_language` should be a two-letter ISO 639-1 language code (e.g., `en` for English, `es` for Spanish).
```

Create `/home/workspace/N5/commands/play-tv-show.md`:

```markdown
# Command: play-tv-show

## Purpose
Generate a direct link to play a TV show episode on the Zo Stream service.

## Usage
play-tv-show --tmdbId <TMDB_TV_ID> --season <SEASON_NUMBER> --episode <EPISODE_NUMBER> [--subtitle_language <LANGUAGE_CODE>]

## Steps
1. Receive TMDB TV show ID, season number, episode number, and optional subtitle language.
2. Construct the Vidking player URL using the Zo Stream service base URL.
3. If `subtitle_language` is provided, append it to the URL parameters.
4. Output the generated clickable URL.

## Examples
- Play Breaking Bad S01E01: `play-tv-show --tmdbId 1396 --season 1 --episode 1`
- Play with Spanish subtitles: `play-tv-show --tmdbId 1396 --season 1 --episode 1 --subtitle_language es`

## Notes
- The TMDB ID refers to The Movie Database ID for a specific TV show series.
- Season and episode numbers are required for TV shows.
- The `subtitle_language` should be a two-letter ISO 639-1 language code.
```

---

### Step 3: Register Commands in N5

Add these entries to `/home/workspace/N5/config/commands.jsonl`:

```json
{"command": "play-movie", "file": "N5/commands/play-movie.md", "description": "Generate a direct link to play a movie on the Zo Stream service.", "aliases": ["movie"], "category": "streaming", "script": "/home/workspace/N5/scripts/n5_play_stream.py"}
{"command": "play-tv-show", "file": "N5/commands/play-tv-show.md", "description": "Generate a direct link to play a TV show episode on the Zo Stream service.", "aliases": ["tv", "episode"], "category": "streaming", "script": "/home/workspace/N5/scripts/n5_play_stream.py"}
```

**Note:** Each entry should be on a single line in the JSONL file.

---

### Step 4: Make the Script Executable

```bash
chmod +x /home/workspace/N5/scripts/n5_play_stream.py
```

---

### Step 5: Test the Installation

Test with a movie (Everything Everywhere All at Once - TMDB ID: 545611):

```bash
python3 /home/workspace/N5/scripts/n5_play_stream.py --command play-movie --tmdbId 545611
```

Expected output:
```
Clickable Link: https://zo-stream-va.zocomputer.io/movie/545611?subtitle=en
```

---

## 🎯 Usage Examples

### Natural Language Commands

Once integrated with N5, you can use natural language:

**Movies:**
- "n5: play 'Everything Everywhere All at Once' movie"
- "Play Dune movie"
- "Stream The Matrix"

**TV Shows:**
- "n5: play Breaking Bad season 1 episode 1"
- "Play The Office S03E05"

### Direct Command Usage

**Play a Movie:**
```bash
python3 /home/workspace/N5/scripts/n5_play_stream.py --command play-movie --tmdbId 545611
```

**Play a Movie with Spanish Subtitles:**
```bash
python3 /home/workspace/N5/scripts/n5_play_stream.py --command play-movie --tmdbId 545611 --subtitle_language es
```

**Play a TV Show Episode:**
```bash
python3 /home/workspace/N5/scripts/n5_play_stream.py --command play-tv-show --tmdbId 1396 --season 1 --episode 1
```

---

## 🔍 Finding TMDB IDs

### Method 1: Ask Zo
Simply say: "Find the TMDB ID for [movie/show name]"

Zo will search and extract the ID for you.

### Method 2: Manual Search
1. Visit [The Movie Database](https://www.themoviedb.org/)
2. Search for your movie or TV show
3. Look at the URL: `themoviedb.org/movie/[ID]-movie-name`
4. The number after `/movie/` or `/tv/` is your TMDB ID

**Examples:**
- Everything Everywhere All at Once: `545611`
- Breaking Bad: `1396`
- The Matrix: `603`

---

## 🌐 Subtitle Language Codes

Common ISO 639-1 language codes:

| Language | Code |
|----------|------|
| English | `en` |
| Spanish | `es` |
| French | `fr` |
| German | `de` |
| Italian | `it` |
| Portuguese | `pt` |
| Japanese | `ja` |
| Korean | `ko` |
| Chinese (Simplified) | `zh` |
| Russian | `ru` |
| Arabic | `ar` |
| Hindi | `hi` |

For a complete list, see: [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

---

## 🔧 Customization Options

### Using Your Own Streaming Service

If you want to use a different streaming service:

1. Open `/home/workspace/N5/scripts/n5_play_stream.py`
2. Modify the `base_url` variable:
   ```python
   base_url = "https://your-stream-service.example.com"
   ```
3. Save the file

### Adding Incantum Triggers (Optional)

To enable natural language triggers like "play movie" or "watch episode", add to `/home/workspace/N5/config/incantum_triggers.json`:

```json
[
  {
    "trigger": "play movie",
    "aliases": [
      "watch movie",
      "stream movie",
      "movie play"
    ],
    "command": "play-movie"
  },
  {
    "trigger": "play tv show",
    "aliases": [
      "watch episode",
      "stream episode",
      "play episode",
      "tv show"
    ],
    "command": "play-tv-show"
  }
]
```

---

## 🐛 Troubleshooting

### Issue: "Command not found"

**Solution:** Ensure the script path in `commands.jsonl` is correct and the script exists:
```bash
ls -la /home/workspace/N5/scripts/n5_play_stream.py
```

### Issue: "Error: --season and --episode are required"

**Solution:** For TV shows, you must specify both season and episode numbers:
```bash
python3 /home/workspace/N5/scripts/n5_play_stream.py --command play-tv-show --tmdbId 1396 --season 1 --episode 1
```

### Issue: Streaming link doesn't work

**Solutions:**
1. Verify you have access to the Zo Stream service
2. Check that the TMDB ID is correct
3. Test with a known working ID (e.g., 545611 for Everything Everywhere All at Once)
4. Ensure your base_url is correctly configured

### Issue: Wrong TMDB ID

**Solution:** Double-check the TMDB ID:
- Movies and TV shows have different IDs
- The ID should be numeric only
- Verify on themoviedb.org

---

## 💡 Pro Tips

1. **Bookmark Common IDs:** Create a personal list of your favorite movies/shows with their TMDB IDs for quick access.

2. **Create Aliases:** Add personal shortcuts in your N5 system for frequently watched content.

3. **Batch Processing:** Write a simple script to generate multiple links at once for binge-watching sessions.

4. **Integration with Lists:** Add streaming commands to your N5 lists system to track what you want to watch.

---

## 📚 Additional Resources

- [The Movie Database (TMDB)](https://www.themoviedb.org/)
- [TMDB API Documentation](https://developers.themoviedb.org/3)
- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [Zo Computer Documentation](https://docs.zocomputer.io/)

---

## 🤝 Contributing Back

If you enhance this setup or create variations, consider sharing your own ZoDrop! The community grows when we share what we build.

**Improvement Ideas:**
- Add watchlist integration
- Create a recommendation system
- Build a "continue watching" feature
- Add support for custom player preferences

---

## 📝 Version History

**v1.0** (2025-10-09)
- Initial release
- Support for movies and TV shows
- Subtitle language selection
- N5 command system integration

---

## ⚖️ Legal Notice

This setup is for personal use within the Zo Computer environment. Ensure you have proper access rights to any streaming services you use. Respect copyright laws and content licensing agreements in your jurisdiction.

---

## 💬 Questions or Issues?

If you run into problems or have questions:
1. Check the troubleshooting section above
2. Review your N5 system logs
3. Ask in the Zo Discord community
4. Tag @va for streaming-specific questions

---

**Happy Streaming! 🍿**

---

*This ZoDrop is part of V's ZoDrops collection - practical capabilities shared with the Zo community.*
