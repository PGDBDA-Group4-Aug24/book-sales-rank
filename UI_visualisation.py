import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_csv('final_daily_df.csv')

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['week'] = df['timestamp'].dt.isocalendar().week  # Extract week number for weekly trend


def plot_book_rank_changes_individually(df, *book_titles):
    """
    Function to plot rank changes over time (month, day, week) for each book individually.

    Args:
    df (pd.DataFrame): DataFrame containing book data with 'rank', 'month', 'day', 'week', and 'TITLE' columns.
    *book_titles (str): Variable number of book titles to plot.
    """
    
    # Filter the DataFrame for the given book titles
    filtered_df = df[df['TITLE'].isin(book_titles)]

    # Check if any titles were passed and if data is available
    if filtered_df.empty:
        print("Error: No data available for the provided book titles.")
        return

    # Loop over each book title and plot separately
    for title in book_titles:
        book_df = filtered_df[filtered_df['TITLE'] == title]

        if book_df.empty:
            print(f"No data available for the book title: {title}")
            continue
        
        # Group by 'month', 'day', and 'week' and calculate the average rank
        avg_rank_per_month = book_df.groupby('month')['rank'].mean()
        avg_rank_per_day = book_df.groupby('day')['rank'].mean()
        avg_rank_per_week = book_df.groupby('week')['rank'].mean()

        # Create a figure with 3 subplots for each book
        fig, axes = plt.subplots(3, 1, figsize=(10, 12))  # 3 rows for month, day, and week plots

        # Plot 1: Monthly rank changes
        axes[0].plot(avg_rank_per_month.index, avg_rank_per_month.values, marker='o', label=title)
        axes[0].set_title(f'Rank Changes Over Months - {title}')
        axes[0].set_xlabel('Month')
        axes[0].set_ylabel('Average Rank')
        axes[0].legend(loc='upper right')
        axes[0].grid(True)

        # Plot 2: Daily rank changes
        axes[1].plot(avg_rank_per_day.index, avg_rank_per_day.values, marker='o', label=title)
        axes[1].set_title(f'Rank Changes Over Days - {title}')
        axes[1].set_xlabel('Day')
        axes[1].set_ylabel('Average Rank')
        axes[1].legend(loc='upper right')
        axes[1].grid(True)

        # Plot 3: Weekly rank changes
        axes[2].plot(avg_rank_per_week.index, avg_rank_per_week.values, marker='o', label=title)
        axes[2].set_title(f'Rank Changes Over Weeks - {title}')
        axes[2].set_xlabel('Week')
        axes[2].set_ylabel('Average Rank')
        axes[2].legend(loc='upper right')
        axes[2].grid(True)

        # Adjust the layout for each figure
        plt.tight_layout()

        # Display the plot for the current book
        plt.show()


# Example usage of the function with varargs
plot_book_rank_changes_individually(df, "Bobby Kennedy: A Raging Spirit", 'Kakadu Sunset')