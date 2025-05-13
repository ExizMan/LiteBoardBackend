package config

import (
	"github.com/spf13/viper"
	"log"
)

type Config struct {
	Port      string `mapstructure:"port"`
	JWTSecret string `mapstructure:"jwt_secret"`
}

var Cfg *Config

func LoadConfig() {
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	viper.AddConfigPath("./config")

	viper.AutomaticEnv() // поддержка переменных окружения

	if err := viper.ReadInConfig(); err != nil {
		log.Fatalf("config read error: %v", err)
	}

	Cfg = &Config{}
	if err := viper.Unmarshal(Cfg); err != nil {
		log.Fatalf("config unmarshal error: %v", err)
	}
}
