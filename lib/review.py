from __init__ import CURSOR, CONN
import sqlite3
from employee import Employee  # Avoid circular import issue by importing inside methods

class Review:
    # A class-level dictionary to keep track of created instances
    all = {}

    
    def __init__(self, year, summary, employee_id, id=None):
        # Validation for year
        if not isinstance(year, int):
            raise ValueError("Year must be an integer")
        if year < 2000:
            raise ValueError("Year must be greater than or equal to 2000")
        
        # Validation for summary
        if not summary or len(summary.strip()) == 0:
            raise ValueError("Summary must be a non-empty string")
        
        # Validation for employee_id
        employee = Employee.find_by_id(employee_id)  # Assuming Employee has this method
        if employee is None:
            raise ValueError(f"Employee with id {employee_id} does not exist")

        self.id = id
        self.year = year
        self.summary = summary
        self._employee_id = employee_id  # Use a private attribute to store the employee_id

    def __repr__(self):
        return f"<Review(id={self.id}, year={self.year}, summary={self.summary}, employee_id={self._employee_id})>"

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, new_employee_id):
        """Setter for employee_id with validation."""
        employee = Employee.find_by_id(new_employee_id)  # Assuming Employee has this method
        if employee is None:
            raise ValueError(f"Employee with id {new_employee_id} does not exist")
        self._employee_id = new_employee_id

    @classmethod
    def create_table(cls):
        """Create the reviews table in the database."""
        query = """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            summary TEXT NOT NULL,
            employee_id INTEGER NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );
        """
        CURSOR.execute(query)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the reviews table in the database."""
        query = "DROP TABLE IF EXISTS reviews"
        CURSOR.execute(query)
        CONN.commit()

    def save(self):
        """Save or update the review to the database."""
        if self.id is None:
            # Insert a new record
            query = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?);
            """
            CURSOR.execute(query, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid  # Update the object id to the last inserted id
            Review.all[self.id] = self  # Store in the class-level dictionary
        else:
            # Update existing record
            query = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?;
            """
            CURSOR.execute(query, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Create a new Review instance and save it to the database."""
        review = cls(year, summary, employee_id)  # Validation happens here
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
     """ Return a Review instance created from a database row """
     id, year, summary, employee_id = row
     if id in cls.all:
        return cls.all[id]
     review = cls(year, summary, employee_id, id)
     cls.all[id] = review
     return review

    @classmethod
    def find_by_id(cls, review_id):
        """Find a Review by its id."""
        query = "SELECT * FROM reviews WHERE id = ?"
        result = CURSOR.execute(query, (review_id,)).fetchone()
        if result:
            return cls.instance_from_db(result)
        return None

    def update(self):
      """ Update an existing review in the database """
      query = """
      UPDATE reviews
      SET year = ?, summary = ?, employee_id = ?
      WHERE id = ?;
      """
      CURSOR.execute(query, (self.year, self.summary, self.employee_id, self.id))
      sqlite3.connect('database.db').commit()


    def delete(self):
        """Delete a review from the database."""
        query = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(query, (self.id,))
        CONN.commit()
        del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return all reviews as a list of Review instances."""
        query = "SELECT * FROM reviews"
        rows = CURSOR.execute(query).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def get_reviews_for_employee(cls, employee_id):
        """Returns all reviews for a given employee."""
        query = "SELECT * FROM reviews WHERE employee_id = ?"
        rows = CURSOR.execute(query, (employee_id,)).fetchall()
        return [cls.instance_from_db(row) for row in rows]
