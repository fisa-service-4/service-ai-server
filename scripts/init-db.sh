#!/bin/bash
# analytics DB 생성 (없을 때만)
psql -U "$POSTGRES_USER" -tc "SELECT 1 FROM pg_database WHERE datname = 'analytics'" | grep -q 1 || \
psql -U "$POSTGRES_USER" -c "CREATE DATABASE analytics;"
