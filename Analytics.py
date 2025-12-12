import sqlalchemy as db
from sqlalchemy import text
import matplotlib.pyplot as plt


class QuizAnalytics:
    def __init__(self, database_url='sqlite:///Quiz.db'):
        """Initializes the database connection"""
        self.engine = db.create_engine(database_url, echo=False)

    def get_user_scores(self):
        """Fetches user scores from the Analytics table"""
        with self.engine.connect() as con:
            query = text('SELECT Username, TotalQuestions, Score FROM Analytics')
            return con.execute(query).fetchall()

    def calculate_average_percentage(self, user_scores):
        """Calculates the average percentage score for each user"""
        averages = {}
        for username, total_questions, score in user_scores:
            if total_questions > 0 and 0 <= score <= total_questions:
                percentage = (score / total_questions) * 100
                if username in averages:
                    averages[username].append(percentage)
                else:
                    averages[username] = [percentage]

        return {user: sum(scores) / len(scores) for user, scores in averages.items()}

    def plot_scores(self):
        """Generates a chart showing the average percentage score of users"""
        user_scores = self.get_user_scores()

        if not user_scores:
            print("No data found in the Analytics table")
            return

        average_percentages = self.calculate_average_percentage(user_scores)

        if not average_percentages:
            print("No valid average percentage data available.")
            return

        usernames = list(average_percentages.keys())
        average_scores = list(average_percentages.values())

        plt.bar(usernames, average_scores, color='blue')
        plt.xlabel('Users')
        plt.ylabel('Average Score (%)')
        plt.title('Average Percentage Score of Users')
        plt.ylim(0, 150)

        for i, score in enumerate(average_scores):
            plt.text(i, score + 1, f'{score:.2f}%', ha='center', fontsize=10)

        plt.show()

    def wait_for_exit(self):

        while input("\nClose the chart and press 0 to exit the program: ") != "0":
            pass
        print("Quitting...")
        plt.close()


# Running the program
if __name__ == "__main__":

    quiz_analytics = QuizAnalytics()  # By default uses 'sqlite:///Quiz.db'
    quiz_analytics.plot_scores()  # Generate the chart
    quiz_analytics.wait_for_exit()  # Wait for the user to press 0
