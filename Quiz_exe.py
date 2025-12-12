from flashcard import FlashcardApp
from learn import FlashcardLearner
from Quiz_App import QuizApp
from Analytics import QuizAnalytics
import logging

import sys
import os
from sqlalchemy import create_engine

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller EXE
    except AttributeError:
        base_path = os.path.abspath(".")  # zwykły Python
    return os.path.join(base_path, relative_path)

DB_PATH = resource_path("Quiz.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

def main_menu():
    print(f"\nWelcome to the Flashcard App: ")


if __name__ == "__main__":
    while True:
        main_menu()  # Display the main menu
        choice = input(
            f"Select 0 to Quit, 1 to Add Flashcard, 2 to Learn, 3 to Start Quiz, 4 to Start Analytics: ").strip()

        if choice == '1':
            print("Adding Flashcard / Deleting Flashcard: \n")
            app = FlashcardApp()
            app.main()

        elif choice == '2':
            print("Learning module has been chosen! \n")
            learner = FlashcardLearner()
            learner.learn_flashcards()

        elif choice == '3':
            print("Start Quiz \n")
            app = QuizApp()
            app.main()

        elif choice == '4':
            print("Start Analytics \n")
            quiz_analytics = QuizAnalytics()  # By default uses 'sqlite:///Quiz.db'
            quiz_analytics.plot_scores()  # Generate the chart
            quiz_analytics.wait_for_exit()  # Wait for user to press 0 to exit the program

        elif choice == '0':
            print("Quitting Quiz \n")
            break
        else:
            print("Invalid choice. Try again!\n")
