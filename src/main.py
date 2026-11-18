"""Terminal interface for viewing pets and adopting from the species store."""

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "database" / "pet.db"
STORE_REFRESH_HOURS = 12


def connect_database():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_or_create_store(connection):
    """Return four species IDs, keeping the same selection for 12 hours."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS AdoptionStore (
            slot INTEGER PRIMARY KEY,
            species_id INTEGER NOT NULL,
            selected_at TEXT NOT NULL,
            FOREIGN KEY (species_id) REFERENCES Species(id)
        )
        """
    )

    now = datetime.now()
    rows = connection.execute(
        "SELECT species_id, selected_at FROM AdoptionStore ORDER BY slot"
    ).fetchall()

    store_is_current = len(rows) == 4
    if store_is_current:
        selected_at = datetime.fromisoformat(rows[0][1])
        store_is_current = now - selected_at < timedelta(hours=STORE_REFRESH_HOURS)

    if store_is_current:
        species_ids = [row[0] for row in rows]
        species_count = connection.execute("SELECT COUNT(*) FROM Species").fetchone()[0]
        species_ids_exist = all(
            connection.execute("SELECT 1 FROM Species WHERE id = ?", (species_id,)).fetchone()
            for species_id in species_ids
        )
        if species_ids_exist and species_count:
            return species_ids

    species_ids = [row[0] for row in connection.execute("SELECT id FROM Species").fetchall()]
    if not species_ids:
        return []

    choices = [random.choice(species_ids) for _ in range(4)]
    selected_at = now.isoformat(timespec="seconds")
    connection.execute("DELETE FROM AdoptionStore")
    connection.executemany(
        "INSERT INTO AdoptionStore (slot, species_id, selected_at) VALUES (?, ?, ?)",
        [(slot, species_id, selected_at) for slot, species_id in enumerate(choices, start=1)],
    )
    connection.commit()
    return choices


def authenticate(connection):
    username = input("Username: ").strip()
    password = input("Password: ")
    user = connection.execute(
        "SELECT id FROM User WHERE username = ? AND password = ?",
        (username, password),
    ).fetchone()
    if user is None:
        print("Invalid username or password.")
        return None
    return user[0]


def view_pets(connection, owner_id):
    pets = connection.execute(
        """
        SELECT Pets.name, Species.name, Species.emoji,
               Pets.hunger, Pets.happiness, Pets.energy, Pets.xp, Pets.level
        FROM Pets
        JOIN Species ON Pets.species_id = Species.id
        WHERE Pets.owner_id = ?
        ORDER BY Pets.id
        """,
        (owner_id,),
    ).fetchall()

    if not pets:
        print("You don't have any pets yet.")
        return

    for name, species, emoji, hunger, happiness, energy, xp, level in pets:
        print(f"\n{name} ({emoji} {species})")
        print(f"  Hunger: {hunger} | Happiness: {happiness} | Energy: {energy}")
        print(f"  XP: {xp} | Level: {level}")


def adoption_store(connection, owner_id):
    latest_adoption = connection.execute(
        "SELECT MAX(born_at) FROM Pets WHERE owner_id = ?",
        (owner_id,),
    ).fetchone()[0]
    pet_count = connection.execute(
        "SELECT COUNT(*) FROM Pets WHERE owner_id = ?",
        (owner_id,),
    ).fetchone()[0]

    adopted_recently = pet_count == 0
    if latest_adoption:
        if datetime.now() - datetime.fromisoformat(latest_adoption) < timedelta(hours=12):
            adopted_recently = True

    if not adopted_recently:
        print("Come back another time to check the adoption store.")
        return

    species_ids = get_or_create_store(connection)
    if not species_ids:
        print("There are no species available in the adoption store.")
        return

    species_by_id = {
        row[0]: row[1:]
        for row in connection.execute(
            "SELECT id, name, emoji FROM Species WHERE id IN ({})".format(
                ",".join("?" for _ in set(species_ids))
            ),
            tuple(set(species_ids)),
        ).fetchall()
    }

    print("\nAdoption Store (refreshes every 12 hours)")
    for option, species_id in enumerate(species_ids, start=1):
        name, emoji = species_by_id[species_id]
        print(f"{option}. {emoji} {name}")

    choice = input("Choose a species number to adopt, or press Enter to go back: ").strip()
    if not choice:
        return
    if not choice.isdigit() or not 1 <= int(choice) <= len(species_ids):
        print("That isn't a valid store option.")
        return

    species_id = species_ids[int(choice) - 1]
    pet_name = input("What would you like to name your pet? ").strip()
    if not pet_name:
        print("A pet name is required; adoption cancelled.")
        return

    connection.execute(
        "INSERT INTO Pets (owner_id, species_id, name) VALUES (?, ?, ?)",
        (owner_id, species_id, pet_name),
    )
    connection.commit()
    print(f"You adopted {pet_name}!")


def main():
    try:
        connection = connect_database()
    except sqlite3.Error as error:
        print(f"Could not open the database: {error}")
        return

    try:
        owner_id = authenticate(connection)
        if owner_id is None:
            return

        while True:
            print("\n1. View Pets")
            print("2. Check Adoption Store")
            print("3. Exit")
            option = input("Choose an option: ").strip()

            if option == "1":
                view_pets(connection, owner_id)
            elif option == "2":
                adoption_store(connection, owner_id)
            elif option == "3":
                break
            else:
                print("Choose 1, 2, or 3.")
    except sqlite3.Error as error:
        print(f"Database error: {error}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
