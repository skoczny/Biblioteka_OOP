class Book:
 
    def __init__(self, title, author, total_copies):
        self.title = title
        self.author = author
        self._total_copies = total_copies
        self._available_copies = total_copies
 
    def get_available_copies(self):
        return self._available_copies
 
    def get_total_copies(self):
        return self._total_copies
 
    def is_available(self):
        return self._available_copies > 0
 
    def borrow(self):
        if not self.is_available():
            raise ValueError(f"Brak dostępnych egzemplarzy: {self.title}")
        self._available_copies -= 1
 
    def return_copy(self):
        if self._available_copies >= self._total_copies:
            raise ValueError(f"Wszystkie egzemplarze już zwrócone: {self.title}")
        self._available_copies += 1
 
    def __str__(self):
        return f'"{self.title}" - {self.author} (dostępne: {self._available_copies}/{self._total_copies})'
 
 
class User:
 
    def __init__(self, login, password, role):
        self.login = login
        self._password = password
        self._role = role
 
    def get_role(self):
        return self._role
 
    def authenticate(self, password):
        return self._password == password
 
    def menu(self):
        raise NotImplementedError("Klasy pochodne muszą zaimplementować menu()")
 
    def __str__(self):
        return f"{self._role.capitalize()}: {self.login}"
 
 
class Reader(User):
 
    def __init__(self, login, password):
        super().__init__(login, password, "czytelnik")
        self.borrowed_books = []
        self.extension_requests = []
 
    def menu(self):
        print(f"\nMenu czytelnika ({self.login})")
        print("1. Przeglądaj katalog")
        print("2. Szukaj książki")
        print("3. Wypożycz książkę")
        print("4. Zwróć książkę")
        print("5. Moje wypożyczenia")
        print("6. Poproś o przedłużenie")
        print("0. Wyloguj")
 
 
class Librarian(User):
 
    def __init__(self, login, password):
        super().__init__(login, password, "bibliotekarz")
 
    def menu(self):
        print(f"\nMenu bibliotekarza ({self.login})")
        print("1. Przeglądaj katalog")
        print("2. Szukaj książki")
        print("3. Lista wszystkich wypożyczeń")
        print("4. Obsługa próśb o przedłużenie")
        print("0. Wyloguj")
 
 
class Library:
 
    def __init__(self):
        self._books = []
        self._users = []
        self._extension_queue = []
 
    def add_book(self, book):
        self._books.append(book)
 
    def add_user(self, user):
        self._users.append(user)
 
    def get_all_books(self):
        return list(self._books)
 
    def search_books(self, query):
        query_lower = query.lower()
        return [
            b for b in self._books
            if query_lower in b.title.lower() or query_lower in b.author.lower()
        ]
 
    def login(self, login, password):
        for user in self._users:
            if user.login == login and user.authenticate(password):
                return user
        return None

 
    def borrow_book(self, reader, book):
        if book in reader.borrowed_books:
            print("Masz już tę książkę wypożyczoną.")
            return
        book.borrow()
        reader.borrowed_books.append(book)
        print(f"Wypożyczono: {book.title}. Pozostało egzemplarzy: {book.get_available_copies()}")
 
    def return_book(self, reader, book):
        if book not in reader.borrowed_books:
            print("Nie masz tej książki wypożyczonej.")
            return
        book.return_copy()
        reader.borrowed_books.remove(book)
        if book in reader.extension_requests:
            reader.extension_requests.remove(book)
        self._extension_queue = [(r, b) for r, b in self._extension_queue if not (r is reader and b  is book)]
        print(f"Zwrócono: {book.title}")
 
    def request_extension(self, reader, book):
        if book not in reader.borrowed_books:
            print("Nie masz tej książki wypożyczonej.")
            return
        if book in reader.extension_requests:
            print("Już złożyłeś prośbę o przedłużenie tej książki.")
            return
        self._extension_queue.append((reader, book))
        reader.extension_requests.append(book)
        print(f"Prośba o przedłużenie książki \"{book.title}\" została wysłana.")
 
    def get_extension_requests(self):
        return list(self._extension_queue)
 
    def handle_extension(self, index, accept):
        if index < 0 or index >= len(self._extension_queue):
            print("Nieprawidłowy numer prośby.")
            return
        reader, book = self._extension_queue.pop(index)
        if book in reader.extension_requests:
            reader.extension_requests.remove(book)
        if accept:
            print(f"Zaakceptowano przedłużenie: \"{book.title}\" dla {reader.login}.")
        else:
            print(f"Odrzucono przedłużenie: \"{book.title}\" dla {reader.login}.")
 
    def get_all_borrowings(self):

        result = []
        for user in self._users:
            if isinstance(user, Reader):
                for book in user.borrowed_books:
                    result.append((user, book))
        return result
 
    def __len__(self):
        return len(self._books)
 
    def __contains__(self, title):
        return any(b.title == title for b in self._books)
 
    def __iter__(self):
        return iter(self._books)
 
 
 
def choose_book_from_list(books, prompt="Wybierz numer książki (0 = anuluj): "):
    if not books:
        print("Brak książek do wyświetlenia.")
        return None
    for i, book in enumerate(books, 1):
        print(f"  {i}. {book}")
    try:
        choice = int(input(prompt))
        if choice == 0:
            return None
        return books[choice - 1]
    except (ValueError, IndexError):
        print("Nieprawidłowy wybór.")
        return None
 
 
def reader_session(library, reader):
    while True:
        reader.menu()
        choice = input("Twój wybór: ").strip()
 
        if choice == "1":
            print("\nKatalog")
            for book in library:
                print(f"  {book}")
 
        elif choice == "2":
            query = input("Szukaj (tytuł/autor): ").strip()
            results = library.search_books(query)
            if results:
                for book in results:
                    print(f"  {book}")
            else:
                print("Nic nie znaleziono.")
 
        elif choice == "3":
            available = [b for b in library.get_all_books() if b.is_available()]
            book = choose_book_from_list(available)
            if book:
                try:
                    library.borrow_book(reader, book)
                except ValueError as e:
                    print(e)
 
        elif choice == "4":
            if not reader.borrowed_books:
                print("Nie masz wypożyczonych książek.")
                continue
            book = choose_book_from_list(list(reader.borrowed_books))
            if book:
                library.return_book(reader, book)
 
        elif choice == "5":
            if not reader.borrowed_books:
                print("Nie masz wypożyczonych książek.")
            else:
                print("\nMoje wypożyczenia")
                for i, book in enumerate(reader.borrowed_books, 1):
                    print(f"  {i}. {book.title} - {book.author}")
 
        elif choice == "6":
            if not reader.borrowed_books:
                print("Nie masz wypożyczonych książek.")
                continue
            book = choose_book_from_list(
                list(reader.borrowed_books),
                "Którą książkę chcesz przedłużyć? (0 = anuluj): "
            )
            if book:
                library.request_extension(reader, book)
 
        elif choice == "0":
            print("Wylogowano.")
            break
        else:
            print("Nieznana opcja, spróbuj ponownie.")
 
 
def librarian_session(library, librarian):
    while True:
        librarian.menu()
        choice = input("Twój wybór: ").strip()
 
        if choice == "1":
            print("\nKatalog")
            for book in library:
                print(f"  {book}")
 
        elif choice == "2":
            query = input("Szukaj (tytuł/autor): ").strip()
            results = library.search_books(query)
            if results:
                for book in results:
                    print(f"  {book}")
            else:
                print("Nic nie znaleziono.")
 
        elif choice == "3":
            borrowings = library.get_all_borrowings()
            if not borrowings:
                print("Brak aktywnych wypożyczeń.")
            else:
                print("\nWszystkie wypożyczenia")
                for i, (reader, book) in enumerate(borrowings, 1):
                    print(f"  {i}. \"{book.title}\" - wypożyczona przez: {reader.login}")
 
        elif choice == "4":
            requests = library.get_extension_requests()
            if not requests:
                print("Brak próśb o przedłużenie.")
                continue
            print("\nProśby o przedłużenie")
            for i, (reader, book) in enumerate(requests, 1):
                print(f"  {i}. {reader.login} prosi o przedłużenie: \"{book.title}\"")
            try:
                idx = int(input("Numer prośby do obsłużenia (0 = anuluj): "))
                if idx == 0:
                    continue
                decision = input("Zaakceptować? (t/n): ").strip().lower()
                library.handle_extension(idx - 1, decision == "t")
            except (ValueError, IndexError):
                print("Nieprawidłowy wybór.")
 
        elif choice == "0":
            print("Wylogowano.")
            break
        else:
            print("Nieznana opcja, spróbuj ponownie.")
 
 
def main():
    library = Library()
 
    books = [
        Book("Pan Tadeusz", "Adam Mickiewicz", 3),
        Book("Lalka", "Bolesław Prus", 2),
        Book("Ferdydurke", "Witold Gombrowicz", 1),
        Book("Solaris", "Stanisław Lem", 4),
        Book("Quo Vadis", "Henryk Sienkiewicz", 2),
    ]
    for b in books:
        library.add_book(b)
 
    users = [
        Reader("anna", "anna123"),
        Reader("jan", "jan123"),
        Librarian("admin", "admin123"),
    ]
    for u in users:
        library.add_user(u)
 
    print("SYSTEM BIBLIOTECZNY")
 
    while True:
        print("\nLogowanie (wpisz 'quit' aby wyjść)")
        login = input("Login: ").strip()
        if login.lower() == "quit":
            print("Do widzenia!")
            break
        password = input("Hasło: ").strip()
 
        user = library.login(login, password)
        if user is None:
            print("Nieprawidłowy login lub hasło.")
            continue
 
        print(f"Witaj, {user.login}! ({user.get_role()})")
 
        if isinstance(user, Reader):
            reader_session(library, user)
        elif isinstance(user, Librarian):
            librarian_session(library, user)
 
 
if __name__ == "__main__":
    main()