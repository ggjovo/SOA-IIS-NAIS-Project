package main

import (
	"auth_microservice/db"
	"auth_microservice/internal/handlers"

	"context"
	"fmt"
	"net"
	"net/http"

	invoicer "auth_microservice/invoicer" // Importovanje generisanih paketa iz proto definicije

	"github.com/gorilla/mux"
	"github.com/rs/cors"
	"google.golang.org/grpc"
	"google.golang.org/protobuf/types/known/emptypb"
)

func main() {
	err := db.InitDB()
	if err != nil {
		fmt.Println("Error initializing database:", err)
		return
	}

	err = db.InitDBGRPC()
	if err != nil {
		fmt.Println("Error initializing database:", err)
		return
	}

	go startGRPCServer()

	router := mux.NewRouter()
	router.HandleFunc("/checktoken", handlers.HandleCheckToken).Methods("GET")
	router.HandleFunc("/userinfo", handlers.GetUserInfo).Methods("GET")
	router.HandleFunc("/tokenize", handlers.LoginHandler).Methods("POST")

	// Kreiranje CORS middleware
	c := cors.New(cors.Options{
		AllowedOrigins:   []string{"http://localhost:3000"}, // Dodajte svoj frontend URL ovdje
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type", "Authorization"},
		AllowCredentials: true,
	})

	// Omotajte postojeći ruter sa CORS middleware-om
	handler := c.Handler(router)

	// Slušajte na portu 8081
	http.ListenAndServe(":8081", handler)
}

// Implementacija servisa
type AuthenticationService struct {
	invoicer.UnimplementedAuthenticationServiceServer
}

func (s AuthenticationService) Login(ctx context.Context, req *invoicer.User) (*invoicer.LoginResponse, error) {
	return handlers.LoginHandlerGRPC(ctx, req)
}

func (s AuthenticationService) LogoutUser(ctx context.Context, req *emptypb.Empty) (*invoicer.LogoutResponse, error) {
	return handlers.LogoutUserGRPC(ctx, req)
}

func (s AuthenticationService) CheckToken(ctx context.Context, req *emptypb.Empty) (*invoicer.CheckTokenResponse, error) {
	return handlers.CheckTokenGRPC(ctx, req)
}

func (s AuthenticationService) GetUserInfo(ctx context.Context, req *emptypb.Empty) (*invoicer.UserInfo, error) {
	return handlers.GetUserInfoGRPC(ctx, req)
}

func startGRPCServer() {
	// Slušajte na portu 50051
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		fmt.Println("Error starting gRPC server:", err)
		return
	}

	// Kreiranje gRPC servera
	s := grpc.NewServer()

	// Kreiranje instance servisa
	authService := &AuthenticationService{}

	// Registrujte implementaciju AuthenticationServiceServer
	invoicer.RegisterAuthenticationServiceServer(s, authService)

	fmt.Println("Starting gRPC server on port 50051...")
	if err := s.Serve(lis); err != nil {
		fmt.Println("Error serving gRPC server:", err)
		return
	}
}
