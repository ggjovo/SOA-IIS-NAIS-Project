package services

import (
	"context"
	"encoding/json"
	"net/http"
	"strconv"
	"time"

	"auth_microservice/internal/models"
	"auth_microservice/internal/repositories"
	"auth_microservice/internal/utils"

	invoicer "auth_microservice/invoicer"

	"auth_microservice/db"
	"database/sql"

	"github.com/dgrijalva/jwt-go"
	"golang.org/x/crypto/bcrypt"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/emptypb"
)

var jwtKey = []byte("tajni_kljuc_za_jwt_token")
var token = ""

type AuthenticationService struct {
	AuthenticationRepository *repositories.AuthenticationRepository
}

type AuthenticationServiceGRPC struct {
	invoicer.UnimplementedAuthenticationServiceServer
}

func (s *AuthenticationServiceGRPC) LoginGRPC(ctx context.Context, req *invoicer.User) (*invoicer.LoginResponse, error) {
	// Pozivanje repozitorijuma za dobijanje korisnika iz baze podataka
	dbUser, err := GetUserByUsername(req.Username)
	if err != nil {
		return nil, err
	}

	// Provera korisničkih kredencijala
	if dbUser == nil || bcrypt.CompareHashAndPassword([]byte(dbUser.Password), []byte(req.Password)) != nil {
		return nil, status.Errorf(codes.Unauthenticated, "Pogrešno korisničko ime ili lozinka")
	}

	// Generisanje JWT tokena
	expirationTime := time.Now().Add(24 * time.Hour)
	claims := &models.Claims{
		Id:       strconv.Itoa(dbUser.ID),
		Username: req.Username,
		Role:     dbUser.Role,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: expirationTime.Unix(),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(jwtKey)
	if err != nil {
		return nil, err
	}

	SetToken(tokenString)

	// Slanje JWT tokena kao odgovor na uspešnu prijavu
	response := &invoicer.LoginResponse{
		Token: tokenString,
	}
	return response, nil
}

func SetToken(tokenString string) {
	token = tokenString
}

// Funkcija GetUserByUsername koja simulira rad sa bazom podataka
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

func (s *AuthenticationServiceGRPC) LogoutUserGRPC(ctx context.Context, req *emptypb.Empty) (*invoicer.LogoutResponse, error) {
	SetToken("")
	response := &invoicer.LogoutResponse{
		Message: "Korisnik je uspešno odjavljen.",
	}
	return response, nil
}

func (s *AuthenticationServiceGRPC) CheckTokenGRPC(ctx context.Context, req *emptypb.Empty) (*invoicer.CheckTokenResponse, error) {
	// Provera ispravnosti JWT tokena
	_, err := utils.CheckTokenGRPC(ctx, token)
	if err != nil {
		response := &invoicer.CheckTokenResponse{
			Valid: false,
		}
		return response, nil
	}

	// Token je validan
	response := &invoicer.CheckTokenResponse{
		Valid: true,
	}
	return response, nil
}

func (s *AuthenticationServiceGRPC) GetUserInfoGRPC(ctx context.Context, req *emptypb.Empty) (*invoicer.UserInfo, error) {
	// Provera ispravnosti JWT tokena
	claims, err := utils.CheckTokenGRPC(ctx, token)
	if err != nil {
		return nil, status.Errorf(codes.Unauthenticated, "Nevalidan token")
	}

	// Kreiranje informacija o korisniku
	userInfo := &invoicer.UserInfo{
		Id:       claims.Id,
		Username: claims.Username,
		Role:     claims.Role,
	}
	return userInfo, nil
}

func (s *AuthenticationService) LoginHandler(w http.ResponseWriter, r *http.Request) {
	r.Body = http.MaxBytesReader(w, r.Body, 1048576)
	defer r.Body.Close()

	var user models.User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		http.Error(w, "Greška prilikom dekodiranja korisničkih podataka", http.StatusBadRequest)
		return
	}

	// Pozivanje repozitorijuma za dobijanje korisnika iz baze podataka
	dbUser, err := s.AuthenticationRepository.GetUserByUsername(user.Username)
	if err != nil {
		http.Error(w, "Greška prilikom provere korisničkih kredencijala", http.StatusInternalServerError)
		return
	}

	// Provera korisničkih kredencijala
	if dbUser == nil || bcrypt.CompareHashAndPassword([]byte(dbUser.Password), []byte(user.Password)) != nil {
		http.Error(w, "Pogrešno korisničko ime ili lozinka", http.StatusUnauthorized)
		return
	}

	// Generisanje JWT tokena
	expirationTime := time.Now().Add(24 * time.Hour)
	claims := &models.Claims{
		Id:       strconv.Itoa(dbUser.ID),
		Username: user.Username,
		Role:     dbUser.Role,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: expirationTime.Unix(),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(jwtKey)
	if err != nil {
		http.Error(w, "Greška prilikom generisanja JWT tokena", http.StatusInternalServerError)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "token",
		Value:    tokenString,
		Expires:  expirationTime,
		Domain:   "localhost", // Podesite na odgovarajući domen
		Path:     "/",         // Podesite na odgovarajuću putanju
		HttpOnly: false,
	})

	// Slanje JWT tokena kao odgovor na uspešnu prijavu
	response := map[string]interface{}{
		"token": tokenString,
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func (s *AuthenticationService) HandleCheckToken(w http.ResponseWriter, r *http.Request) {
	_, err := utils.CheckToken(r)
	if err != nil {
		// Handle error (for example, token not found or invalid)
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	// Token is valid, you can return a 200 OK response or something else as needed
	w.Write([]byte("Token is valid"))
}

func (s *AuthenticationService) GetUserInfo(w http.ResponseWriter, r *http.Request) {
	// Parse JWT token
	claims, err := utils.CheckToken(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	// Create user info object
	userInfo := models.UserInfo{
		Username: claims.Username,
		Role:     claims.Role,
	}

	// Encode user info object as JSON and send it in the response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(userInfo)
}
