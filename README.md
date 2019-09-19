
## DB
    psql -U postgres -c "CREATE DATABASE survey"
    psql -U postgres -c "CREATE USER survey WITH ENCRYPTED PASSWORD 'surveysurvey';"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE survey TO survey;"

## DB TEST
    psql -U postgres -c "CREATE DATABASE survey_test"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE survey_test TO survey;"
    
#### Redo DB
    psql -U postgres -c "DROP DATABASE survey"
    psql -U postgres -c "CREATE DATABASE survey"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE survey TO survey;"