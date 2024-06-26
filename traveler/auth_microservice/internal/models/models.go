package models

import "github.com/dgrijalva/jwt-go"

type User struct {
	ID       int    `json:"id"`
	Username string `json:"username"`
	Password string `json:"password"`
	Email    string `json:"email"`
	Role     string `json:"role"`
	Blocked  bool   `json:"blocked"`
}

type Claims struct {
	Id       string `json:"id"`
	Username string `json:"username"`
	Role     string `json:"role"`
	jwt.StandardClaims
}

type UserInfo struct {
	Username string `json:"username"`
	Role     string `json:"role"`
}
