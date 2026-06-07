-- CRIAÇÃO DO BANCO
CREATE DATABASE tele_severino;
USE tele_severino;

-- 1. USUÁRIOS
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('CLIENTE', 'ESPECIALISTA') NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. ESPECIALISTAS
CREATE TABLE especialistas (
    id_especialista INT PRIMARY KEY,
    especialidade VARCHAR(50) NOT NULL,
    valor_minuto DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (id_especialista)
        REFERENCES usuarios(id_usuario)
);

-- 3. CATEGORIAS
CREATE TABLE categorias (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nome_categoria VARCHAR(50) UNIQUE NOT NULL
);

-- 4. CONSULTORIAS
CREATE TABLE consultorias (
    id_consultoria INT PRIMARY KEY AUTO_INCREMENT,

    id_cliente INT NOT NULL,
    id_especialista INT NOT NULL,
    id_categoria INT NOT NULL,

    inicio_sessao DATETIME,
    fim_sessao DATETIME,

    valor_total DECIMAL(10,2),

    FOREIGN KEY (id_cliente)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_especialista)
        REFERENCES especialistas(id_especialista),

    FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
);

-- 5. AVALIAÇÕES
CREATE TABLE avaliacoes (
    id_avaliacao INT PRIMARY KEY AUTO_INCREMENT,

    id_consultoria INT NOT NULL,

    nota INT CHECK (nota BETWEEN 1 AND 5),
    comentario TEXT,

    FOREIGN KEY (id_consultoria)
        REFERENCES consultorias(id_consultoria)
);