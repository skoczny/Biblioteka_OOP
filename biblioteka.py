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

    def borrowed_count(self):
        return self._total_copies - self._available_copies
 
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
        self.reservations = []
 
    def menu(self):
        print(f"\nMenu czytelnika ({self.login})")
        print("1. Przeglądaj katalog")
        print("2. Szukaj książki")
        print("3. Sortuj katalog")
        print("4. Wypożycz książkę")
        print("5. Zwróć książkę")
        print("6. Moje wypożyczenia")
        print("7. Poproś o przedłużenie")
        print("8. Zarezerwuj niedostępną książkę")
        print("0. Wyloguj")
 
 
class Librarian(User):
 
    def __init__(self, login, password):
        super().__init__(login, password, "bibliotekarz")
 
    def menu(self):
        print(f"\nMenu bibliotekarza ({self.login})")
        print("1. Przeglądaj katalog")
        print("2. Szukaj książki")
        print("3. Sortuj katalog")
        print("4. Lista wszystkich wypożyczeń")
        print("5. Obsługa próśb o przedłużenie")
        print("6. Statystyki")
        print("0. Wyloguj")
 
 
class Library:
 
    def __init__(self):
        self._books = []
        self._users = []
        self._extension_queue = []
        self._reservation_queue = []
 
    def add_book(self, book):
        self._books.append(book)
 
    def add_user(self, user):
        self._users.append(user)
 
    def get_all_books(self):
        return list(self._books)

    def display_filtered(self, predicate, label):
        results = list(filter(predicate, self._books))
        if not results:
            print(f"Brak wyników dla {label}")
            return []
        print(f"\n {label} ({len(results)})")
        [print(f" {i}. {book}") for i, book in enumerate(results, 1)]
        return results
 
    def search_books(self, query):
        query_lower = query.lower()
        return self.display_filtered(
            lambda b: query_lower in b.title.lower() or query_lower in b.author.lower(),
            f"Wyniki dla: '{query}'"
        )

    def show_available(self):
        return self.display_filtered(
            lambda b: b.is_available(),
            "Dostępne książki"
        )
    
    def sort_books(self, sort_key):
        sort_options = {
            "1": (lambda b: b.title.lower(), "tytuł"),
            "2": (lambda b: b.author.lower(), "autor"),
            "3": (lambda b: b.get_available_copies(), "dostępne egzemplarze"),
        }
        if sort_key not in sort_options:
            print("Nieprawidłowa opcja sortowania.")
            return
        key_fn, label = sort_options[sort_key]
        sorted_books = sorted(self._books, key=key_fn)
        print(f"\nKatalog posortowany wg: {label}")
        [print(f" {i}. {book}") for i, book in enumerate(sorted_books, 1)]
 
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
        self._reservation_queue = [
            (r, b) for r, b in self._reservation_queue if not (r is reader and b is book)
        ]
        if book in reader.reservations:
            reader.reservations.remove(book)
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
        waiting = [r for r, b in self._reservation_queue if b is book]
        if waiting:
            print(f"Zwrócono: {book.title} (uwaga: {len(waiting)} os. czeka na rezerwację)")
        else:
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

    def reserve_book(self, reader, book):
        if book.is_available():
            print("Ksiąka jest dostępna - wypoycz ją zamiast rezerwować.")
            return
        if book in reader.borrowed_books:
            print("Masz już tę książkę wypożyczoną.")
            return
        if any(r is reader and b is book for r, b in self._reservation_queue):
            print("Już złożyłeś rezerwację tej książki.")
            return
        self._reservation_queue.append((reader, book))
        reader.reservations.append(book)
        print(f'Zarezerwowano: "{book.title}". Otrzymasz powiadomienie, gdy książka będzie dostępna.')

    def has_reservation(self, book):
        return [r.login for r, b in self._reservation_queue if b is book]
 
    def get_all_borrowings(self):
        return [(u, b) for u in self._users if isinstance(u, Reader) for b in u.borrowed_books]

    def get_statistics(self):
        most_popular = max(self._books, key=lambda b: b.borrowed_count()) if self._books else None

        total_borrowings = sum(len(r.borrowed_books) for r in self._users if isinstance(r, Reader))

        readers_sorted = sorted(
            [u for u in self._users if isinstance(u, Reader)],
            key=lambda r: len(r.borrowed_books),
            reverse=True
        )

        return {
            "most_popular": most_popular,
            "total_borrowings": total_borrowings,
            "readers_ranked": readers_sorted,
        }
 
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
            print("1. Wszystkie  2. Tylko dostępne")
            sub = input("Wybór: ").strip()
            if sub == "2":
                library.show_available()
            else:
                library.display_filtered(lambda b: True, "Cały katalog")
 
        elif choice == "2":
            query = input("Szukaj (tytuł/autor): ").strip()
            if query:
                library.search_books(query)
 
        elif choice == "3":
            print("Sortuj wg: 1. Tytuł  2. Autor  3. Dostępne sztuki")
            sort_key = input("Wybór: ").strip()
            library.sort_books(sort_key)
 
        elif choice == "4":
            available = list(filter(lambda b: b.is_available(), library.get_all_books()))
            book = choose_book_from_list(available)
            if book:
                try:
                    library.borrow_book(reader, book)
                except ValueError as e:
                    print(e)
 
        elif choice == "5":
            if not reader.borrowed_books:
                print("Nie masz wypożyczonych książek.")
                continue
            book = choose_book_from_list(list(reader.borrowed_books))
            if book:
                library.return_book(reader, book)
 
        elif choice == "6":
            if not reader.borrowed_books:
                print("Nie masz wypożyczonych książek.")
            else:
                print("\n--- Moje wypożyczenia ---")
                [print(f"  {i}. {b.title} — {b.author}") for i, b in enumerate(reader.borrowed_books, 1)]

        elif choice == "7":
            if not reader.borrowed_books:
                print("Nie masz wypożyczonych książek.")
                continue
            book = choose_book_from_list(
                list(reader.borrowed_books),
                "Którą książkę chcesz przedłużyć? (0 = anuluj): "
            )
            if book:
                library.request_extension(reader, book)

        elif choice == "8":
            unavailable = list(filter(lambda b: not b.is_available(), library.get_all_books()))
            if not unavailable:
                print("Wszystkie książki są dostępne.")
                continue
            book = choose_book_from_list(
                unavailable,
                "Którą książkę chcesz zarezerwować? (0 = anuluj): "
            )
            if book:
                library.reserve_book(reader, book)
 
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
            print("1. Wszystkie  2. Tylko dostępne")
            sub = input("Wybór: ").strip()
            if sub == "2":
                library.show_available()
            else:
                library.display_filtered(lambda b: True, "Cały katalog")
 
        elif choice == "2":
            query = input("Szukaj (tytuł/autor): ").strip()
            if query:
                library.search_books(query)
 
        elif choice == "3":
            print("Sortuj wg: 1. Tytuł  2. Autor  3. Dostępne sztuki")
            sort_key = input("Wybór: ").strip()
            library.sort_books(sort_key)
 
        elif choice == "4":
            borrowings = library.get_all_borrowings()
            if not borrowings:
                print("Brak aktywnych wypożyczeń.")
            else:
                print("\n--- Wszystkie wypożyczenia ---")
                [print(f'  {i}. "{b.title}" — wypożyczona przez: {r.login}')
                 for i, (r, b) in enumerate(borrowings, 1)]
        
        elif choice == "5":
            requests = library.get_extension_requests()
            if not requests:
                print("Brak próśb o przedłużenie.")
                continue
            print("\n--- Prośby o przedłużenie ---")
            for i, (reader, book) in enumerate(requests, 1):
                reservations = library.has_reservation(book)
                res_info = f" [REZERWACJA: {', '.join(reservations)}]" if reservations else ""
                print(f'  {i}. {reader.login} prosi o przedłużenie: "{book.title}"{res_info}')
            try:
                idx = int(input("Numer prośby do obsłużenia (0 = anuluj): "))
                if idx == 0:
                    continue
                decision = input("Zaakceptować? (t/n): ").strip().lower()
                library.handle_extension(idx - 1, decision == "t")
            except (ValueError, IndexError):
                print("Nieprawidłowy wybór.")

        elif choice == "6":
            stats = library.get_statistics()
            print("\n--- Statystyki ---")
            if stats["most_popular"]:
                mp = stats["most_popular"]
                print(f"  Najpopularniejsza książka: \"{mp.title}\" "
                      f"(wypożyczone: {mp.borrowed_count()}/{mp.get_total_copies()})")
            print(f"  Aktywne wypożyczenia ogółem: {stats['total_borrowings']}")
            print("  Czytelnicy wg liczby wypożyczeń:")
            [print(f"    {i}. {r.login} — {len(r.borrowed_books)} książek")
             for i, r in enumerate(stats["readers_ranked"], 1)]
 
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