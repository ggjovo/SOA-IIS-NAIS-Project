package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/rs/cors"
	"google.golang.org/grpc"

	auth_invoicer "gateway/invoicer/auth" // Importovanje generisanih paketa iz proto definicije za autentifikaciju
	user_invoicer "gateway/invoicer/user" // Importovanje generisanih paketa iz proto definicije za korisnički mikroservis

	"google.golang.org/protobuf/types/known/emptypb"
)

func main() {
	// Inicijalizacija gRPC klijenta za komunikaciju sa postojećim mikroservisima
	userConn, err := grpc.Dial("user-microservice:50052", grpc.WithInsecure())
	if err != nil {
		fmt.Println("Greška prilikom povezivanja sa gRPC serverom za korisnički mikroservis:", err)
		return
	}
	defer userConn.Close()

	authConn, err := grpc.Dial("auth-microservice:50051", grpc.WithInsecure())
	if err != nil {
		fmt.Println("Greška prilikom povezivanja sa gRPC serverom za autentifikaciju:", err)
		return
	}
	defer authConn.Close()

	userClient := user_invoicer.NewUserServiceClient(userConn)
	authClient := auth_invoicer.NewAuthenticationServiceClient(authConn)

	// Definisanje REST API ruta
	router := mux.NewRouter()
	ctx := context.Background()

	router.HandleFunc("/login", func(w http.ResponseWriter, r *http.Request) {
		var user auth_invoicer.User
		if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
			http.Error(w, "Error parsing request", http.StatusBadRequest)
			return
		}
		response, err := authClient.Login(context.Background(), &user)
		if err != nil {
			http.Error(w, "Error invoking gRPC function", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}).Methods("POST")

	router.HandleFunc("/logout", func(w http.ResponseWriter, r *http.Request) {
		ctx := context.Background()

		// Provera validnosti tokena
		tokenResponse, err := authClient.CheckToken(ctx, &emptypb.Empty{})
		if err != nil {
			http.Error(w, "Error invoking gRPC function for token validation", http.StatusInternalServerError)
			return
		}

		// Ako je token validan, pozivamo LogoutUser
		if tokenResponse.Valid {
			_, err := authClient.LogoutUser(ctx, &emptypb.Empty{})
			if err != nil {
				http.Error(w, "Error invoking gRPC function for logout", http.StatusInternalServerError)
				return
			}

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]string{"message": "Successfully logged out"})
		} else {
			// Ako token nije validan, obaveštavamo korisnika da nije bio ulogovan
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]string{"message": "User was not logged in"})
		}
	}).Methods("GET")

	router.HandleFunc("/checktoken", func(w http.ResponseWriter, r *http.Request) {
		response, err := authClient.CheckToken(ctx, &emptypb.Empty{})
		if err != nil {
			http.Error(w, "Error invoking gRPC function for authentication", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}).Methods("GET")

	router.HandleFunc("/getuserinfo", func(w http.ResponseWriter, r *http.Request) {
		response, err := authClient.GetUserInfo(ctx, &emptypb.Empty{})
		if err != nil {
			http.Error(w, "Error invoking gRPC function for authentication", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}).Methods("GET")

	router.HandleFunc("/register", func(w http.ResponseWriter, r *http.Request) {
		tokenResponse, err := authClient.CheckToken(ctx, &emptypb.Empty{})
		if err != nil {
			http.Error(w, "Error invoking gRPC function for token validation", http.StatusInternalServerError)
			return
		}

		if tokenResponse.Valid {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]string{"message": "User is logged in!"})
		} else {
			var userRegister user_invoicer.UserRegister
			if err := json.NewDecoder(r.Body).Decode(&userRegister); err != nil {
				http.Error(w, "Error parsing request", http.StatusBadRequest)
				return
			}

			response, err := userClient.RegisterUser(context.Background(), &userRegister)
			if err != nil {
				http.Error(w, "Error invoking gRPC function", http.StatusInternalServerError)
				return
			}

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(response)
		}
	}).Methods("POST")

	router.HandleFunc("/blockuser", func(w http.ResponseWriter, r *http.Request) {
		tokenResponse, err := authClient.CheckToken(ctx, &emptypb.Empty{})
		if err != nil {
			http.Error(w, "Error invoking gRPC function for token validation", http.StatusInternalServerError)
			return
		}

		if !tokenResponse.Valid {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]string{"message": "User is not logged in!"})
		} else {
			dataResponse, err := authClient.GetUserInfo(ctx, &emptypb.Empty{})
			if err != nil {
				http.Error(w, "Error invoking gRPC function for token validation", http.StatusInternalServerError)
				return
			}
	
			if dataResponse.Role != "admin" {
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(map[string]string{"message": "User is not an admin!"})
			} else {
				var blockRequest user_invoicer.BlockUserRequest
				if err := json.NewDecoder(r.Body).Decode(&blockRequest); err != nil {
					http.Error(w, "Error parsing request", http.StatusBadRequest)
					return
				}
		
				response, err := userClient.BlockUser(ctx, &blockRequest)
				if err != nil {
					http.Error(w, "You can't block an admin!", http.StatusInternalServerError)
					return
				}
		
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(response)
			}
		}		
	}).Methods("POST")

	router.HandleFunc("/getallusers", func(w http.ResponseWriter, r *http.Request) {
		tokenResponse, err := authClient.CheckToken(ctx, &emptypb.Empty{})
		if err != nil {
			http.Error(w, "Error invoking gRPC function for token validation", http.StatusInternalServerError)
			return
		}

		if !tokenResponse.Valid {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]string{"message": "User is not logged in!"})
		} else {
			dataResponse, err := authClient.GetUserInfo(ctx, &emptypb.Empty{})
			if err != nil {
				http.Error(w, "Error invoking gRPC function for token validation", http.StatusInternalServerError)
				return
			}

			if dataResponse.Role != "admin" {
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(map[string]string{"message": "User is not an admin!"})
			} else {
				response, err := userClient.GetAllUsers(ctx, &emptypb.Empty{})
				if err != nil {
					http.Error(w, "Error invoking gRPC function", http.StatusInternalServerError)
					return
				}

				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(response)
			}
		}
	}).Methods("GET")

	// Kreiranje CORS middleware
	c := cors.New(cors.Options{
		AllowedOrigins:   []string{"http://localhost:3000"}, // Promenite na svoje potrebe
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type", "Authorization"},
		AllowCredentials: true,
	})

	// Omotavanje postojećeg rutera sa CORS middleware-om
	handler := c.Handler(router)

	// Pokretanje HTTP servera
	fmt.Println("Pokretanje HTTP servera na portu 8080...")
	http.ListenAndServe(":8080", handler)
}
