package utils

import (
	"errors"
	"net/http"
	"user_microservice/internal/models"

	"github.com/dgrijalva/jwt-go"
)

var jwtKey = []byte("tajni_kljuc_za_jwt_token")

// CheckTokenAndUserInfo parses the JWT token and retrieves user information.
func CheckTokenAndUserInfo(r *http.Request) (*models.UserInfo, error) {
	userInfo, err := GetUserInfoFromAuth(r)
	if err != nil {
		return nil, err
	}
	return userInfo, nil
}

// GetUserInfoFromAuth retrieves user information from the JWT token stored in the request cookie.
func GetUserInfoFromAuth(r *http.Request) (*models.UserInfo, error) {
	// Get JWT token from cookie
	cookie, err := r.Cookie("token")
	if err != nil {
		return nil, err
	}
	tokenString := cookie.Value

	// Parse JWT token
	claims := &models.Claims{}
	token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		return jwtKey, nil
	})
	if err != nil {
		return nil, err
	}
	if !token.Valid {
		return nil, errors.New("invalid token")
	}

	// Create user info object
	userInfo := &models.UserInfo{
		Id:       claims.Id,
		Username: claims.Username,
		Role:     claims.Role,
		// Add other fields if needed
	}

	return userInfo, nil
}
