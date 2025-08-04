"""User database management system with data visualization."""
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import os


def connect_db():
    """Create connection to database.
    Returns:
        sqlite3.Connection: Database connection object
    """
    return sqlite3.connect("my_database.db")


def initialize_database():
    """Create users table if it doesn't exist."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER CHECK(age > 0),
            iq INTEGER CHECK(iq > 0),
            bench_press INTEGER CHECK(bench_press >= 0)
        )
    ''')
    conn.commit()
    conn.close()


def add_new_user():
    """Add new user to database with input validation."""
    conn = connect_db()
    cursor = conn.cursor()
    while True:
        try:
            # Prompt the user for input and validate the data
            name = input("Name (Name_Lastname): ").strip()
            if not name:  # Ensure the name is not empty
                raise ValueError("Name cannot be empty")
            age = int(input("Age: "))
            if age <= 0:  # Ensure the age must be a positive number
                raise ValueError("Age must be a positive number")
            iq = int(input("IQ: "))
            if iq <= 0:  # Ensure the IQ is a positive number
                raise ValueError("IQ must be a positive number")
            bench_press = int(input("Bench press (kg): "))
            if bench_press < 0:  # Ensure the bench press is not negative
                raise ValueError("Bench press cannot be negative")

            # If all inputs are valid, insert the new user into the database
            new_user = (name, age, iq, bench_press)
            cursor.execute(
                "INSERT INTO users (name, age, iq, bench_press) VALUES (?, ?, ?, ?)",
                new_user
            )
            conn.commit()
            print("New user was added")
            break  # Exit the loop if everything is ok
        except ValueError as e:
            # Handle invalid input errors and prompt the user to try again
            print(f"Invalid input: {e}. Please try again")
        except Exception as e:
            # Handle any unexpected errors and exit loop
            print(f"An unexpected error occurred: {e}")
            conn.rollback()
            break
    conn.close()


def delete_user():
    """Delete user from database by ID."""
    conn = connect_db()
    cursor = conn.cursor()
    # First show all users
    df = read_db()
    if df.empty:
        print("Database is empty. Nothing to delete.")
        conn.close()
        return
    print("Current users:")
    print(df.to_string(index=False))
    while True:
        try:
            # Prompt the user for input and validate the data
            user_id = int(input("Enter user id to delete: "))
            # Check if user exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE id=?", (user_id,))
            if cursor.fetchone()[0] == 0:
                print("User with this ID does not exist. Please try again")
                continue
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()  # Saving changes
            print("User was deleted from DataBase")
            break
        except ValueError:
            # Handle invalid input error and prompt the user to not enter the string
            print("Invalid input: Please enter a valid ID (number).")
            continue
        except Exception as e:
            print(f"Error deleting user: {e}")
            conn.rollback()  # Roll back changes in case of error
            break
    conn.close()


def update_user():
    """Update user from database by ID."""
    conn = connect_db()
    cursor = conn.cursor()
    # First show all users
    df = read_db()
    if df.empty:
        print("Database is empty. Nothing to update.")
        conn.close()
        return
    print("Current users:")
    print(df.to_string(index=False))

    while True:
        try:
            user_id = int(input("Enter user id to update: "))
            # Check if user exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE id=?", (user_id,))
            if cursor.fetchone()[0] == 0:
                print("User with this ID does not exist. Please try again")
                continue

            print("What do you want to update?")
            print("1. Bench press")
            print("2. IQ")
            print("3. Age")
            print("4. Name")
            update_choice = input("Choose an option (1-4): ").strip()

            if update_choice == "1":
                try:
                    new_bench_press = int(input("New bench press (kg): "))
                    if new_bench_press < 0:
                        print("Bench press cannot be negative.")
                        continue
                    cursor.execute("UPDATE users SET bench_press = ? WHERE id = ?", (new_bench_press, user_id))
                    conn.commit()
                    print("Bench press was updated")
                    break
                except ValueError:
                    print("Invalid input: Please enter a number.")
                    continue

            elif update_choice == "2":
                try:
                    new_iq = int(input("New IQ: "))
                    if new_iq <= 0:
                        print("IQ must be a positive number.")
                        continue
                    cursor.execute("UPDATE users SET iq = ? WHERE id = ?", (new_iq, user_id))
                    conn.commit()
                    print("IQ was updated")
                    break
                except ValueError:
                    print("Invalid input: Please enter a number.")
                    continue

            elif update_choice == "3":
                try:
                    new_age = int(input("New age: "))
                    if new_age <= 0:
                        print("Age must be a positive number.")
                        continue
                    cursor.execute("UPDATE users SET age = ? WHERE id = ?", (new_age, user_id))
                    conn.commit()
                    print("Age was updated")
                    break
                except ValueError:
                    print("Invalid input: Please enter a number.")
                    continue

            elif update_choice == "4":
                new_name = input("New name: ").strip()
                if not new_name:
                    print("Name cannot be empty.")
                    continue
                cursor.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
                conn.commit()
                print("Name was updated")
                break

            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
                continue

        except ValueError:
            print("Invalid input: Please enter a valid ID (number).")
            continue
        except Exception as e:
            print(f"Error updating user: {e}")
            conn.rollback()
            break
    conn.close()


def read_db():
    """Read all users from database.
    Returns:
        pandas.DataFrame: DataFrame with all users data
    """
    query = 'SELECT * FROM users'
    conn = connect_db()
    try:
        df = pd.read_sql_query(query, conn)  # Using pandas to read the database
    except Exception as e:
        print(f"Error reading database: {e}")
        df = pd.DataFrame()  # Return empty DataFrame on error
    finally:
        conn.close()
    return df


def draw_scatter():
    """Create and display scatter plot of IQ vs Bench Press with unique filename."""
    df = read_db()
    # Check if data exists
    if df.empty:
        print("No data available for visualization")
        return

    x = df['iq']
    y = df['bench_press']

    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, color='red', alpha=0.7, s=60)
    plt.title("Bench press by IQ", fontsize=14, fontweight='bold')
    plt.xlabel("IQ", fontsize=12)
    plt.ylabel("Bench press (kg)", fontsize=12)
    plt.grid(True, alpha=0.3)

    # Add correlation coefficient if we have enough data
    if len(df) > 1:
        correlation = df['iq'].corr(df['bench_press'])
        plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}',
                 transform=plt.gca().transAxes, fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    def get_unique_filename(base_name="scatter", extension=".png"):
        """Generate unique filename by checking existing files."""
        filename = base_name + extension
        if not os.path.exists(filename):
            return filename
        counter = 2
        while True:
            filename = f"{base_name}{counter}{extension}"
            if not os.path.exists(filename):
                return filename
            counter += 1

    save_choice = input("Do you want to save the scatter? (y/n): ").strip().lower()
    if save_choice == 'y':
        filename = get_unique_filename()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f'Scatter saved as {filename}')
    plt.show()


def show_statistics():
    """Show basic statistics of the data."""
    df = read_db()
    if df.empty:
        print("No data available for statistics")
        return
    print("\nData Statistics:")
    print("=" * 30)
    print(f"Total users: {len(df)}")
    print(f"Average age: {df['age'].mean():.1f}")
    print(f"Average IQ: {df['iq'].mean():.1f}")
    print(f"Average bench press: {df['bench_press'].mean():.1f} kg")
    print(f"Max bench press: {df['bench_press'].max()} kg")
    print(f"Min bench press: {df['bench_press'].min()} kg")


def main():
    """Main application function."""
    # Initialize database
    initialize_database()
    print("=== User Database Manager ===")
    while True:
        print("\nOptions:")
        print("1. View all users")
        print("2. Add new user")
        print("3. Delete user")
        print("4. Update user")
        print("5. Show statistics")
        print("6. Create scatter plot")
        print("7. Exit")
        choice = input("Choose an option (1-7): ").strip()
        if choice == "1":
            df = read_db()
            if df.empty:
                print("Database is empty")
            else:
                print("\nCurrent database content:")
                print(df.to_string(index=False))
        elif choice == "2":
            add_new_user()
        elif choice == "3":
            delete_user()
        elif choice == "4":
            update_user()
        elif choice == "5":
            show_statistics()
        elif choice == "6":
            draw_scatter()
        elif choice == "7":
            print("Program ended")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


if __name__ == '__main__':
    main()
