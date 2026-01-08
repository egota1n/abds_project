-- Сырые данные из всех источников
CREATE DATABASE IF NOT EXISTS raw;

-- Очищенные и нормализованные данные
CREATE DATABASE IF NOT EXISTS dwh;

-- Агрегированные витрины для аналитики
CREATE DATABASE IF NOT EXISTS mart;