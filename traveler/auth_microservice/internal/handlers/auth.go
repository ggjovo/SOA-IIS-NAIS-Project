package handlers

import (
	"auth_microservice/internal/services"
	"auth_microservice/invoicer"
	"context"
	"net/http"

	"google.golang.org/protobuf/types/known/emptypb"
)

var authService = services.AuthenticationService{}
var authServiceGRPC = services.AuthenticationServiceGRPC{}

func LoginHandler(w http.ResponseWriter, r *http.Request) {
	authService.LoginHandler(w, r)
}

func HandleCheckToken(w http.ResponseWriter, r *http.Request) {
	authService.HandleCheckToken(w, r)
}

func GetUserInfo(w http.ResponseWriter, r *http.Request) {
	authService.GetUserInfo(w, r)
}

func LoginHandlerGRPC(ctx context.Context, req *invoicer.User) (*invoicer.LoginResponse, error) {
	return authServiceGRPC.LoginGRPC(ctx, req)
}

func LogoutUserGRPC(ctx context.Context, req *emptypb.Empty) (*invoicer.LogoutResponse, error) {
	return authServiceGRPC.LogoutUserGRPC(ctx, req)
}

func CheckTokenGRPC(ctx context.Context, req *emptypb.Empty) (*invoicer.CheckTokenResponse, error) {
	return authServiceGRPC.CheckTokenGRPC(ctx, req)
}

func GetUserInfoGRPC(ctx context.Context, req *emptypb.Empty) (*invoicer.UserInfo, error) {
	return authServiceGRPC.GetUserInfoGRPC(ctx, req)
}
