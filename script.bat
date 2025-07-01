@echo off
REM Удаляет все данные из таблицы canvas_events
SET PGPASSWORD=postgres
psql "postgresql://postgres:postgres@localhost:5432/postgres" -c "DELETE FROM \"canvas_events\";"