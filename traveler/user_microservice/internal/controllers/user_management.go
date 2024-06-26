package controllers

import (
	"context"
	"net/http"
	invoicer "user_microservice/invoicer"

	"user_microservice/internal/services"

	"google.golang.org/protobuf/types/known/emptypb"
)

var userService = services.UserService{}
var userServiceGRPC = services.UserServiceGRPC{}

func RegisterUserGRPC(ctx context.Context, req *invoicer.UserRegister) (*invoicer.UserInfo, error) {
	return userServiceGRPC.RegisterUserGRPC(ctx, req)
}

func BlockUserGRPC(ctx context.Context, req *invoicer.BlockUserRequest) (*invoicer.BlockMessage, error) {
	return userServiceGRPC.BlockUserGRPC(ctx, req)
}

func GetAllUsersGRPC(ctx context.Context, req *emptypb.Empty) (*invoicer.GetAllUsersResponse, error) {
	return userServiceGRPC.GetAllUsersGRPC(ctx, req)
}

func RegisterUser(w http.ResponseWriter, r *http.Request) {
	userService.RegisterUser(w, r)
}

func BlockUser(w http.ResponseWriter, r *http.Request) {
	userService.BlockUser(w, r)
}

func GetAllUsers(w http.ResponseWriter, r *http.Request) {
	userService.GetAllUsers(w, r)
}

func IsLoggedIn(w http.ResponseWriter, r *http.Request) {
	userService.IsLoggedIn(w, r)
}

func AddToCart(w http.ResponseWriter, r *http.Request) {
	userService.AddToCart(w, r)
}

func RemoveFromCart(w http.ResponseWriter, r *http.Request) {
	userService.RemoveFromCart(w, r)
}

func ViewCart(w http.ResponseWriter, r *http.Request) {
	userService.ViewCart(w, r)
}

func Checkout(w http.ResponseWriter, r *http.Request) {
	userService.Checkout(w, r)
}

func GetCheckout(w http.ResponseWriter, r *http.Request) {
	userService.GetCheckout(w, r)
}

func GetShoppingCartPrice(w http.ResponseWriter, r *http.Request) {
	userService.GetShoppingCartPrice(w, r)
}

func BoughtTours(w http.ResponseWriter, r *http.Request) {
	userService.BoughtTours(w, r)
}
