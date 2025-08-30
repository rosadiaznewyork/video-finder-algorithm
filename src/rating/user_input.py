def get_user_rating_response() -> str:
    import sys
    while True:
        sys.stdout.write("Rate this video (y/n/q): ")
        sys.stdout.flush()
        response = sys.stdin.readline().strip().lower()
        
        if not response:
            print("No input received. Please try again.")
            continue
            
        if response[0] in ['y', 'n', 'q']:
            return response[0]
        print("Please enter 'y', 'n', or 'q'")

def get_user_notes_for_rating(liked: bool) -> str:
    import sys
    if liked:
        sys.stdout.write("Why did you like it? (optional): ")
    else:
        sys.stdout.write("Why didn't you like it? (optional): ")
    sys.stdout.flush()
    return sys.stdin.readline().strip()