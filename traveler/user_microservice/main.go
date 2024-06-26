package main

import (
	"fmt"
	"net/http"
	"user_microservice/db"
	"user_microservice/internal/controllers"

	"context"
	"net"

	invoicer "user_microservice/invoicer" // Importovanje generisanih paketa iz proto definicije

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
	startHTTPServer()
}

func startGRPCServer() {
	// Slušajte na portu 50052
	lis, err := net.Listen("tcp", ":50052")
	if err != nil {
		fmt.Println("Error starting gRPC server:", err)
		return
	}

	// Kreiranje gRPC servera
	s := grpc.NewServer()

	// Kreiranje instance servisa
	userService := &UserServiceGRPC{}

	// Registrujte implementaciju UserServiceServer
	invoicer.RegisterUserServiceServer(s, userService)

	fmt.Println("Starting gRPC server on port 50052...")
	if err := s.Serve(lis); err != nil {
		fmt.Println("Error serving gRPC server:", err)
		return
	}
}

func startHTTPServer() {
	router := mux.NewRouter()
	router.HandleFunc("/register", controllers.RegisterUser).Methods("POST")
	router.HandleFunc("/users", controllers.GetAllUsers).Methods("GET")
	router.HandleFunc("/blockuser", controllers.BlockUser).Methods("POST")
	router.HandleFunc("/login", controllers.LoginUser).Methods("POST")
	router.HandleFunc("/logout", controllers.LogoutUser).Methods("GET")
	router.HandleFunc("/checklogin", controllers.IsLoggedIn).Methods("GET")

	router.HandleFunc("/addtocart", controllers.AddToCart).Methods("POST")
	router.HandleFunc("/removefromcart", controllers.RemoveFromCart).Methods("DELETE")
	router.HandleFunc("/viewcart", controllers.ViewCart).Methods("GET")
	router.HandleFunc("/viewcartprice", controllers.GetShoppingCartPrice).Methods("GET")
	router.HandleFunc("/checkout", controllers.Checkout).Methods("PUT")
	router.HandleFunc("/getcheckout", controllers.GetCheckout).Methods("GET")
	router.HandleFunc("/boughttours", controllers.BoughtTours).Methods("GET")

	// Kreiranje CORS middleware
	c := cors.New(cors.Options{
		AllowedOrigins:   []string{"http://localhost:3000"}, // Dodajte svoj frontend URL ovdje
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type", "Authorization"},
		AllowCredentials: true,
	})

	// Omotavanje postojećeg ruter sa CORS middleware-om
	handler := c.Handler(router)

	// Slušajte na portu 8082
	fmt.Println("Starting HTTP server on port 8082...")
	if err := http.ListenAndServe(":8082", handler); err != nil {
		fmt.Println("Error starting HTTP server:", err)
		return
	}
}

// Implementacija servisa
type UserServiceGRPC struct {
	invoicer.UnimplementedUserServiceServer
}

func (s *UserServiceGRPC) RegisterUser(ctx context.Context, req *invoicer.UserRegister) (*invoicer.UserInfo, error) {
	return controllers.RegisterUserGRPC(ctx, req)
}

func (s *UserServiceGRPC) BlockUser(ctx context.Context, req *invoicer.BlockUserRequest) (*invoicer.BlockMessage, error) {
	return controllers.BlockUserGRPC(ctx, req)
}

func (s *UserServiceGRPC) GetAllUsers(ctx context.Context, req *emptypb.Empty) (*invoicer.GetAllUsersResponse, error) {
	return controllers.GetAllUsersGRPC(ctx, req)
}