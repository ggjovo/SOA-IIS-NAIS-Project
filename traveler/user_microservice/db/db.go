package db

import (
	"database/sql"

	_ "github.com/lib/pq"
)

var DB *sql.DB
var DBGRPC *sql.DB

// InitDB za gRPC
func InitDBGRPC() error {
	var err error
	DBGRPC, err = sql.Open("postgres", "postgresql://postgres:postgres@postgres/postgres?sslmode=disable")
	if err != nil {
		return err
	}
	return nil
}

func InitDB() error {
	// Inicijalizujte vezu sa bazom podataka
	var err error
	DB, err = sql.Open("postgres", "postgresql://postgres:postgres@postgres/postgres?sslmode=disable")
	if err != nil {
		return err
	}
	return nil
}
