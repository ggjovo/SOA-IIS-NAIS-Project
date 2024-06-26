package utils

import (
	"auth_microservice/internal/models"
	"context"
	"errors"
	"net/http"

	"github.com/dgrijalva/jwt-go"
)

var jwtKey = []byte("tajni_kljuc_za_jwt_token")

func CheckToken(r *http.Request) (*models.Claims, error) {
	cookie, err := r.Cookie("token")

	if err != nil {
		if err == http.ErrNoCookie {
			return nil, err
		}
		return nil, err
	}

	tokenStr := cookie.Value
	claims := &models.Claims{}

	token, err := jwt.ParseWithClaims(tokenStr, claims, func(token *jwt.Token) (interface{}, error) {
		return jwtKey, nil
	})
	if err != nil {
		return nil, err
	}
	if !token.Valid {
		return nil, errors.New("invalid token")
	}
	return claims, nil
}

func CheckTokenGRPC(ctx context.Context, tokenStr string) (*models.Claims, error) {
	// Izvadite JWT token iz konteksta
	if tokenStr == "" {
		return nil, errors.New("token not found in context")
	}

	// Parsiranje JWT tokena
	claims := &models.Claims{}
	token, err := jwt.ParseWithClaims(tokenStr, claims, func(token *jwt.Token) (interface{}, error) {
		return jwtKey, nil
	})
	if err != nil {
		return nil, err
	}
	if !token.Valid {
		return nil, errors.New("invalid token")
	}

	// Ako je token validan, vraćamo podatke o claims-ima
	return claims, nil
}
