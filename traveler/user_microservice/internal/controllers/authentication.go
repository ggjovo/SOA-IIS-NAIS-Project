package controllers

import (
	"net/http"
)

func LoginUser(w http.ResponseWriter, r *http.Request) {
	userService.LoginUser(w, r)
}

func LogoutUser(w http.ResponseWriter, r *http.Request) {
	userService.LogoutUser(w, r)
}
