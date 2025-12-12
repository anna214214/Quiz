import sqlalchemy as db
from sqlalchemy import text


class FlashcardApp:
    def __init__(self, database_url='sqlite:///Quiz.db'):
        """Initialize the flashcard management app."""
        self.database_url = database_url
        self.engine = db.create_engine(self.database_url, echo=False)  # Create the connection engine

    def get_db_connection(self):
        """Connect to the database"""
        return self.engine.connect()

    def close_db_connection(self, connection):
        """Close the database connection."""
        if connection:
            connection.close()

    def display_flashcards_from_db(self):
        """Fetch all flashcards from the database"""
        with self.get_db_connection() as con:
            flash_query = con.execute(text('SELECT QuestionID, question, answer, category FROM questions;'))
            existing_flashcards = flash_query.fetchall()

        if existing_flashcards:
            print("\nYour flashcards in the database:")
            for row in existing_flashcards:
                print(f"{row[0]}. {row[1]} - Answer: {row[2]} - Category: {row[3]}")
        else:
            print("No flashcards found in the database.")

    def get_valid_input(self, prompt):
        user_input = input(prompt).strip()
        while not user_input:
            print("Input cannot be empty. Please try again.")
            user_input = input(prompt).strip()
        return user_input

    def add_flashcard(self):
        """Allow the user to add a new flashcard to Quiz.db."""
        category = self.get_valid_input("Enter the category for your flashcard: ")
        question = self.get_valid_input("Enter the question for your flashcard: ")
        answer = self.get_valid_input("Enter the answer: ")

        with self.get_db_connection() as con:
            # Check if the question already exists
            result = con.execute(text('SELECT 1 FROM questions WHERE question = :question')
                                 .params(question=question)).fetchone()

            if result:
                print(f"Flashcard '{question}' already exists in the database.")
            else:
                try:
                    con.execute(
                        text(
                            'INSERT INTO questions (question, answer, category) VALUES (:question, :answer, :category);')
                        .params(question=question, answer=answer, category=category)
                    )
                    con.commit()
                    print(f"Flashcard '{question}' has been added to the database.")
                except Exception as e:
                    print(f"There was a problem adding the flashcard: {e}")

    def delete_flashcard(self):
        """Allow the user to delete a flashcarde."""
        self.display_flashcards_from_db()
        try:
            card_to_delete = int(input("Enter the ID of the flashcard you want to delete (0 to cancel): ").strip())
            if card_to_delete == 0:
                print("Flashcard deletion canceled.")
                return

            with self.get_db_connection() as con:
                # Check if the flashcard with the given ID exists
                flash_query = con.execute(text('SELECT QuestionID, question FROM questions WHERE QuestionID = :id')
                                          .params(id=card_to_delete))
                flashcard = flash_query.fetchone()

                if flashcard:
                    question_to_delete = flashcard[1]
                    con.execute(
                        text('DELETE FROM questions WHERE QuestionID = :id').params(id=card_to_delete))
                    con.commit()
                    print(f"Flashcard '{question_to_delete}' has been deleted from the database.")

                    # Reorder the QuestionID values to remove gaps
                    con.execute(text(""" 
                        WITH RankedQuestions AS (
                            SELECT QuestionID, ROW_NUMBER() OVER (ORDER BY QuestionID) AS RowNum
                            FROM questions
                        )
                        UPDATE questions
                        SET QuestionID = RankedQuestions.RowNum
                        FROM RankedQuestions
                        WHERE questions.QuestionID = RankedQuestions.QuestionID;
                    """))
                    con.commit()
                else:
                    print("Invalid flashcard ID.")
        except ValueError:
            print("Please enter a valid number.")

    def main(self):
        """Main program loop for"""
        while True:
            self.display_flashcards_from_db()

            action = input("\nChoose an option:\n1. Add a flashcard\n2. Delete a flashcard\n0. Exit\nChoice: ").strip()

            if action == '0':
                print("Exiting the program.")
                break
            elif action == '1':
                self.add_flashcard()
            elif action == '2':
                self.delete_flashcard()
            else:
                print("Invalid option. Please try again.")

# Run the application
if __name__ == "__main__":
    app = FlashcardApp()
    app.main()
