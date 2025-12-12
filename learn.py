import sqlalchemy as db
import random

class FlashcardLearner:
    def __init__(self, database_url='sqlite:///Quiz.db'):
        """Initialize the FlashcardLearner"""
        self.database_url = database_url
        self.engine = db.create_engine(self.database_url, echo=False)
        self.connection = None

    def get_db_connection(self):
        """connects to the database"""
        if not self.connection:
            self.connection = self.engine.connect()
        return self.connection

    def close_db_connection(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_flashcards_from_db(self):
        """ fetches all flashcards from the database and returns them as a list."""
        con = self.get_db_connection()  # Using the active connection
        flash_query = con.execute(db.text('SELECT question, answer, category FROM questions;'))
        flashcards = flash_query.fetchall()  # Fetch all query results
        return flashcards

    def check_if_flashcards_exist(self):
        """Checks if there are any flashcards."""
        flashcards = self.get_flashcards_from_db()
        return len(flashcards) > 0

    def learn_flashcards(self):
        """learning process."""
        if not self.check_if_flashcards_exist():
            print("No flashcards in the system. Exiting.")
            self.close_db_connection()
            return

        print("Welcome to the flashcard learning module!")  # Welcome message

        while True:  # Main loop, runs until the user decides to exit
            flashcards = self.get_flashcards_from_db()
            random.shuffle(flashcards)  # Shuffle flashcards

            for card in flashcards:
                question, correct_answer, category = card
                print(f"\nCategory: {category}\nQuestion: {question}")

                #  user's answer
                user_answer = input("Your answer (press Enter to skip or enter 0 to quit): ").strip()

                if user_answer == '0':
                    print("Quitting")
                    self.close_db_connection()
                    return

                # If the user presses Enter without an answer, skip the question
                if user_answer == '':
                    print("Skipping the question.\n")
                    continue

                # Check the answer
                if user_answer.lower() == correct_answer.lower():
                    print("Correct answer.")
                else:
                    print(f"The answer was incorrect. The correct answer is: {correct_answer}")

                user_input = input("\nEnter 0 to quit or press Enter for the next question: ").strip()

                if user_input == '0':
                    print("Quitting")
                    self.close_db_connection()
                    return  # End the program

            print("\nEnd of round. Starting over...\n")

        self.close_db_connection()

# Start the learning process
if __name__ == "__main__":

    learner = FlashcardLearner()  # Create the FlashcardLearner object
    learner.learn_flashcards()  # Start the learning session
