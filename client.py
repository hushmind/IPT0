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
    print(f"Thank you for playing with us, {full_name}! Your score is {score}.")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5050))

# Receive greeting
print(s.recv(1024).decode('ascii'))

# Get user's full name
full_name = get_full_name()

# Choose difficulty level
difficulty = choose_difficulty()
s.send(difficulty.encode('ascii'))

# Game loop
attempts = 0
score = 0
try:
    while True:
        while True:
            guess = input("Enter your guess (an integer): ")
            s.send(guess.encode('ascii'))
            response = s.recv(1024).decode('ascii')
            print(response)
            attempts += 1
            if "Correct" in response:
                score += 1
                break
            if attempts >= 10:
                print("You have reached the maximum number of attempts.")
                if not play_again():
                    raise KeyboardInterrupt
    
        if not play_again():
            s.send("n".encode('ascii'))
            break
        else:
            s.send("y".encode('ascii'))

except KeyboardInterrupt:
    print_final_message(full_name, score)
    s.close()