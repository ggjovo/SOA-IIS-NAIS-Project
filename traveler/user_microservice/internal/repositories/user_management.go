package repositories

import (
	"user_microservice/internal/models"
	"user_microservice/db"
    "database/sql"
)

type UserRepository struct{}

func (r *UserRepository) FindByUsername(username string) (*models.User, error) {
    var user models.User
    err := db.DB.QueryRow("SELECT id, username, password, email, role FROM users WHERE username = $1", username).Scan(&user.ID, &user.Username, &user.Password, &user.Email, &user.Role)
    switch {
    case err == sql.ErrNoRows:
        return nil, nil
    case err != nil:
        return nil, err
    default:
        return &user, nil
    }
}

func (r *UserRepository) CreateUser(user *models.User, hashedPassword []byte) error {
    _, err := db.DB.Exec("INSERT INTO users (username, password, email, role) VALUES ($1, $2, $3, $4)", user.Username, hashedPassword, user.Email, user.Role)
    return err
}

func (r* UserRepository) BlockUser(username string) error {
	_, err := db.DB.Exec("UPDATE users SET blocked = true WHERE username = $1", username)
	return err
}

func (r *UserRepository) GetRoleByUsername(username string) (error, string) {
	var role string
	err := db.DB.QueryRow("SELECT role FROM users WHERE username = $1", username).Scan(&role)
	return err, role
}

func (r *UserRepository) GetNonAdminUsers() ([]models.User, error) {
    // Izvršavanje SQL upita za dohvatanje korisnika koji nisu administratori
    rows, err := db.DB.Query("SELECT id, username, email, role, blocked FROM users WHERE role != 'admin'")
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

func (r *UserRepository) AddToShoppingCart(order *models.ShoppingCart) error {
    _, err := db.DB.Exec("INSERT INTO shoppingcart (tours_id, quantity, username) VALUES ($1, $2, $3)", order.ToursId, order.Quantity, order.Username)
    return err
}

func (r *UserRepository) FindOrderInShoppingCart(username string, tours_id int) (*models.ShoppingCart, error) {
    var shoppingCart models.ShoppingCart
    err := db.DB.QueryRow("SELECT username, tours_id, quantity FROM shoppingcart WHERE username = $1 and tours_id = $2 and checkout_id = 0", username, tours_id).Scan(&shoppingCart.Username, &shoppingCart.ToursId, &shoppingCart.Quantity)
    switch {
    case err == sql.ErrNoRows:
        return nil, nil
    case err != nil:
        return nil, err
    default:
        return &shoppingCart, nil
    }
}

func (r* UserRepository) RemoveFromShoppingCart(username string, tours_id int) error {
	_, err := db.DB.Exec("DELETE from shoppingcart where username = $1 and tours_id = $2 and checkout_id = 0", username, tours_id)
	return err
}

func (r *UserRepository) GetShoppingCart(username string) ([]models.OrderItem, error) {
    rows, err := db.DB.Query("SELECT tours_id, quantity FROM shoppingcart where username = $1 and checkout_id = 0", username)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var orderItems []models.OrderItem
    for rows.Next() {
        var order models.OrderItem
        if err := rows.Scan(&order.ToursId, &order.Quantity); err != nil {
            return nil, err
        }
        db.DB.QueryRow("SELECT title, price FROM tours WHERE id = $1", order.ToursId).Scan(&order.Title, &order.Price)
        orderItems = append(orderItems, order)
    }

    // Provera za greške koje se mogu desiti tokom iteracije kroz redove
    if err := rows.Err(); err != nil {
        return nil, err
    }

    return orderItems, nil
}

func (r *UserRepository) CalculateTotalPrice(username string) (int, error) {
    rows, err := db.DB.Query("SELECT username, tours_id, quantity FROM shoppingcart where username = $1 and checkout_id = 0", username)
    if err != nil {
        return 0, err
    }
    defer rows.Close()

    var totalAmount = 0
    for rows.Next() {
        var order models.ShoppingCart
        if err := rows.Scan(&order.Username, &order.ToursId, &order.Quantity); err != nil {
            return 0, err
        }
        var price = 0
        db.DB.QueryRow("SELECT cena FROM tourse WHERE id = $1", order.ToursId).Scan(&price)

        totalAmount += price * order.Quantity
    }

    // Provera za greške koje se mogu desiti tokom iteracije kroz redove
    if err := rows.Err(); err != nil {
        return 0, err
    }

    return totalAmount, nil
}

func (r* UserRepository) Checkout(username string) error {
    var total_price, _ = r.CalculateTotalPrice(username)
    var lastID int
    row := db.DB.QueryRow("INSERT INTO checkout (username, total_price) VALUES ($1, $2) RETURNING id", username, total_price)
    row.Scan(&lastID)

	db.DB.Exec("UPDATE shoppingcart SET checkout_id = $1 WHERE username = $2", lastID, username)
	return nil
}

func (r *UserRepository) GetCheckoutOfUser(username string) (*models.Checkout, error) {
    var checkout models.Checkout
    err := db.DB.QueryRow("SELECT username, total_price, checkout_date FROM checkout WHERE username = $1", username).Scan(&checkout.Username, &checkout.TotalPrice, &checkout.CheckoutDate)
    switch {
    case err == sql.ErrNoRows:
        return nil, nil
    case err != nil:
        return nil, err
    default:
        return &checkout, nil
    }
}

func (r *UserRepository) GetBoughtTours(username string) ([]models.Tours, error) {
    rows, _ := db.DB.Query("SELECT tours_id FROM shoppingcart where username = $1 and checkout_id != 0", username)
    defer rows.Close()

    var boughtTours []models.Tours
    for rows.Next() {
        var tours_id = 0
        if err := rows.Scan(&tours_id); err != nil {
            return nil, err
        }
        var tour models.Tours
        db.DB.QueryRow("SELECT id, title, description, price, duration, difficulty FROM tours WHERE id = $1", tours_id).Scan(&tour.ToursId, &tour.Title, &tour.Description, &tour.Price, &tour.Duration, &tour.Difficulty)
        
        checkpoints, _ := db.DB.Query("SELECT name, latitude, longitude, position FROM checkpoints where tour_id = $1", tour.ToursId)
        defer checkpoints.Close()

        for checkpoints.Next(){
            var checkpoint models.Checkpoints
            checkpoints.Scan(&checkpoint.Name, &checkpoint.Latitude, &checkpoint.Longitude, &checkpoint.Position)
            tour.Checkpoints = append(tour.Checkpoints, checkpoint)
        }
        
        boughtTours = append(boughtTours, tour)
    }
    
    return boughtTours, nil
}