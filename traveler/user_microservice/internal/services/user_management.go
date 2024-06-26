package services

import (
	"context"
	"database/sql"
	"encoding/json"
	"net/http"

	"user_microservice/internal/models"
	"user_microservice/internal/repositories"
	"user_microservice/internal/utils"
	invoicer "user_microservice/invoicer"

	"golang.org/x/crypto/bcrypt"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/emptypb"
)

type UserService struct {
	UserRepository *repositories.UserRepository
}

func (s *UserServiceGRPC) RegisterUserGRPC(ctx context.Context, req *invoicer.UserRegister) (*invoicer.UserInfo, error) {
	// Provera da li je korisnik već ulogovan
	claims, _ := utils.CheckTokenAndUserInfoGRPC(ctx, token)
	if claims != nil && claims.Username != "" {
		return nil, status.Errorf(codes.Unauthenticated, "Vec ste ulogovani.")
	}

	// Nastavak procesa registracije korisnika
	var user models.User
	user.Username = req.Username
	user.Password = req.Password
	user.Role = req.Role
	user.Email = req.Email

	// Provera da li korisnik već postoji
	existingUser, err := utils.FindByUsernameGRPC(user.Username)
	if err != nil && err != sql.ErrNoRows {
		return nil, status.Error(codes.Internal, err.Error())
	}

	if existingUser != nil {
		// Korisnik već postoji
		return nil, status.Error(codes.InvalidArgument, "Korisničko ime već postoji")
	}

	// Korisnik ne postoji, registrujemo novog
	// AKO ZELIS DA DODAS NOVOG ADMINA, ZAKOMENTARISI OVAJ USLOV PA GA OTKOMENTARISI NAKON OBRADE
	// if user.Role != "tourist" && user.Role != "guide" {
	// 	return nil, status.Error(codes.InvalidArgument, "Uloga može biti samo 'tourist' ili 'guide'")
	// }

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	err = utils.CreateUserGRPC(&user, hashedPassword)
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	return &invoicer.UserInfo{
		Username: user.Username,
		Role:     user.Role,
	}, nil
}

// Implementacija GRPC servisa
func (s *UserServiceGRPC) BlockUserGRPC(ctx context.Context, req *invoicer.BlockUserRequest) (*invoicer.BlockMessage, error) {
	// // Provera da li je korisnik ulogovan kao administrator
	// claims, err := utils.CheckTokenAndUserInfoGRPC(ctx, token)
	// if err != nil {
	// 	return nil, status.Errorf(codes.Unauthenticated, "Niste autentifikovani")
	// }

	// if claims.Role != "admin" {
	// 	return nil, status.Errorf(codes.PermissionDenied, "Samo administratori mogu pristupiti ovoj funkciji")
	// }

	// Provera da li je korisnik koji se blokira admin
	role, err := utils.GetRoleByUsernameGRPC(req.Username)
	print(req.Username)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Greška prilikom dobijanja informacija o korisniku: %v", err)
	}
	if role == "admin" {
		return nil, status.Errorf(codes.InvalidArgument, "Nije dozvoljeno blokirati druge admine")
	}

	// Izvršite SQL upit za blokiranje korisnika
	err = utils.BlockUserRepoGRPC(req.Username)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Greška prilikom blokiranja korisnika: %v", err)
	}

	// Vratite odgovor da je korisnik uspešno blokiran
	return &invoicer.BlockMessage{
		Message: "Uspesna blokada.",
	}, nil
}

func (s *UserServiceGRPC) GetAllUsersGRPC(ctx context.Context, req *emptypb.Empty) (*invoicer.GetAllUsersResponse, error) {
	// // Check if user is logged in as an administrator
	// userInfo, err := utils.CheckTokenAndUserInfoGRPC(ctx, token)
	// if err != nil {
	// 	return nil, status.Error(codes.Unauthenticated, err.Error())
	// }

	// if userInfo.Role != "admin" {
	// 	return nil, status.Error(codes.PermissionDenied, "Only administrators can access this function")
	// }

	// Get all non-admin users from the repository
	users, err := utils.GetNonAdminUsersGRPC()
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	// Create response message
	var response invoicer.GetAllUsersResponse
	for _, user := range users {
		response.Users = append(response.Users, &invoicer.UserInfo{
			Username: user.Username,
			Role:     user.Role,
		})
	}

	return &response, nil
}

func (s *UserService) RegisterUser(w http.ResponseWriter, r *http.Request) {
	// Provjera da li je korisnik već ulogovan
	_, err := utils.CheckTokenAndUserInfo(r)
	if err == nil {
		// Korisnik je već ulogovan, ne dozvoljavamo registraciju
		http.Error(w, "Već ste ulogovani.", http.StatusUnauthorized)
		return
	}

	// Nastavak procesa registracije korisnika
	w.Header().Set("Content-Type", "application/json")
	var user models.User
	_ = json.NewDecoder(r.Body).Decode(&user)

	// Provera da li korisnik već postoji
	existingUser, err := s.UserRepository.FindByUsername(user.Username) // Koristimo s.UserRepository umesto userRepository
	if err != nil && err != sql.ErrNoRows {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if existingUser != nil {
		// Korisnik već postoji
		http.Error(w, "Korisničko ime već postoji", http.StatusBadRequest)
		return
	}

	// Korisnik ne postoji, registrujemo novog
	// AKO ZELIS DA DODAS NOVOG ADMINA, ZAKOMENTARISI OVAJ USLOV PA GA OTKOMENTARISI NAKON OBRADE
	// if user.Role != "tourist" && user.Role != "guide" {
	// 	http.Error(w, "Uloga može biti samo 'tourist' ili 'guide'", http.StatusBadRequest)
	// 	return
	// }

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = s.UserRepository.CreateUser(&user, hashedPassword) // Koristimo s.UserRepository umesto userRepository
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(user)
}

func (s *UserService) BlockUser(w http.ResponseWriter, r *http.Request) {
	// Provera da li je korisnik ulogovan kao administrator
	claims, err := utils.CheckTokenAndUserInfo(r)
	if err != nil {
		return
	}

	if claims.Role != "admin" {
		http.Error(w, "Samo administratori mogu pristupiti ovoj funkciji", http.StatusUnauthorized)
		return
	}

	// Pročitajte korisničko ime korisnika koji se blokira iz URL parametra
	username := r.URL.Query().Get("username")
	if username == "" {
		http.Error(w, "Morate dostaviti korisničko ime korisnika za blokiranje", http.StatusBadRequest)
		return
	}

	// Provera da li je korisnik koji se blokira admin
	err, role := s.UserRepository.GetRoleByUsername(username)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if role == "admin" {
		http.Error(w, "Nije dozvoljeno blokirati druge admine", http.StatusBadRequest)
		return
	}

	// Izvršite SQL upit za blokiranje korisnika
	err = s.UserRepository.BlockUser(username)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Vratite odgovor da je korisnik uspešno blokiran
	response := map[string]interface{}{
		"message": "Korisnik je uspešno blokiran",
	}
	jsonResponse, err := json.Marshal(response)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(jsonResponse)
}

func (s *UserService) GetAllUsers(w http.ResponseWriter, r *http.Request) {
	// Provera da li je korisnik ulogovan kao administrator
	claims, err := utils.CheckTokenAndUserInfo(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	if claims.Role != "admin" {
		http.Error(w, "Samo administratori mogu pristupiti ovoj funkciji", http.StatusUnauthorized)
		return
	}

	// Dohvatanje svih korisnika koji nisu administratori iz repozitorijuma
	users, err := s.UserRepository.GetNonAdminUsers()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Postavljanje Content-Type zaglavlja na application/json
	w.Header().Set("Content-Type", "application/json")

	// Slanje korisnika kao JSON odgovor
	json.NewEncoder(w).Encode(users)
}

func (s *UserService) IsLoggedIn(w http.ResponseWriter, r *http.Request) {
	// Provera da li je token validan
	claims, err := utils.CheckTokenAndUserInfo(r)
	if err != nil {
		// If there's an error, return an appropriate HTTP error response
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	// Extract username and role from claims
	id := claims.Id
	username := claims.Username
	role := claims.Role

	// Create a response struct
	type Response struct {
		Id       string `json:"id"`
		LoggedIn bool   `json:"loggedIn"`
		Username string `json:"username"`
		Role     string `json:"role"`
	}

	// Populate the response struct
	resp := Response{
		Id:       id,
		LoggedIn: true,
		Username: username,
		Role:     role,
	}

	// Encode the response as JSON
	respJSON, err := json.Marshal(resp)
	if err != nil {
		// If there's an error in encoding, return an internal server error
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	// Set the content type header
	w.Header().Set("Content-Type", "application/json")

	// Write the response
	w.Write(respJSON)
}

func (s *UserService) AddToCart(w http.ResponseWriter, r *http.Request) {
	claims, err := utils.CheckTokenAndUserInfo(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	var order models.OrderRequest
	_ = json.NewDecoder(r.Body).Decode(&order)

	var shoppingCart models.ShoppingCart
	shoppingCart.Username = claims.Username
	shoppingCart.ToursId = order.ToursId
	shoppingCart.Quantity = order.Quantity

	existingOrder, _ := s.UserRepository.FindOrderInShoppingCart(claims.Username, order.ToursId)
	if existingOrder != nil {
		http.Error(w, "Already in cart", http.StatusBadRequest)
		return
	}

	err = s.UserRepository.AddToShoppingCart(&shoppingCart)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(shoppingCart)
}

func (s *UserService) RemoveFromCart(w http.ResponseWriter, r *http.Request) {
	claims, err := utils.CheckTokenAndUserInfo(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	var removeOrder models.RemoveOrder
	_ = json.NewDecoder(r.Body).Decode(&removeOrder)

	err = s.UserRepository.RemoveFromShoppingCart(claims.Username, removeOrder.ToursId)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
}

func (s *UserService) ViewCart(w http.ResponseWriter, r *http.Request) {
	claims, err := utils.CheckTokenAndUserInfo(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	shoppingCart, err := s.UserRepository.GetShoppingCart(claims.Username)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(shoppingCart)
}

func (s *UserService) Checkout(w http.ResponseWriter, r *http.Request) {
	claims, err := utils.CheckTokenAndUserInfo(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	err = s.UserRepository.Checkout(claims.Username)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
}

func (s *UserService) GetCheckout(w http.ResponseWriter, r *http.Request) {
	claims, err := utils.CheckTokenAndUserInfo(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	checkout, err := s.UserRepository.GetCheckoutOfUser(claims.Username)
	if err != nil {
		http.Error(w, "No checkout", http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(checkout)
}

func (s *UserService) GetShoppingCartPrice(w http.ResponseWriter, r *http.Request) {
	claims, err := utils.CheckTokenAndUserInfo(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	price, err := s.UserRepository.CalculateTotalPrice(claims.Username)
	if err != nil {
		http.Error(w, "ShoppinCart Empty", http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(price)
}

func (s *UserService) BoughtTours(w http.ResponseWriter, r *http.Request) {
	claims, err := utils.CheckTokenAndUserInfo(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	boughtTours, err := s.UserRepository.GetBoughtTours(claims.Username)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(boughtTours)
}
