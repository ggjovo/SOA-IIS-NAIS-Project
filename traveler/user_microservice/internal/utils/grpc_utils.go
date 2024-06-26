package utils

import (
	"context"
	"database/sql"
	"user_microservice/db"
	"user_microservice/internal/models"
	"user_microservice/invoicer"

	"github.com/dgrijalva/jwt-go"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func CheckTokenAndUserInfoGRPC(ctx context.Context, tokenStr string) (*invoicer.UserInfo, error) {
	// Implementacija funkcije za proveru JWT tokena i dobijanje korisničkih informacija
	userInfo, err := GetUserInfoFromAuthGRPC(ctx, tokenStr)
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}
	return &invoicer.UserInfo{
		Username: userInfo.Username,
		Role:     userInfo.Role,
	}, nil
}

func GetUserInfoFromAuthGRPC(ctx context.Context, tokenStr string) (*invoicer.UserInfo, error) {
	// Implementacija funkcije za dobijanje korisničkih informacija iz JWT tokena
	if tokenStr == "" {
		return nil, status.Error(codes.Unauthenticated, "JWT token missing")
	}

	claims := &models.Claims{}
	token, err := jwt.ParseWithClaims(tokenStr, claims, func(token *jwt.Token) (interface{}, error) {
		return jwtKey, nil
	})
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}
	if !token.Valid {
		return nil, status.Error(codes.Unauthenticated, "Invalid token")
	}

	userInfo := &models.UserInfo{
		Id:       claims.Id,
		Username: claims.Username,
		Role:     claims.Role,
	}
	return &invoicer.UserInfo{
		Username: userInfo.Username,
		Role:     userInfo.Role,
	}, nil
}

func FindByUsernameGRPC(username string) (*models.User, error) {
	var user models.User
	err := db.DBGRPC.QueryRow("SELECT id, username, password, email, role FROM users WHERE username = $1", username).Scan(&user.ID, &user.Username, &user.Password, &user.Email, &user.Role)
	switch {
	case err == sql.ErrNoRows:
		return nil, nil
	case err != nil:
		return nil, err
	default:
		return &user, nil
	}
}

func CreateUserGRPC(user *models.User, hashedPassword []byte) error {
	_, err := db.DBGRPC.Exec("INSERT INTO users (username, password, email, role) VALUES ($1, $2, $3, $4)", user.Username, hashedPassword, user.Email, user.Role)
	return err
}

func BlockUserRepoGRPC(username string) error {
	_, err := db.DBGRPC.Exec("UPDATE users SET blocked = true WHERE username = $1", username)
	return err
}

func GetRoleByUsernameGRPC(username string) (string, error) {
	var role string
	err := db.DBGRPC.QueryRow("SELECT role FROM users WHERE username = $1", username).Scan(&role)
	return role, err
}

func GetNonAdminUsersGRPC() ([]models.User, error) {
	// Izvršavanje SQL upita za dohvatanje korisnika koji nisu administratori
	rows, err := db.DBGRPC.Query("SELECT id, username, email, role, blocked FROM users WHERE role != 'admin'")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	// Prolazak kroz rezultate i kreiranje liste korisnika
	var users []models.User
	for rows.Next() {
		var user models.User
		if err := rows.Scan(&user.ID, &user.Username, &user.Email, &user.Role, &user.Blocked); err != nil {
			return nil, err
		}
		users = append(users, user)
	}

	// Provera za greške koje se mogu desiti tokom iteracije kroz redove
	if err := rows.Err(); err != nil {
		return nil, err
	}

	return users, nil
}
