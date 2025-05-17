from database import add_contact, get_contacts

def add_worker(name, phone):
    add_contact(name, phone)

def fetch_contacts():
    return get_contacts()

if __name__ == "__main__":
    add_worker('Bob', '+987654321')
    print(list(fetch_contacts()))
