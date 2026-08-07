class Book:
    def __init__(self, ID, title, author):
        self.ID = ID
        self.title = title
        self.author = author
        self.borrowed = False
    def borrow_book(self):
        self.borrowed = True
    def return_book(self):
        self.borrowed = False
    def get_status(self):
        return "Borrowed" if self.borrowed else "Available"
    
class Library:
    def __init__(self):
        self.books = []
    def add_book(self, book):
        self.books.append(book)
    def borrow_book(self, id):
        for book in self.books:
            if book.ID == id:
                if book.borrowed:
                    print("Not available")
                else:
                    book.borrow_book()
    def return_book(self, id):
        for book in self.books:
            if book.ID == id:
                book.return_book() 
    def list_available_books(self):
        sorted_books = sorted(self.books, key=lambda x: x.ID)
        for book in sorted_books:
            if not book.borrowed:
                print(f"ID: {book.ID}, Title: {book.title}, Author: {book.author}, Status: {book.get_status()}")
    def __getitem__(self, i):
        return self.books[i]    