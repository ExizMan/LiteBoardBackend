package utils

import (
	"canvas/config"
	"errors"
	"github.com/golang-jwt/jwt/v5"
	"log"
	"os"
)

var jwtSecret = []byte(os.Getenv("JWT_SECRET"))

func ValidateToken(tokenString string) (string, error) {
	secret := []byte(config.Cfg.JWTSecret) // теперь берём при вызове
	log.Printf("SECRET USED IN Go: %s", secret)
	log.Printf("Validating token: %s", tokenString)

	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		log.Println("Token parsing callback invoked")
		return secret, nil
	})

	if err != nil {
		log.Printf("Token parse error: %v", err)
		return "", errors.New("invalid token")
	}

	if !token.Valid {
		log.Println("Token is not valid")
		return "", errors.New("invalid token")
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		log.Println("Token claims type assertion failed")
		return "", errors.New("invalid claims")
	}

	sub, ok := claims["sub"].(string)
	if !ok {
		log.Println("Missing 'sub' claim in token")
		return "", errors.New("missing sub claim")
	}

	log.Printf("Token valid. User ID: %s", sub)
	return sub, nil
}
