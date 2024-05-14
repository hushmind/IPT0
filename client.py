import socket

def choose_difficulty():
    while True:
        choice = input("Choose difficulty level (a/b/c): ").lower()
        if choice in ['a', 'b', 'c']:
            return choice
        else:
            print("Invalid choice. Please enter 'a', 'b', or 'c'.")

def get_full_name():
    return input("Enter your full name: ")

def play_again():
    while True:
        choice = input("Do you want to keep playing? (y/n): ").lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print("Invalid choice. Please enter 'y' or 'n'.")

def print_final_message(full_name, score):
    print(f"Thank you for playing with us, {full_name}! Your final score is {score}.")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect(('127.0.0.1', 5050))
    print("Connected to the server.")

    # Receive greeting
    print(s.recv(1024).decode('ascii'))

    # Get user's full name
    full_name = get_full_name()
    s.send(full_name.encode('ascii'))
    print(f"Sent full name: {full_name}")

    # Main game loop
    while True:
        # Receive current score and difficulty prompt
        print(s.recv(1024).decode('ascii'))

        # Choose difficulty level
        difficulty = choose_difficulty()
        s.send(difficulty.encode('ascii'))
        print(f"Sent difficulty: {difficulty}")

        # Game loop
        while True:
            guess = input("Enter your guess (an integer): ")
            s.send(guess.encode('ascii'))
            response = s.recv(1024).decode('ascii')
            print(response)
            if "Correct" in response or "You have reached the maximum number of attempts." in response:
                break

        if not play_again():
            s.send("n".encode('ascii'))
            print("Sent play again choice: n")
            break
        else:
            s.send("y".encode('ascii'))
            print("Sent play again choice: y")

    # Receive and display final message and leaderboard
    print(s.recv(1024).decode('ascii'))
    leaderboard = s.recv(4096).decode('ascii')  # increased buffer size to handle large leaderboard
    print("Leaderboard:\n", leaderboard)

except KeyboardInterrupt:
    print_final_message(full_name, "unknown")  # final score is unknown if interrupted
finally:
    s.close()   
