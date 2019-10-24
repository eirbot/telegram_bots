#! /bin/env python

"""
Methods to add and list stuff borrowed.
Stuff borrowed is stored in a .csv file with the following format:
> Description of the object, Name of the borrower,
    Date of borrow, State, Date of return

State is one of the following : AWAY, RETURNED
"""

import csv
import time

VALID_STATES = [
    "AWAY",
    "RETURNED"
]


class BorrowList:
    "An object to work with borrow list"

    def __init__(self, filename=".borrow_store"):
        self.store = []
        self.filename = filename
        self.load()

    def load(self):
        """Load data in self.filename inside self.store"""
        try:
            with open(self.filename, newline='') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    self.add(Borrow(*row))
        except FileNotFoundError:
            pass  # nothing to load

    def save(self):
        """Save data from self.store into self.filename"""
        with open(self.filename, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for b in self.store:
                csv_writer.writerow(b.data.values())

    def add(self, borrow):
        """Add an entry to the BorrowList"""
        self.store.append(borrow)
        self.save()

    def borrowed_items(self):
        """Return a list of Borrow still borrowed"""
        return [b for b in self.store if b.isBorrowed()]

    def len(self):
        """Return the number of objects in the store"""
        return len(self.store)


class Borrow:
    "A only borrow"

    def __init__(self, description=None, borrower_name=None,
                 borrow_date=time.time(), state=None, return_date=None):
        if state:
            if state not in VALID_STATES:
                raise TypeError("State should be one of {}".format(
                    VALID_STATES.__str__()))
        else:
            state = "AWAY"

        self.data = {
            "description": description,
            "borrower_name": borrower_name,
            "borrow_date": borrow_date,
            "state": state,
            "returned_date": return_date,
        }

    def __repr__(self):
        return "The object **{}** has been borrowed by **{}**".format(
            self.data["description"], self.data["borrower_name"])

    def isReturned(self):
        """Return whether the borrow is returned"""
        return self.state == "RETURNED"

    def isBorrowed(self):
        """Return whether the borrow is borrowed"""
        return self.state == "AWAY"

    def setReturned(self):
        """Set the borrow as returned"""
        self.state = "RETURNED"


if __name__ == '__main__':
    Store = BorrowList()
    print("BorrowList created")
    first_borrow = Borrow("Un tournevis", "Alban Chauvel")
    print("Created a borrow : {}".format(first_borrow))
    Store.add(first_borrow)
    print("The BorrowList now contain {} item{}.".format(
        Store.len(),
        "" if Store.len() <= 1 else "s"))
