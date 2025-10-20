
import os

def main():
    list_file = "/home/workspace/Lists/content_creators_to_add.md"
    creators_dir = "/home/workspace/Startup Intelligence/Content Creators"

    with open(list_file, "r") as f:
        names = [line.strip() for line in f if line.strip()]

    for name in names:
        filename = name.lower().replace(" ", "-") + ".md"
        filepath = os.path.join(creators_dir, filename)

        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                f.write(f"# {name}\n\n")
            print(f"Created file: {filepath}")

    # Clear the list file
    with open(list_file, "w") as f:
        f.write("")

if __name__ == "__main__":
    main()
