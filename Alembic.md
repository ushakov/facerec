# When you modify DB schema, you need to run the following commands:

# Generate a new migration file
```
alembic revision --autogenerate -m "<commit message>"
```

# Apply the changes to the database
```
alembic upgrade head
```
