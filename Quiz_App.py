import sqlalchemy as db
from sqlalchemy import text
import random
import datetime


class QuizApp:
    def __init__(self, database_url='sqlite:///Quiz.db'):
        """Initialize the quiz app and connect to the database."""
        self.engine = db.create_engine(database_url, echo=False)
        self.quiz_id_counter = self.get_quiz_id_counter()

    def get_db_connection(self):
        """Returns a connection to the database."""
        return self.engine.connect()

    def get_quiz_id_counter(self):
        """Fetches the quiz ID counter or initializes it to 1."""
        con = self.get_db_connection()
        con.execute(text('''CREATE TABLE IF NOT EXISTS Settings (key TEXT PRIMARY KEY, value TEXT);'''))
        result = con.execute(text('SELECT value FROM Settings WHERE key = "quiz_id_counter";')).fetchone()

        if result:
            return int(result[0])
        else:
            con.execute(text('INSERT OR REPLACE INTO Settings (key, value) VALUES ("quiz_id_counter", "1");'))
            con.commit()
            return 1

    def update_quiz_id_counter(self):
        """Increments the quiz ID counter."""
        self.quiz_id_counter += 1
        con = self.get_db_connection()
        con.execute(text('UPDATE Settings SET value = :new_counter WHERE key = "quiz_id_counter";'),
                    {'new_counter': self.quiz_id_counter})
        con.commit()

    def get_flashcards_from_db(self):
        """Fetches all flashcards from the database."""
        con = self.get_db_connection()
        flash_query = con.execute(text('SELECT QuestionID, question, answer, category FROM questions;'))
        return flash_query.fetchall()

    def start_quiz(self, user_name):
        """Starts the quiz with selected flashcards."""
        flashcards = self.get_flashcards_from_db()
        if not flashcards:
            print("No flashcards in the database.")
            return

        num_questions = self.get_quiz_number(len(flashcards))

        # Randomly select questions
        selected_flashcards = random.sample(flashcards, num_questions)

        score = 0
        quiz_id = f'quiz_{self.quiz_id_counter}'

        print(f"\n{user_name}, the quiz is starting! Type '0' to quit.")
        for idx, (question_id, question, correct_answer, category) in enumerate(selected_flashcards, 1):
            print(f"\nQuestion {idx}/{num_questions} (Category: {category}):\n{question}")

            user_answer = input("Your answer: ").strip()
            if user_answer == '0':
                print("Ending the quiz.")
                break

            # Check the answer and update the score
            result = 1 if user_answer.lower() == correct_answer.lower() else 0
            print("Correct answer!" if result else f"Incorrect. The correct answer was: {correct_answer}")
            score += result

            self.save_answer_to_history(question, user_answer, result, question_id, user_name)

        print(f"\nQuiz ended! Your score: {score}/{num_questions}")
        self.save_quiz_result(quiz_id, user_name, num_questions, score)

    def get_quiz_number(self, total_questions):
        """Gets the number of questions for the quiz from the user."""
        while True:
            try:
                num_questions = int(input(f"Enter the number of questions for the quiz (maximum {total_questions}): "))
                if 0 < num_questions <= total_questions:
                    return num_questions
                else:
                    print(f"Please enter a number between 1 and {total_questions}.")
            except ValueError:
                print("Please enter a valid integer.")

    def save_answer_to_history(self, question, answer, result, question_id, user_name):
        """Saves the user's answer to the History table."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        con = self.get_db_connection()
        con.execute(text(''' 
            INSERT INTO History (Question, Answer, Date, Result, QuestionId, Username)
            VALUES (:question, :answer, :date, :result, :question_id, :username);
        '''), {'question': question, 'answer': answer, 'date': timestamp, 'result': result,
               'question_id': question_id, 'username': user_name})
        con.commit()

    def save_quiz_result(self, quiz_id, user_name, total_questions, score):
        """Saves the quiz result to the Analytics table."""
        self.update_quiz_id_counter()
        con = self.get_db_connection()
        con.execute(text(''' 
            INSERT INTO Analytics (QuizId, Username, TotalQuestions, Score)
            VALUES (:quiz_id, :username, :total_questions, :score);
        '''), {'quiz_id': quiz_id, 'username': user_name, 'total_questions': total_questions, 'score': score})
        con.commit()

    def main(self):
        """Main loop for the quiz application."""
        user_name = input("Enter your name: ").strip()
        if not user_name:
            print("Name cannot be empty. Try again.")
            return

        print(f"Hello, {user_name}!\n")
        while True:
            action = input("\n1. Start the quiz\n0. Quit\nChoice: ").strip()
            if action == '0':
                print("Exiting the application.")
                break
            elif action == '1':
                self.start_quiz(user_name)
            else:
                print("Invalid option. Try again.")


if __name__ == "__main__":
    app = QuizApp()
    app.main()
