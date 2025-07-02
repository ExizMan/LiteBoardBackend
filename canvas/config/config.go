package config

import (
	"github.com/spf13/viper"
	"log"
)

type CORSConfig struct {
	AllowedOrigins   []string `mapstructure:"allowed_origins"`
	AllowedMethods   []string `mapstructure:"allowed_methods"`
	AllowedHeaders   []string `mapstructure:"allowed_headers"`
	AllowCredentials bool     `mapstructure:"allow_credentials"`
}

type Config struct {
	Port         string     `mapstructure:"port"`
	JWTSecret    string     `mapstructure:"jwt_secret"`
	RedisAddr    string     `mapstructure:"redis_addr"`
	PostgresDSN  string     `mapstructure:"postgres_dsn"`
	SyncInterval string     `mapstructure:"sync_interval"` // например, "1m" или "30s"
	Env          string     `mapstructure:"env"`
	CORS         CORSConfig `mapstructure:"cors"`
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
