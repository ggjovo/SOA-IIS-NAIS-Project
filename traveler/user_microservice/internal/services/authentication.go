package services

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"user_microservice/db"
	"user_microservice/internal/models"
	"user_microservice/internal/utils"
	invoicer "user_microservice/invoicer"
)

var jwtKey = []byte("tajni_kljuc_za_jwt_token")
var token = ""

type UserServiceGRPC struct {
	invoicer.UnimplementedUserServiceServer
}

// Funkcija koja simulira rad sa bazom podataka
func GetUserByUsername(username string) (*models.User, error) {
	var user models.User
	// Izvršavanje SQL upita za dobijanje korisnika iz baze podataka
	err := db.DBGRPC.QueryRow("SELECT id, username, password, role FROM users WHERE username = $1", username).
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

// Funkcija za postavljanje JWT tokena u promenljivu
func SetToken(tokenString string) {
	token = tokenString
}

func (s *UserService) LoginUser(w http.ResponseWriter, r *http.Request) {
	_, err := utils.CheckTokenAndUserInfo(r)
	if err == nil {
		// Korisnik je već ulogovan, ne dozvoljavamo logovanje
		http.Error(w, "Već ste ulogovani.", http.StatusUnauthorized)
		return
	}

	var user models.User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		http.Error(w, "Greška prilikom dekodiranja korisničkih podataka", http.StatusBadRequest)
		return
	}

	authURL := "http://auth-microservice:8081/tokenize"
	jsonData, err := json.Marshal(user)
	if err != nil {
		http.Error(w, "Greška prilikom enkodiranja korisničkih podataka", http.StatusInternalServerError)
		return
	}

	resp, err := http.Post(authURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Println("Greška prilikom slanja zahteva ka auth mikroservisu:", err)
		http.Error(w, "Greška prilikom slanja zahteva ka auth mikroservisu", http.StatusInternalServerError)
		return
	}

	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		http.Error(w, fmt.Sprintf("Neuspešna autentifikacija: %s", resp.Status), resp.StatusCode)
		return
	}

	var tokenData map[string]string
	if err := json.NewDecoder(resp.Body).Decode(&tokenData); err != nil {
		http.Error(w, "Greška prilikom dekodiranja odgovora od auth mikroservisa", http.StatusInternalServerError)
		return
	}

	token, ok := tokenData["token"]
	if !ok {
		http.Error(w, "Nije primljen JWT token od auth mikroservisa", http.StatusInternalServerError)
		return
	}

	// Postavljanje JWT tokena kao kolačića u HTTP odgovoru
	expirationTime := time.Now().Add(24 * time.Hour)
	http.SetCookie(w, &http.Cookie{
		Name:     "token",
		Value:    token,
		Expires:  expirationTime,
		Domain:   "localhost", // Podesite na odgovarajući domen
		Path:     "/",         // Podesite na odgovarajuću putanju
		HttpOnly: false,
	})

	// Slanje poruke o uspešnoj prijavi korisnika
	message := fmt.Sprintf("Korisnik %s je uspešno prijavljen!\n", user.Username)
	w.Write([]byte(message))

	// Slanje JWT tokena kao odgovor na uspešnu prijavu
	w.Write([]byte("JWT token: " + token))
}

func (s *UserService) LogoutUser(w http.ResponseWriter, r *http.Request) {
	// Brisanje JWT tokena iz kolačića
	http.SetCookie(w, &http.Cookie{
		Name:   "token",
		MaxAge: -1,
	})
}
