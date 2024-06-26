package repositories

import (
	"auth_microservice/internal/models"
	"auth_microservice/db"
	"database/sql"
)

type AuthenticationRepository struct{}

func (r *AuthenticationRepository) GetUserByUsername(username string) (*models.User, error) {
	var user models.User
	// Izvršavanje SQL upita za dobijanje korisnika iz baze podataka
	err := db.DB.QueryRow("SELECT id, username, password, role FROM users WHERE username = $1", username).
		Scan(&user.ID, &user.Username, &user.Password, &user.Role)
	if err != nil {
		if err == sql.ErrNoRows {
			// Korisnik nije pronađen
			return nil, nil
		}
		// Greška prilikom izvršavanja SQL upita
		return nil, err
	}

	return &user, nil
}