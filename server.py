import socket
import random
import logging
import os
import json

# Configure logging to write to both file and console
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('server.log'),
                        logging.StreamHandler()
                    ])

DATA_FILE = 'leaderboard.json'

def load_leaderboard():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_leaderboard(leaderboard):
    with open(DATA_FILE, 'w') as f:
        json.dump(leaderboard, f)

def generate_random_number(difficulty):
    if difficulty == 'a':
        return random.randint(1, 50)
    elif difficulty == 'b':
        return random.randint(1, 100)
    elif difficulty == 'c':
        return random.randint(1, 500)
    else:
        return None

def get_score(attempts):
    return max(0, 100 - attempts)

def print_leaderboard(leaderboard):
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1]['score'], reverse=True)
    return "\n".join([f"{name}: {data['score']} (Difficulty: {data['difficulty']})" for name, data in sorted_leaderboard])

leaderboard = load_leaderboard()

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set socket options to allow address reuse
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    serversocket.bind(('127.0.0.1', 5050))
    serversocket.listen(5)
    logging.info("Server started. Waiting for connections on port 5050...")
except Exception as e:
    logging.error(f"Error occurred while starting server: {e}")
    raise

try:
    while True:
        logging.info("Waiting for connections...")
        clientsocket, address = serversocket.accept()
        logging.info(f"Connection from: {address}")

        try:
            # Send greeting
            clientsocket.send("Welcome to the Guessing Game! Please enter your full name: ".encode('ascii'))

            # Receive full name from client
            full_name = clientsocket.recv(1024).decode('ascii')
            logging.info(f"Received full name: {full_name}")

            # Load user data if available
            if full_name in leaderboard:
                current_score = leaderboard[full_name]['score']
                last_difficulty = leaderboard[full_name]['difficulty']
            else:
                current_score = 0
                last_difficulty = 'a'

            while True:
                # Send current score and difficulty prompt
                clientsocket.send(f"Your current score: {current_score}. Last chosen difficulty: {last_difficulty}. Choose a new difficulty level (a/b/c): ".encode('ascii'))

                # Receive difficulty choice from client
                difficulty = clientsocket.recv(1024).decode('ascii')
                logging.info(f"Difficulty chosen: {difficulty}")

                # Generate random number based on chosen difficulty
                num_to_guess = generate_random_number(difficulty)
                logging.info(f"Number to guess: {num_to_guess}")

                # Game loop
                attempts = 0
                max_attempts = 10
                while attempts < max_attempts:
                    guess = clientsocket.recv(1024).decode('ascii')
                    logging.info(f"Received guess: {guess}")

                    if not guess.isdigit():
                        clientsocket.send("Invalid guess. Please enter an integer.".encode('ascii'))
                        continue

                    guess = int(guess)
                    attempts += 1

                    if guess == num_to_guess:
                        clientsocket.send("Correct! You guessed it!".encode('ascii'))
                        current_score += get_score(attempts)
                        break
                    elif guess < num_to_guess:
                        clientsocket.send("Too low! Try again.".encode('ascii'))
                    else:
                        clientsocket.send("Too high! Try again.".encode('ascii'))

                    if attempts >= max_attempts:
                        clientsocket.send("You have reached the maximum number of attempts.".encode('ascii'))
                        break

                # Update leaderboard
                leaderboard[full_name] = {
                    'score': current_score,
                    'difficulty': difficulty
                }
                save_leaderboard(leaderboard)

                # Ask if user wants to play again
                play_again = clientsocket.recv(1024).decode('ascii')
                logging.info(f"Play again choice: {play_again}")
                if play_again.lower() != 'y':
                    break

            # Send final message and leaderboard
            clientsocket.send(f"Thank you for playing with us, {full_name}! Your final score is {current_score}.".encode('ascii'))
            clientsocket.send(print_leaderboard(leaderboard).encode('ascii'))

        except Exception as ex:
            logging.error(f"Error occurred during game: {ex}")
        finally:
            clientsocket.close()

except KeyboardInterrupt:
    logging.info("Server terminated by user.")
finally:
    serversocket.close()
