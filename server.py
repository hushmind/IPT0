import socket
import random
import logging

# Configure logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_random_number(difficulty):
    if difficulty == 'a':
        return random.randint(1, 50)
    elif difficulty == 'b':
        return random.randint(1, 100)
    elif difficulty == 'c':
        return random.randint(1, 500)
    else:
        return None

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    serversocket.bind(('127.0.0.1', 5050))
    serversocket.listen(5)
    logging.info("Server started. Waiting for connections...")
except Exception as e:
    logging.error(f"Error occurred while starting server: {e}")
    raise

try:
    while True:
        logging.info("Waiting for connections...")
        (clientsocket, address) = serversocket.accept()
        logging.info(f"Connection from: {address}")
        
        try:
            # Send greeting
            clientsocket.send("Welcome to the Guessing Game! Choose your difficulty level (a/b/c): ".encode('ascii'))

            # Receive difficulty choice from client
            difficulty = clientsocket.recv(1024).decode('ascii')
            logging.info(f"Difficulty chosen: {difficulty}")

            # Generate random number based on chosen difficulty
            num_to_guess = generate_random_number(difficulty)
            logging.info(f"Number to guess: {num_to_guess}")

            # Game loop
            while True:
                guess = clientsocket.recv(1024).decode('ascii')
                logging.info(f"Received guess: {guess}")
                
                if not guess.isdigit():
                    clientsocket.send("Invalid guess. Please enter an integer.".encode('ascii'))
                    continue
                
                guess = int(guess)
                if guess == num_to_guess:
                    clientsocket.send("Correct! You guessed it!".encode('ascii'))
                    break
                elif guess < num_to_guess:
                    clientsocket.send("Too low! Try again.".encode('ascii'))
                else:
                    clientsocket.send("Too high! Try again.".encode('ascii'))
        except Exception as ex:
            logging.error(f"Error occurred during game: {ex}")
        finally:
            clientsocket.close()

except KeyboardInterrupt:
    logging.info("Server terminated by user.")
finally:
    serversocket.close()