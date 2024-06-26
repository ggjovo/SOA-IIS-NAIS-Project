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

type UserInfo struct {
	Id       string `json:"id"`
	Username string `json:"username"`
	Role     string `json:"role"`
}

type Claims struct {
	Id       string `json:"id"`
	Username string `json:"username"`
	Role     string `json:"role"`
	jwt.StandardClaims
}

type UserCredentials struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type OrderRequest struct {
	ToursId       int `json:"tours_id"`
	Quantity 	 	int `json:"quantity"`
}

type ShoppingCart struct {
	Username 		string `json:"username"`
	ToursId       int `json:"tours_id"`
	Quantity 	 	int `json:"quantity"`
}

type RemoveOrder struct {
	ToursId       int `json:"tours_id"`
}

type OrderItem struct {
	ToursId       int `json:"tours_id"`
	Title 		string `json:"title"`
	Price 		int `json:"price"`
	Quantity 	 	int `json:"quantity"`
}

type Checkout struct {
	Username 		string `json:"username"`
	TotalPrice      int `json:"total_price"`
	CheckoutDate 	string `json:"checkout_date"`
}

type Checkpoints struct {
	Name      string `json:"title"`
	Latitude 	string `json:"latitude"`
	Longitude			string `json:"longitude"`
	Position 	string `json:"position"`
}

type Tours struct {
	ToursId 		int `json:"tours_id"`
	Title      string `json:"title"`
	Description 	string `json:"description"`
	Price			int `json:"price"`
	Duration 	string `json:"duration"`
	Difficulty 	string `json:"difficulty"`
	Checkpoints []Checkpoints `json:"checkpoints"`
}