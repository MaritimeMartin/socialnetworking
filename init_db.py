from datamodel import DB

if __name__ == "__main__":
    DB.bind(provider="sqlite", filename="db_model.sqlite", create_db=True)
    DB.generate_mapping(create_tables=True)
