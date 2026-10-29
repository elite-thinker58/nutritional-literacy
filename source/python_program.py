import mysql.connector
import csv

#Connection Mysql to python
def connect_database():
    print("Connect to the nutritional_literature database")
    user_name = input("Enter MySQL username (usually root): ")
    password = input("Enter MySQL password: ")

    connection = mysql.connector.connect(
        host="localhost",
        user=user_name,
        password=password,
        database="nutritional_literature"
    )
    return connection

# It displays all the products stored in the items table.
def show_all_items(cursor):
    cursor.execute("SELECT item_id, item_name, category FROM items ORDER BY item_id")
    rows = cursor.fetchall()

    print("\n================ PRODUCT LIST ================")
    if len(rows) == 0:
        print("No products are present. Use the CSV import option first.")
    else:

        # Each column becomes wide enough for its heading and longest value.
        id_width = len("ID")
        product_width = len("Product")
        category_width = len("Category")

        for row in rows:
            if len(str(row[0])) > id_width:
                id_width = len(str(row[0]))
            if len(str(row[1])) > product_width:
                product_width = len(str(row[1]))
            if len(str(row[2])) > category_width:
                category_width = len(str(row[2]))


        # These form the table border and separate the three columns.
        border = "+-" + "-" * id_width + "-+-" + "-" * product_width
        border = border + "-+-" + "-" * category_width + "-+"
        print(border)
        print("| " + "ID".ljust(id_width) + " | "
              + "Product".ljust(product_width) + " | "
              + "Category".ljust(category_width) + " |")
        print(border)

        for row in rows:
            print("| " + str(row[0]).ljust(id_width) + " | "
                  + str(row[1]).ljust(product_width) + " | "
                  + str(row[2]).ljust(category_width) + " |")
        print(border)


# It first finds a product, then uses its item_id to show matching ingredients.
# item_id connects a product in items with its ingredients in ingredients.
def search_item(cursor):
    word = input("Enter all or part of a product name: ")
    cursor.execute(
        "SELECT item_id, item_name, category, description "
        "FROM items WHERE item_name LIKE %s",
        ("%" + word + "%",)
    )
    products = cursor.fetchall()

    if len(products) == 0:
        print("No matching product was found.")
    else:
        for product in products:
            print("\n---------- PRODUCT DETAILS ----------")
            print("Product:", product[1])
            print("Category:", product[2])
            if product[3] is not None and product[3] != "":
                print("Description:", product[3])

            cursor.execute(
                "SELECT ingredient_name, short_description, source_url "
                "FROM ingredients WHERE item_id = %s",
                (product[0],)
            )
            ingredients = cursor.fetchall()

            print("Ingredients and simple explanations:")
            if len(ingredients) == 0:
                print("No ingredient details are stored for this product.")
            else:
                for ingredient in ingredients:
                    print("\n-", ingredient[0])
                    print("  Meaning / information:", ingredient[1])
                    if ingredient[2] is not None and ingredient[2] != "":
                        print("  Source:", ingredient[2])
            print("-------------------------------------")


# The concerning_ingredients table stores general research, not a specific product.
# This lets the user search it independently by ingredient name or additive code.
def search_concerning_ingredient(cursor):
    word = input("Enter an ingredient name or code to search (or press Enter for all): ")

    if word == "":
        cursor.execute(
            "SELECT ingredient_name, ingredient_type, why_concerning, "
            "health_evidence_level, status_in_india, consumer_guidance "
            "FROM concerning_ingredients ORDER BY ingredient_name"
        )
    else:
        cursor.execute(
            "SELECT ingredient_name, ingredient_type, why_concerning, "
            "health_evidence_level, status_in_india, consumer_guidance "
            "FROM concerning_ingredients "
            "WHERE ingredient_name LIKE %s OR ingredient_type LIKE %s",
            ("%" + word + "%", "%" + word + "%")
        )

    rows = cursor.fetchall()
    print("\n======= INGREDIENT RESEARCH =======")
    if len(rows) == 0:
        print("No matching research record was found.")
    else:
        for row in rows:
            print("\nIngredient:", row[0])
            print("Type / code:", row[1])
            print("Why it is researched:", row[2])
            print("Evidence level:", row[3])
            print("India status:", row[4])
            print("Consumer guidance:", row[5])
    print("===================================")


# It adds a new product without changing or deleting existing products.
# The next item_id is one greater than the largest ID already in the table.
def add_item(connection, cursor):
    item_name = input("Enter product name: ")
    category = input("Enter product category: ")
    description = input("Enter a short description: ")

    cursor.execute("SELECT MAX(item_id) FROM items")
    result = cursor.fetchone()
    if result[0] is None:
        new_id = 1
    else:
        new_id = result[0] + 1

    cursor.execute(
        "INSERT INTO items (item_id, item_name, category, description) "
        "VALUES (%s, %s, %s, %s)",
        (new_id, item_name, category, description)
    )
    connection.commit()
    print("Product added successfully. Its item ID is", new_id)
    print("Use this same ID if to add ingredients for it.")


# It reads existing CSV data
# Prevent the same CSV rows being added repeatedly.
def import_csv_files(connection, cursor):
    imported_items = 0
    imported_ingredients = 0
    imported_concerning = 0

    # Import products from items.csv.
    try:
        with open("items.csv", "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                cursor.execute(
                    "SELECT item_id FROM items WHERE item_id = %s",
                    (row["item_id"],)
                )
                existing = cursor.fetchone()
                if existing is None:
                    cursor.execute(
                        "INSERT INTO items (item_id, item_name, category, description) "
                        "VALUES (%s, %s, %s, %s)",
                        (row["item_id"], row["item_name"], row["category"],
                         row.get("description", ""))
                    )
                    imported_items = imported_items + 1
        connection.commit()
        print("items.csv checked successfully.")
    except FileNotFoundError:
        print("Could not find items.csv in the program folder.")
        return
    except KeyError:
        print("The headings in items.csv do not match the expected headings.")
        return

    # Import product ingredients from ingredients.csv.
    try:
        with open("ingredients.csv", "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                cursor.execute(
                    "SELECT ingredient_id FROM ingredients "
                    "WHERE item_id = %s AND ingredient_name = %s",
                    (row["item_id"], row["ingredient_name"])
                )
                existing = cursor.fetchone()
                if existing is None:
                    cursor.execute("SELECT MAX(ingredient_id) FROM ingredients")
                    result = cursor.fetchone()
                    if result[0] is None:
                        new_id = 1
                    else:
                        new_id = result[0] + 1
                    cursor.execute(
                        "INSERT INTO ingredients "
                        "(ingredient_id, item_id, ingredient_name, short_description, source_url) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (new_id, row["item_id"], row["ingredient_name"],
                         row.get("short_description", ""), row.get("source_url", ""))
                    )
                    imported_ingredients = imported_ingredients + 1
        connection.commit()
        print("ingredients.csv checked successfully.")
    except FileNotFoundError:
        print("Could not find ingredients.csv in the program folder.")
        return
    except KeyError:
        print("The headings in ingredients.csv do not match the expected headings.")
        return

    # Import independent ingredient/additive research.
    try:
        with open("concerning_ingredients_india.csv", "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                cursor.execute(
                    "SELECT concerning_id FROM concerning_ingredients "
                    "WHERE ingredient_name = %s",
                    (row["ingredient_name"],)
                )
                existing = cursor.fetchone()
                if existing is None:
                    cursor.execute("SELECT MAX(concerning_id) FROM concerning_ingredients")
                    result = cursor.fetchone()
                    if result[0] is None:
                        new_id = 1
                    else:
                        new_id = result[0] + 1
                    cursor.execute(
                        "INSERT INTO concerning_ingredients "
                        "(concerning_id, ingredient_name, ingredient_type, "
                        "common_food_context, why_concerning, health_evidence_level, "
                        "status_in_india, status_in_other_countries, consumer_guidance, source_urls) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (new_id, row["ingredient_name"], row.get("ingredient_type", ""),
                         row.get("common_food_context", ""), row.get("why_concerning", ""),
                         row.get("health_evidence_level", ""), row.get("status_in_india", ""),
                         row.get("status_in_other_countries", ""),
                         row.get("consumer_guidance", ""), row.get("source_urls", ""))
                    )
                    imported_concerning = imported_concerning + 1
        connection.commit()
        print("concerning_ingredients_india.csv checked successfully.")
    except FileNotFoundError:
        print("Could not find concerning_ingredients_india.csv in the program folder.")
        return
    except KeyError:
        print("The headings in concerning_ingredients_india.csv do not match.")
        return

    print("\nCSV IMPORT SUMMARY")
    print("New products added:", imported_items)
    print("New ingredient rows added:", imported_ingredients)
    print("New research rows added:", imported_concerning)


def main():
    try:
        connection = connect_database()
        cursor = connection.cursor()

        choice = ""
        while choice != "6":
            print("\n========================================")
            print("     NUTRITIONAL LITERATURE SYSTEM")
            print("========================================")
            print("1. Display all products")
            print("2. Search a product and view its ingredients")
            print("3. Search concerning ingredients / additives")
            print("4. Add a new product")
            print("5. Import CSV files into MySQL")
            print("6. Exit")
            print("========================================")

            choice = input("Enter your choice (1-6): ")

            if choice == "1":
                show_all_items(cursor)
            elif choice == "2":
                search_item(cursor)
            elif choice == "3":
                search_concerning_ingredient(cursor)
            elif choice == "4":
                add_item(connection, cursor)
            elif choice == "5":
                import_csv_files(connection, cursor)
            elif choice == "6":
                print("Thank you for using the Nutritional Literature System.")
            else:
                print("Invalid choice. Please enter a number from 1 to 6.")

        cursor.close()
        connection.close()


    # It shows a helpful message if MySQL is stopped or the login details are wrong.
    except mysql.connector.Error as error:
        print("Could not connect to or use MySQL.")
        print("Check that MySQL Server is running, the database exists, and the login is correct.")
        print("MySQL message:", error)


# It starts the menu when this file is run directly in Python IDLE.
if __name__ == "__main__":
    main()
