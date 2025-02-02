import psycopg2
import os

def connect_to_db():
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(
            dbname="legiscan_api",
            user="legiscan_api",
            password="password",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_document_for_state(conn, state):
    try:
        # Open a cursor to perform database operations
        cur = conn.cursor()
        
        # Execute a query which looks for all engrossed/enrolled/passed bills in a particular state
        query = f"SELECT ls_bill.title, ls_bill.description, ls_bill.status_date, ls_bill.status_id FROM ls_bill JOIN ls_state ON ls_bill.state_id = ls_state.state_id WHERE ls_state.state_name = '{state}' AND ls_bill.status_id IN (2, 3, 4)"

        cur.execute(query)
        
        # Retrieve query results
        records = cur.fetchall()
        
        # Create a document for the state
        file = open(f"{state}_bills.txt", "w")
        file.write(f"Below are the bills that have been engrossed, enrolled, or passed in the state of {state}:\n")

        # Add each record
        for record in records:
            verb = "engrossed" if record[3] == 2 else "enrolled" if record[3] == 3 else "passed"
            year = str(record[2].year)
            file.write(f"In {year}, {state} {verb} a bill titled: {record[0]}. Description: {record[1]}\n")
        
        # Close communication with the database
        cur.close()
    except Exception as e:
        print(f"Error fetching data: {e}")

def main():
    conn = connect_to_db()
    if conn:
        # Create a directory to store state data if it doesn't exist
        output_dir = "state_data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Change the working directory to the output directory
        os.chdir(output_dir)

        states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
        for state in states:
            create_document_for_state(conn, state)
        # create_document_for_state(conn, 'Alabama')
        conn.close()

if __name__ == "__main__":
    main()