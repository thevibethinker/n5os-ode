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
